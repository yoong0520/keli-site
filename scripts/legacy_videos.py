#!/usr/bin/env python3
"""old-keli/ 의 세미나·파트너 영상 → content/videos_extra.json (썸네일은 media/youtube/ 에 내려받음)."""
import json, os, re, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
G = {'seminar': 'seminar', 'partner-video': 'partner'}
items = []
for b, g in G.items():
    d = os.path.join(ROOT, 'old-keli', b)
    if not os.path.isdir(d): continue
    for sq in os.listdir(d):
        mp = os.path.join(d, sq, 'meta.json')
        if not os.path.exists(mp): continue
        m = json.load(open(mp, encoding='utf-8'))
        for y in (m.get('youtube') or [])[:1]:
            th = f'media/youtube/{y}.jpg'
            if not os.path.exists(os.path.join(ROOT, th)):
                try:
                    os.makedirs(os.path.join(ROOT, 'media', 'youtube'), exist_ok=True)
                    b2 = urllib.request.urlopen(urllib.request.Request(f'https://i.ytimg.com/vi/{y}/hqdefault.jpg', headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read()
                    open(os.path.join(ROOT, th), 'wb').write(b2)
                except Exception as e:
                    print('thumb fail', y, e); th = f'https://i.ytimg.com/vi/{y}/hqdefault.jpg'
            items.append({'id': y, 'title': m['title'], 'date': (m.get('date') or '').replace('-', '.'), 'group': g,
                          'url': f'https://www.youtube.com/watch?v={y}', 'embed': f'https://www.youtube-nocookie.com/embed/{y}?autoplay=1&rel=0',
                          'thumb': th, 'source': m.get('source', '')})
json.dump({'note': '구 KELI 플랫폼(keliedu.org)에서 옮겨 온 영상. scripts/legacy_videos.py 로 다시 만들 수 있음', 'items': items},
          open(os.path.join(ROOT, 'content', 'videos_extra.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(items), 'videos')
