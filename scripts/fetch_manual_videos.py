#!/usr/bin/env python3
"""HAI 활용 매뉴얼 사이트(haimanual.csedu4all.com)의 서비스별 '영상 보기' 목록 → assets/manual_videos.json
- 매뉴얼 사이트 js/data.js(window.HAI_DATA)를 node 로 읽는다. 영상이 없는 서비스는 넣지 않는다(매뉴얼 사이트처럼 버튼을 숨김).
- 실패하면 기존 파일을 그대로 둔다.
"""
import json, os, re, sys, subprocess, urllib.request, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'manual_videos.json')
SITE = 'https://haimanual.csedu4all.com/'
UA = {'User-Agent': 'KELI-site manual video fetcher (+https://keli-aied.org/)'}
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40) as r: return r.read().decode('utf-8', 'ignore')
def main():
    try:
        page = get(SITE)
        m = re.search(r'src="(js/data\.js[^"]*)"', page); js = get(SITE + (m.group(1) if m else 'js/data.js'))
        code = 'global.window={};' + js + ';process.stdout.write(JSON.stringify(window.HAI_DATA))'
        d = json.loads(subprocess.run(['node', '-e', code], capture_output=True, text=True, check=True, timeout=60).stdout)
        items = []
        for s in (d.get('services') or {}).get('items') or []:
            vids = []
            for v in s.get('videos') or []:
                u = v.get('url') or ''; emb = v.get('embed') or ''
                y = re.search(r'(?:watch\?v=|youtu\.be/)([\w-]{11})', u); pl = re.search(r'list=([\w-]+)', u)
                if not emb:
                    emb = f'https://www.youtube-nocookie.com/embed/{y.group(1)}?autoplay=1&rel=0' if y else (f'https://www.youtube-nocookie.com/embed/videoseries?list={pl.group(1)}' if pl else u)
                vids.append({'label': v.get('label') or '영상', 'type': v.get('type') or '', 'url': u, 'embed': emb})
            if vids:
                items.append({'id': s.get('id'), 'name': s.get('name'), 'portalName': s.get('portalName') or '', 'videos': vids})
        if not items: raise RuntimeError('no videos')
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        json.dump({'source': SITE, 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '), 'items': items}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('ok', len(items), 'services with videos')
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
if __name__ == '__main__': main()
