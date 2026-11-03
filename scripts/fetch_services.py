#!/usr/bin/env python3
"""한림 AI 교육 포털(ai.hallym.ac.kr/hallym-ai)의 서비스 목록을 assets/services.live.json 에 기록한다.

- 포털 공개 API(/api/v1/hallym-services)에서 이름 · 분류 · 상태 · 한 줄 설명 · 주소 · 아이콘을 읽는다.
- 사이트의 「관심 서비스」 체크 목록(참여·도입 문의)이 이 파일로 만들어지며, 배포 때마다(매일 1회 + 수정 시) 새로 받는다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, sys, os, datetime, urllib.request
PORTAL = 'https://ai.hallym.ac.kr'
API = PORTAL + '/api/v1/hallym-services'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'services.live.json')
UA = {'User-Agent': 'KELI-site services fetcher (+https://keli-aied.org/)', 'Accept': 'application/json'}

def main():
    try:
        with urllib.request.urlopen(urllib.request.Request(API, headers=UA), timeout=40) as r:
            data = json.loads(r.read().decode('utf-8', 'ignore'))
        services = data.get('items', data if isinstance(data, list) else [])
        items, cats = [], {}
        for s in services:
            if not s.get('name'):
                continue
            cat = s.get('category') or {}
            items.append({
                'id': s.get('id'), 'name': s['name'].strip(), 'title': s['name'].strip(), 'category': cat.get('name', '기타'), 'category_order': cat.get('display_order') or 99,
                'status': s.get('status', ''), 'summary': (s.get('summary') or s.get('description') or '').strip(), 'url': (s.get('service_url') or '').strip(),
                'icon': (PORTAL + s['icon']) if str(s.get('icon', '')).startswith('/') else (s.get('icon') or ''), 'home_order': s.get('home_order') or 0,
            })
            cats.setdefault(cat.get('name', '기타'), cat.get('display_order') or 99)
        if not items:
            raise RuntimeError('no services')
        items.sort(key=lambda x: (x['category_order'], 0 if x['status'] == 'live' else 1, x['home_order'], x['name'].lower()))
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        out = {'source': PORTAL + '/hallym-ai', 'api': API, 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '), 'fetched_iso': kst.isoformat(timespec='minutes'),
               'count': len(items), 'live_count': sum(1 for i in items if i['status'] == 'live'), 'coming_count': sum(1 for i in items if i['status'] != 'live'), 'categories': [c for c, _ in sorted(cats.items(), key=lambda kv: kv[1])], 'items': items}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), 'services in', len(cats), 'categories')
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
