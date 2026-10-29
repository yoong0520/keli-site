#!/usr/bin/env python3
"""한림 AI 교육 포털(ai.hallym.ac.kr) 홈의 '한눈에 보는 한림 AI' 숫자를 읽어 assets/stats.live.json에 기록한다.

포털은 이 숫자를 API가 아니라 프런트엔드 번들(/assets/index-*.js)의 상수로 가지고 있으므로
홈 HTML → 번들 경로 → 번들 안의  {label:"AI 강좌 수",value:NNNN}  을 찾는다.
실패하면 기존 파일을 그대로 둔다(배포는 계속 진행).
"""
import json, re, sys, os, datetime, urllib.request

BASE = 'https://ai.hallym.ac.kr'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'stats.live.json')
UA = {'User-Agent': 'KELI-site stats fetcher (+https://yoong0520.github.io/keli-site/)'}

def get(url, limit=5_000_000):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read(limit).decode('utf-8', 'ignore')

def main():
    try:
        home = get(BASE + '/')
        m = re.search(r'src="(/assets/index-[A-Za-z0-9_-]+\.js)"', home)
        if not m:
            raise RuntimeError('bundle path not found in homepage')
        js = get(BASE + m.group(1))
        c = re.search(r'label:"AI 강좌 수",value:(\d+)', js)
        if not c:
            raise RuntimeError('course count not found in bundle')
        courses = int(c.group(1))
        t = re.search(r'label:"AI 강좌 개설 교원 수",value:(\d+)', js)
        s = re.search(r'label:"AI 강좌 수강생 수",value:(\d+)', js)
        kst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
        data = {
            'courses': courses,
            'teachers': int(t.group(1)) if t else None,
            'students': int(s.group(1)) if s else None,
            'fetched_at': kst.strftime('%Y. %m. %d.').replace(' 0', ' '),
            'source': BASE + '/',
            'bundle': m.group(1),
            'note': '포털 홈 "한눈에 보는 한림 AI" 집계값(연도별 AI 강좌 수 합계). 포털 측 공식 API가 생기면 그쪽으로 교체.',
        }
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        json.dump(data, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print('ok', data['courses'], data['fetched_at'])
    except Exception as e:
        print('fetch failed, keeping previous file:', e, file=sys.stderr)
        sys.exit(0)

if __name__ == '__main__':
    main()
