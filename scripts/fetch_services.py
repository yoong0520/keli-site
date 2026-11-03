#!/usr/bin/env python3
"""한림 AI 교육 포털(ai.hallym.ac.kr/hallym-ai)의 서비스 목록을 assets/services.live.json 에 기록한다.

- 포털 공개 API(/api/v1/hallym-services)에서 이름 · 분류 · 상태 · 한 줄 설명 · 자세한 설명 · 대상 · 주소 · 아이콘 · 영상 · 매뉴얼을 읽는다.
- Marketplace(services.html)의 서비스 카드 · 서비스 상세 페이지 · 홈 서비스 · 「관심 서비스」 체크 목록 · 홈 숫자가 이 파일로 만들어지며,
  배포 때마다(매일 1회 + 수정 시) 새로 받는다. 포털에 서비스가 추가·변경되면 다음 배포에서 사이트에 반영된다.
- 서비스 그림(포털의 icon 필드: 실제로는 서비스 화면 캡처)은 media/services/ 에 JPEG로 내려받아 사이트 안에서 직접 보여 준다(핫링크·CSP 영향 없음).
- HAI 활용 매뉴얼(haimanual.csedu4all.com)의 「수업의 순간마다」 6단계 배치도 함께 읽어 manual_stages 에 넣는다.
- 실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, sys, os, re, hashlib, datetime, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from media import localize

PORTAL = 'https://ai.hallym.ac.kr'
API = PORTAL + '/api/v1/hallym-services'
MANUAL = 'https://haimanual.csedu4all.com'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'services.live.json')
UA = {'User-Agent': 'KELI-site services fetcher (+https://keli-aied.org/)', 'Accept': 'application/json, text/html'}
STAGE_KEYS = ['design', 'content', 'class', 'practice', 'assess', 'analysis']   # 매뉴얼 01~06 순서


def get(url, timeout=40):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read().decode('utf-8', 'ignore')


def absolute(u):
    u = (u or '').strip()
    if not u:
        return ''
    return PORTAL + u if u.startswith('/') else u


def manual_stages():
    """매뉴얼 data.js 의 steps.items[].services → {서비스명: [stage key, ...]}. 실패하면 None"""
    try:
        html = get(MANUAL + '/')
        m = re.search(r'src="([^"]*data\.js[^"]*)"', html)
        if not m:
            return None
        js = get(MANUAL + '/' + m.group(1).lstrip('/'))
        i = js.find('"steps"')
        j = re.compile(r'"services"\s*:\s*\{').search(js, i + 10)   # steps 다음의 최상위 services 객체 앞까지
        block = js[i:j.start()] if i >= 0 and j else ''
        out = {}
        for k, chunk in enumerate(re.findall(r'"services"\s*:\s*\[(.*?)\]', block, flags=re.S)):
            for name in re.findall(r'"([^"]+)"', chunk):
                out.setdefault(name.strip(), []).append(STAGE_KEYS[k] if k < len(STAGE_KEYS) else f's{k+1}')
        return out or None
    except Exception as e:
        print('manual stages failed:', e, file=sys.stderr)
        return None


def main():
    try:
        data = json.loads(get(API))
        services = data.get('items', data if isinstance(data, list) else [])
        items, cats = [], {}
        for s in services:
            if not s.get('name'):
                continue
            cat = s.get('category') or {}
            res = sorted(s.get('resources') or [], key=lambda r: r.get('display_order') or 0)
            videos = [absolute(r.get('url')) for r in res if r.get('kind') == 'video' and r.get('url')]
            manuals = [absolute(r.get('url')) for r in res if r.get('kind') == 'manual' and r.get('url')]
            icon_remote = absolute(s.get('icon'))
            icon_local = localize(icon_remote, 'services', f'shot-{s.get("id")}-{hashlib.md5(icon_remote.encode()).hexdigest()[:8]}', referer=PORTAL + '/', max_px=1200) if icon_remote else None   # 포털이 그림을 바꾸면 주소가 바뀌어 새 파일로 받는다
            items.append({
                'id': s.get('id'), 'name': s['name'].strip(), 'title': s['name'].strip(),
                'category': cat.get('name', '기타'), 'category_order': cat.get('display_order') or 99,
                'status': s.get('status', ''), 'launch_date': s.get('launch_date'),
                'summary': (s.get('summary') or s.get('description') or '').strip(),
                'description': (s.get('description') or s.get('summary') or '').strip(),
                'target_roles': [t.strip() for t in str(s.get('target_roles') or '').split(',') if t.strip()],
                'url': (s.get('service_url') or '').strip(),
                'icon': icon_local or icon_remote, 'icon_remote': icon_remote,
                'video': videos[0] if videos else '', 'videos': videos, 'manual': manuals[0] if manuals else '', 'manuals': manuals,
                'home_order': s.get('home_order') or 0,
            })
            cats.setdefault(cat.get('name', '기타'), cat.get('display_order') or 99)
        if not items:
            raise RuntimeError('no services')
        items.sort(key=lambda x: (x['category_order'], 0 if x['status'] == 'live' else 1, x['home_order'], x['name'].lower()))
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        prev = {}
        try:
            prev = json.load(open(OUT, encoding='utf-8'))
        except Exception:
            pass
        stages = manual_stages() or prev.get('manual_stages') or {}
        out = {'source': PORTAL + '/hallym-ai', 'api': API, 'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '), 'fetched_iso': kst.isoformat(timespec='minutes'),
               'count': len(items), 'live_count': sum(1 for i in items if i['status'] == 'live'), 'coming_count': sum(1 for i in items if i['status'] != 'live'),
               'categories': [c for c, _ in sorted(cats.items(), key=lambda kv: kv[1])], 'items': items,
               'manual_source': MANUAL, 'manual_stages': stages}
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', len(items), 'services in', len(cats), 'categories;', len(stages), 'manual stage entries')
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)


if __name__ == '__main__':
    main()
