#!/usr/bin/env python3
"""한림대학교 홍보 보도자료(www.hallym.ac.kr/pr/5865/subview.do)에서 제목에 KELI 또는 켈리가 들어간 글을 모아
assets/press.live.json 에 기록한다. KELI 사이트의 '뉴스레터 › 보도자료'는 이 파일만 보고 그린다.

- 게시판 검색(findType=sj 제목, findWord=KELI / 켈리)을 페이지 끝까지 읽어 합치고 중복을 제거한다.
- 글마다 상세 페이지를 열어 작성일·분류·본문(허용 태그만)·이미지·첨부를 보탠다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, re, sys, os, html, datetime, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_events import clean_html, text
from media import localize

BASE = 'https://www.hallym.ac.kr'
BOARD = '/bbs/pr/876'
PUBLIC = BASE + '/pr/5865/subview.do'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'press.live.json')
UA = {'User-Agent': 'KELI-site press fetcher (+https://yoong0520.github.io/keli-site/)'}
KEYWORDS = ['KELI', '켈리']

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'ignore')

def search_url(word, page):
    q = urllib.parse.urlencode({'findType': 'sj', 'findWord': word, 'page': page})
    return f'{BASE}{BOARD}/artclList.do?{q}'

def parse_list(h):
    rows = []
    for href, aid, body in re.findall(r'<a href="(' + BOARD + r'/(\d+)/artclView\.do)"(.*?)</li>', h, flags=re.S):
        t = re.search(r'<strong>\s*(.*?)\s*</strong>', body, flags=re.S)
        title = text(re.sub(r'<span class="new">.*?</span>', '', t.group(1))) if t else ''
        summ = re.search(r'<div class="artcl-content">\s*<p>(.*?)</p>', body, flags=re.S)
        date = re.search(r'(\d{4}\.\d{2}\.\d{2})', body)
        rows.append({'id': int(aid), 'title': title, 'url': BASE + href, 'date': date.group(1) if date else '',
                     'summary': text(summ.group(1)) if summ else ''})
    tot = re.search(r'class="_totPage">(\d+)<', h)
    return rows, int(tot.group(1)) if tot else 1

def parse_detail(h, it):
    i = h.find('class="view viewCont"')
    s = h[i:] if i > 0 else h
    tt = re.search(r'<div class="title">\s*<strong>\s*(.*?)\s*</strong>', s, flags=re.S)
    if tt:
        it['title'] = text(tt.group(1))                                           # 목록의 잘린 제목 대신 전체 제목
    m = re.search(r'작성일\s*:\s*</span>\s*([\d.]+)', s)
    if m:
        it['date'] = m.group(1).strip().rstrip('.')
    c = re.search(r'<li class="cl">\s*<span class="hidden">분류</span>\s*\[?([^<\]]+)\]?', s)
    if c:
        it['category'] = c.group(1).strip()
    j = s.find('class="txt"')
    ends = [s.find(m, j) for m in ('class="prev-list"', 'class="next-list"', 'class="btns"', 'class="board-list"', 'class="bbs-anchor"')]
    ends = [e for e in ends if e > j]
    k = min(ends) if ends else -1
    if j > 0:
        body = s[j:k if k > 0 else j + 200000]
        body = body[body.find('>') + 1:]
        body = re.sub(r'<p[^>]*>(?:\s|<span[^>]*>\s*</span>|<br\s*/?>|&nbsp;)*</p>', '', body)   # 빈 문단 제거
        bh = clean_html(body, BASE)
        bh = re.sub(r'<p>(?:\s|&nbsp;|<br>)*</p>', '', bh)                       # 빈 문단
        bh = re.sub(r'<p>(?:\s|&nbsp;)+', '<p>', bh)                               # 문단 앞 공백
        bh = re.sub(r'<img src="([^"]+)"', lambda m: '<img src="' + urllib.parse.quote(m.group(1), safe=':/%?=&') + '"', bh)
        norm = lambda x: re.sub(r'[^0-9A-Za-z가-힣]', '', html.unescape(x))
        first = re.match(r'\s*<p>(.*?)</p>', bh, flags=re.S)
        if first and norm(text(first.group(1))) and norm(text(first.group(1))) == norm(it['title']):
            bh = bh[first.end():].lstrip()                                         # 제목을 반복한 첫 문단 제거
        n = [0]
        def loc(m):
            n[0] += 1
            rel = localize(m.group(1), 'press', f'{it["id"]}-{n[0]}', referer=it['url'])
            return f'<img src="{rel or m.group(1)}"'
        bh = re.sub(r'<img src="([^"]+)"', loc, bh)
        it['body_html'] = bh
        imgs = re.findall(r'<img src="([^"]+)"', bh)
        if imgs:
            it['thumb'] = imgs[0]
        if not it.get('summary'):
            t = text(bh)
            it['summary'] = (t[:160] + '…') if len(t) > 160 else t
    files = []
    a = s.find('class="attachment"'); b = s.find('class="aditIem"', a)
    for fm in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', s[a:b] if a > 0 and b > a else '', flags=re.S):
        href = fm.group(1)
        if 'download' in href or 'atchmnfl' in href:
            name = text(fm.group(2))
            if name and not any(f['url'].endswith(href) for f in files):
                files.append({'name': name, 'url': (BASE + href) if href.startswith('/') else href})
    it['files'] = files[:6]
    return it

def main():
    try:
        seen, items = set(), []
        for w in KEYWORDS:
            page, total = 1, 1
            while page <= total and page <= 20:
                rows, total = parse_list(get(search_url(w, page)))
                if not rows:
                    break
                for r in rows:
                    if r['id'] not in seen and re.search(r'KELI|켈리', r['title'], flags=re.I):
                        seen.add(r['id']); items.append(r)
                page += 1
        if not items:
            raise RuntimeError('no KELI press releases found')
        for it in items:
            try:
                parse_detail(get(it['url']), it)
            except Exception as e:
                print('detail failed', it['url'], e, file=sys.stderr)
        items.sort(key=lambda x: (x.get('date') or '', x['id']), reverse=True)
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        data = {'source': PUBLIC, 'filter': '제목에 KELI 또는 켈리가 들어간 보도자료', 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '),
                'fetched_iso': kst.isoformat(timespec='minutes'), 'count': len(items), 'items': items}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), [i['date'] + ' ' + i['title'][:30] for i in items])
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
