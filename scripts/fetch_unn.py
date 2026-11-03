#!/usr/bin/env python3
"""한국대학신문(news.unn.net)에서 '한림대 KELI' · '한림대 켈리' 로 검색한 기사를 모아 assets/unn.live.json 에 기록한다.

- 검색 결과(요약형 목록)에서 제목 · 요약(리드) · 날짜 · 기자 · 분류 · 썸네일을 읽는다 (POST /news/articleList.html).
- 검색은 본문까지 찾아 주기 때문에, 제목이나 요약에 KELI 또는 켈리가 들어간 기사만 남긴다(사무국이 숨기기로 추가 조정).
- 기사 본문은 신문사 저작물이므로 가져오지 않는다. 사이트에는 제목 · 요약 · 사진 1장 · 출처(기자명)만 보여 주고 원문으로 연결한다.
- 대표 사진은 기사 페이지의 첫 사진을 media/unn/<idxno>.jpg 로 내려받고, 없으면 목록 썸네일을 쓴다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, re, sys, os, html, datetime, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from media import localize

BASE = 'https://news.unn.net'
LIST = BASE + '/news/articleList.html'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'unn.live.json')
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36', 'Accept-Language': 'ko', 'Referer': BASE + '/'}
TERMS = ['한림대 KELI', '한림대 켈리']
KEEP = re.compile(r'KELI|켈리', re.I)

import time
def _retry(fn, tries=4):
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 + 3 * i)

def post(url, data):
    def go():
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(), headers=dict(UA, **{'Content-Type': 'application/x-www-form-urlencoded'}))
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read().decode('utf-8', 'ignore')
    return _retry(go)

def get(url):
    def go():
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40) as r:
            return r.read().decode('utf-8', 'ignore')
    return _retry(go)

def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def parse_list(h):
    out = []
    for li in re.findall(r'<li class="clearfix">(.*?)</li>', h, flags=re.S):
        m = re.search(r'<h4 class="titles"><a href="/news/articleView\.html\?idxno=(\d+)"[^>]*>(.*?)</a>', li, flags=re.S)
        if not m:
            continue
        lead = re.search(r'<p class="lead[^"]*">(.*?)</p>', li, flags=re.S)
        by = [text(x) for x in re.findall(r'<em>(.*?)</em>', li, flags=re.S)]
        th = re.search(r'<img src="([^"]+)"', li)
        date = ''
        for b in by:
            d = re.match(r'(\d{4})\.(\d{2})\.(\d{2})', b)
            if d:
                date = f'{d.group(1)}.{d.group(2)}.{d.group(3)}'
        out.append({'id': m.group(1), 'title': text(m.group(2)), 'summary': text(lead.group(1)) if lead else '', 'category': by[0] if by else '',
                    'reporter': by[1] if len(by) > 1 else '', 'date': date, 'url': f'{BASE}/news/articleView.html?idxno={m.group(1)}', 'thumb_small': th.group(1) if th else ''})
    return out

def total_of(h):
    m = re.search(r'total=(\d+)', h)
    return int(m.group(1)) if m else 0

def main():
    try:
        seen, items = set(), []
        for term in TERMS:
            page = 1
            while page <= 10:
                h = post(LIST, {'sc_area': 'A', 'view_type': 'sm', 'sc_word': term, 'page': page})
                got = parse_list(h)
                if not got:
                    break
                for it in got:
                    if it['id'] in seen:
                        continue
                    seen.add(it['id'])
                    if KEEP.search(it['title'] + ' ' + it['summary']):
                        it['term'] = term
                        items.append(it)
                if page * 20 >= total_of(h):
                    break
                page += 1
        if not items:
            raise RuntimeError('no articles found')
        for it in items:
            photo = ''
            try:
                a = get(it['url'])
                m = re.search(r'<img[^>]+src="(https://cdn\.news\.unn\.net/news/photo/[^"]+)"', a)
                if m:
                    photo = m.group(1)
                cap = re.search(r'<figcaption[^>]*>(.*?)</figcaption>', a, flags=re.S)
                if cap:
                    it['caption'] = text(cap.group(1))[:200]
            except Exception as e:
                print('article fetch failed', it['url'], e, file=sys.stderr)
            it['photo_remote'] = photo or it['thumb_small']
            it['thumb'] = (localize(it['photo_remote'], 'unn', it['id'], referer=BASE + '/') if it['photo_remote'] else None) or ''
            if not it['thumb'] and it['thumb_small'] and it['thumb_small'] != it['photo_remote']:   # 큰 사진이 안 되면 목록 썸네일
                it['thumb'] = localize(it['thumb_small'], 'unn', it['id'], referer=BASE + '/') or ''
            it['summary'] = (it['summary'][:180] + '…') if len(it['summary']) > 180 else it['summary']
            it['source'] = '한국대학신문'
        items.sort(key=lambda x: x['date'], reverse=True)
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        data = {'source': LIST, 'filter': '검색어 ' + ' · '.join(TERMS) + ' 결과 중 제목이나 요약에 KELI·켈리가 든 기사', 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '),
                'fetched_iso': kst.isoformat(timespec='minutes'), 'count': len(items), 'items': items}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), [(i['date'], i['title'][:40]) for i in items])
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
