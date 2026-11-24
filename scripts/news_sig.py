#!/usr/bin/env python3
"""소식 게시판 자료(행사·보도자료·언론 보도·영상)의 '내용 지문'을 찍는다. watch-news.yml 이 사이트에 올라간 것과 비교해
달라졌을 때만 다시 배포한다. 조회수·'n일 전'처럼 저절로 바뀌는 값과, 배포 때 사이트가 덧붙이는 값(대표 사진 대체 등)은 뺀다."""
import json, sys, hashlib, re
FIELDS = {
    'events.live.json': ['id', 'title', 'start', 'end', 'place', 'when', 'thumb_remote', 'body_html'],
    'press.live.json': ['id', 'url', 'title', 'date', 'category', 'body_html'],
    'unn.live.json': ['url', 'title', 'date'],
    'videos.live.json': ['id', 'title'],
}
def sig(path, name):
    try:
        d = json.load(open(path, encoding='utf-8'))
    except Exception:
        return ''
    rows = []
    for it in d.get('items', []):
        if it.get('manual') or str(it.get('id', '')).startswith('m'): continue   # 사무국이 직접 올린 글(사이트가 합침)
        vals = [it.get(k) for k in FIELDS[name]]
        vals = [re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', v)).strip() if isinstance(v, str) and '<' in v else v for v in vals]   # 본문은 글자만(그림 주소 차이 무시)
        rows.append(json.dumps(vals, ensure_ascii=False, sort_keys=True))
    return hashlib.sha1('\n'.join(sorted(rows)).encode()).hexdigest() + f' ({len(rows)} items)' if rows else ''
if __name__ == '__main__':
    print(sig(sys.argv[1], sys.argv[2]))
