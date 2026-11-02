#!/usr/bin/env python3
"""한림 AI 교육 포털(ai.hallym.ac.kr/hallym-ai)의 서비스별 데모 영상을 모아 assets/demos.live.json 에 기록한다.

- 포털 공개 API(/api/v1/hallym-services)의 각 서비스 resources 중 kind == 'video' 를 가져온다
  (포털 「한림 AI」 화면의 [영상] 버튼과 같은 자료).
- Google Drive 영상은 /preview 로, YouTube 는 youtube-nocookie 로 사이트 안에서 바로 재생되게 주소를 만든다.
- 썸네일(Drive thumbnail · YouTube hqdefault)은 media/demos/ 에 내려받는다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, re, sys, os, datetime, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from media import localize

PORTAL = 'https://ai.hallym.ac.kr'
PAGE = PORTAL + '/hallym-ai'
API = PORTAL + '/api/v1/hallym-services'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'demos.live.json')
UA = {'User-Agent': 'KELI-site demo fetcher (+https://yoong0520.github.io/keli-site/)', 'Accept': 'application/json'}
AUD = {'common': '', 'student': '학생용', 'faculty': '교수자용'}

def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))

def embed_of(url):
    """원본 주소 → (재생 주소, 썸네일 주소, 종류)"""
    u = url.strip()
    m = re.search(r'drive\.google\.com/file/d/([A-Za-z0-9_-]+)', u)
    if m:
        fid = m.group(1)
        return f'https://drive.google.com/file/d/{fid}/preview', f'https://drive.google.com/thumbnail?id={fid}&sz=w1280', 'drive'
    m = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})', u)
    if m:
        vid = m.group(1)
        return f'https://www.youtube-nocookie.com/embed/{vid}?rel=0', f'https://i.ytimg.com/vi/{vid}/hqdefault.jpg', 'youtube'
    m = re.search(r'youtube\.com/playlist\?list=([A-Za-z0-9_-]+)', u)
    if m:
        return f'https://www.youtube-nocookie.com/embed/videoseries?list={m.group(1)}', '', 'playlist'
    return u, '', 'link'

def main():
    try:
        data = get_json(API)
        services = data.get('items', data if isinstance(data, list) else [])
        items = []
        for s in sorted(services, key=lambda x: ((x.get('category') or {}).get('display_order') or 99, x.get('home_order') or 0, x.get('id') or 0)):
            vids = [r for r in (s.get('resources') or []) if r.get('kind') == 'video' and r.get('url')]
            for r in sorted(vids, key=lambda r: r.get('display_order') or 0):
                emb, thumb, kind = embed_of(r['url'])
                key = f"{s['id']}-{r.get('id', 0)}"
                it = {
                    'id': key, 'service_id': s['id'], 'name': s.get('name', ''), 'summary': (s.get('summary') or s.get('description') or '').strip(),
                    'category': (s.get('category') or {}).get('name', ''), 'status': s.get('status', ''),
                    'audience': AUD.get(r.get('audience', 'common'), ''), 'url': r['url'].strip(), 'embed': emb, 'kind': kind,
                    'icon': (PORTAL + s['icon']) if s.get('icon', '').startswith('/') else (s.get('icon') or ''),
                    'service_url': (s.get('service_url') or '').strip(),
                }
                it['thumb'] = (localize(thumb, 'demos', key) if thumb else None) or ''
                items.append(it)
        if not items:
            raise RuntimeError('no demo videos found')
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        out = {'source': PAGE, 'api': API, 'filter': '포털 서비스 자료 중 영상(kind=video)', 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '),
               'fetched_iso': kst.isoformat(timespec='minutes'), 'count': len(items), 'services': len({i['service_id'] for i in items}), 'items': items}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), 'videos /', out['services'], 'services; thumbs', sum(1 for i in items if i['thumb']))
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
