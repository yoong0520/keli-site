#!/usr/bin/env python3
"""한림대학교 유튜브 채널(@HALLYMNEWS)에서 KELI 관련 영상을 모아 assets/videos.live.json 에 기록한다.

- 채널 안 검색(https://www.youtube.com/@HALLYMNEWS/search?query=…)으로 제목·설명에 키워드가 든 영상을 찾는다.
  (동영상·실시간·Shorts 탭을 모두 포함하는 YouTube 자체 검색 결과)
- 1순위 키워드(KELI · 켈리) → group 'keli', 2순위(HAI Ecosystems · 에듀테크 소프트랩) → group 'related'
- 채널 RSS(최신 15건)로 정확한 게시일을 보강한다. 썸네일은 media/youtube/에 내려받는다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, re, sys, os, html, datetime, urllib.request, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from media import localize

HANDLE = 'HALLYMNEWS'
CHANNEL_ID = 'UCZp7unmkcLM4zn9Bom_Pl-A'
CHANNEL_URL = f'https://www.youtube.com/@{HANDLE}'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'videos.live.json')
UA = {'User-Agent': 'Mozilla/5.0 (KELI-site video fetcher; +https://yoong0520.github.io/keli-site/)', 'Accept-Language': 'ko'}
GROUPS = [('keli', ['KELI', '켈리']), ('related', ['HAI', '에듀테크 소프트랩'])]
RELATED_OK = re.compile(r'HAI[- ]|HAI Ecosystem|에코시스템|소프트랩', re.I)   # related 그룹은 제목이 이 패턴에 맞을 때만
RELATED_NO = re.compile(r'수시|정시|모집|입학|장학', re.I)                          # 입시 홍보물은 제외

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.read().decode('utf-8', 'ignore')

def search(q):
    h = get(f'{CHANNEL_URL}/search?query={urllib.parse.quote(q)}')
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', h, flags=re.S)
    if not m:
        return []
    d = json.loads(m.group(1))
    out = []
    def walk(o):
        if isinstance(o, dict):
            if 'videoRenderer' in o:
                v = o['videoRenderer']
                title = ''.join(r.get('text', '') for r in v.get('title', {}).get('runs', []))
                desc = ''.join(r.get('text', '') for s in v.get('detailedMetadataSnippets', []) for r in s.get('snippetText', {}).get('runs', []))
                out.append({
                    'id': v.get('videoId'), 'title': html.unescape(title).strip(),
                    'published_text': v.get('publishedTimeText', {}).get('simpleText', ''),
                    'length': v.get('lengthText', {}).get('simpleText', ''),
                    'views': v.get('viewCountText', {}).get('simpleText', '') or v.get('shortViewCountText', {}).get('simpleText', ''),
                    'desc': desc[:200],
                })
            for x in o.values(): walk(x)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(d)
    return out

def age_days(t):
    """'8일 전' · '11개월 전' · '2년 전' · '스트리밍 시간: 8일 전' → 대략의 일수"""
    m = re.search(r'(\d+)\s*(분|시간|일|주|개월|년)', t or '')
    if not m:
        return 99999
    n, u = int(m.group(1)), m.group(2)
    return n * {'분': 0, '시간': 0, '일': 1, '주': 7, '개월': 30, '년': 365}[u]

def rss_dates():
    try:
        x = get(f'https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}')
        return dict(re.findall(r'<yt:videoId>([^<]+)</yt:videoId>.*?<published>([^<]+)</published>', x, flags=re.S))
    except Exception:
        return {}

def main():
    try:
        items, seen = [], set()
        for group, words in GROUPS:
            for w in words:
                for v in search(w):
                    if not v['id'] or v['id'] in seen:
                        continue
                    blob = v['title'] + ' ' + v['desc']
                    if group == 'keli' and not re.search(r'KELI|켈리', blob, re.I):
                        continue
                    if group == 'related' and (not RELATED_OK.search(v['title']) or RELATED_NO.search(v['title'])):
                        continue
                    seen.add(v['id']); v['group'] = group; items.append(v)
        if not items:
            raise RuntimeError('no videos found')
        dates = rss_dates()
        for v in items:
            v['url'] = f'https://www.youtube.com/watch?v={v["id"]}'
            v['embed'] = f'https://www.youtube-nocookie.com/embed/{v["id"]}?autoplay=1&rel=0'
            v['is_live_recording'] = '스트리밍' in (v.get('published_text') or '')
            v['published_text'] = re.sub(r'^스트리밍 시간:\s*', '', v.get('published_text') or '')
            if v['id'] in dates:
                v['published'] = dates[v['id']][:10].replace('-', '.')
            v['age_days'] = age_days(v['published_text'])
            v['thumb'] = localize(f'https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg', 'youtube', v['id']) or f'https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg'
            v.pop('desc', None)
        items.sort(key=lambda v: (0 if v['group'] == 'keli' else 1, v['age_days']))
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        data = {'source': CHANNEL_URL, 'filter': '채널 내 검색: 제목·설명에 KELI 또는 켈리 (관련: HAI Ecosystems · 에듀테크 소프트랩)',
                'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '), 'fetched_iso': kst.isoformat(timespec='minutes'),
                'count': len(items), 'items': items}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), [(v['group'], v['title'][:30]) for v in items])
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
