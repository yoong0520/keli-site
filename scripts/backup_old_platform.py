#!/usr/bin/env python3
"""구 KELI 플랫폼(keliedu.org/keli) 게시판 전체를 새 플랫폼 저장소에 보관한다(폐쇄 대비 1회 백업, 다시 돌려도 됨).

- 게시판마다 목록을 끝 페이지까지(POST pageIndex) 읽고, 글마다 상세(POST mode=view&articleSeq)를 읽는다.
- 저장: old-keli/<board>/<seq>/view.html(원본 화면) · meta.json(제목·날짜·본문 HTML·첨부·유튜브·그림) · 첨부파일 · 본문 그림
- 결과 목록: old-keli/index.json
"""
import json, re, os, sys, html, time, urllib.request, urllib.parse
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'old-keli')
BASE = 'https://keliedu.org'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36', 'Accept-Language': 'ko'}
BOARDS = [
    ('seminar', '/keli/contents/video/seminar', '한림지식공유세미나 영상'),
    ('partner-video', '/keli/partners/video', '파트너 영상'),
    ('solution-data', '/keli/solution/data', '솔루션 자료실'),
    ('notice', '/keli/board/notice', '공지사항'),
    ('news', '/keli/board/news', '뉴스'),
    ('newsletter', '/keli/board/newsletter', '뉴스레터'),
    ('column-khighedu', '/keli/board/column/K-highedu', '칼럼 · K-고등교육'),
    ('column-humanities', '/keli/board/column/humanities', '칼럼 · 인문'),
    ('edu-ai', '/keli/edu-center/ai', '교육센터 · AI'),
    ('edu-learner', '/keli/edu-center/learner', '교육센터 · 학습자'),
    ('edu-professor', '/keli/edu-center/professor', '교육센터 · 교수자'),
    ('edu-corporate', '/keli/edu-center/corporate', '교육센터 · 기업'),
    ('archive-business', '/keli/contents/archive/business', '아카이브 · 실증 사례집'),
    ('archive-technic', '/keli/contents/archive/technic', '아카이브 · 기술 동향'),
    ('archive-policy', '/keli/contents/archive/policy', '아카이브 · 정책 연구'),
    ('archive-guidebook', '/keli/contents/archive/guidebook', '아카이브 · 간행물'),
]

def get(url, data=None, raw=False):
    h = dict(UA)
    if data is not None:
        h['Content-Type'] = 'application/x-www-form-urlencoded'; data = urllib.parse.urlencode(data).encode()
    for k in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=h), timeout=90) as r:
                b = r.read(); return (b, r.headers) if raw else b.decode('utf-8', 'ignore')
        except Exception as e:
            if k == 2: raise
            time.sleep(2)

def safe(n): return re.sub(r'_+', '_', re.sub(r'[\\/:*?"<>|#%&+\s]+', '_', n)).strip('_')[:120] or 'file'
def txt(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h or ''))).strip()

def listing(path):
    seqs, meta = [], {}
    for p in range(1, 40):
        s = get(BASE + path, {'pageIndex': str(p)}) if p > 1 else get(BASE + path)
        found = list(dict.fromkeys(re.findall(r'data-seq="(\d+)"', s)))
        new = [x for x in found if x not in seqs]
        for m in re.finditer(r'data-seq="(\d+)"(.*?)</a>', s, re.S):
            sq, blk = m.group(1), m.group(2)
            if sq in meta: continue
            th = re.search(r'<img src="([^"]+)"', blk); dt = re.search(r'(\d{4}-\d{2}-\d{2})', blk)
            meta[sq] = {'thumb': html.unescape(th.group(1)) if th else '', 'date': dt.group(1) if dt else ''}
        if not new: break
        seqs += new
    return seqs, meta

def main():
    os.makedirs(OUT, exist_ok=True)
    index = []
    only = set(sys.argv[1:])
    for key, path, label in BOARDS:
        if only and key not in only: continue
        try: seqs, lm = listing(path)
        except Exception as e: print(key, 'list failed', e); continue
        print(key, len(seqs), 'posts', flush=True)
        for sq in seqs:
            d = os.path.join(OUT, key, sq); os.makedirs(d, exist_ok=True)
            try: v = get(BASE + path, {'pageIndex': '1', 'mode': 'view', 'articleSeq': sq})
            except Exception as e: print(' ', sq, 'view failed', e); continue
            open(os.path.join(d, 'view.html'), 'w', encoding='utf-8').write(v)
            m = re.search(r'board-title">\s*(.*?)\s*</div>', v, re.S) or re.search(r'skinTb-sbj">\s*(.*?)\s*</div>', v, re.S); title = txt(m.group(1)) if m else ''
            m = re.search(r'skinTb-date">\s*([\d-]+)', v); date = (m.group(1) if m else lm.get(sq, {}).get('date', ''))
            m = re.search(r'<div class="skinTb-td skinTb-conts">(.*?)</div>\s*</div>\s*(?:<!--|<div class="skinTb-tr">)', v, re.S)
            body = m.group(1) if m else ''
            yts = list(dict.fromkeys(re.findall(r'(?:youtube(?:-nocookie)?\.com/(?:embed/|watch\?v=|shorts/)|youtu\.be/|i\.ytimg\.com/vi/)([\w-]{11})', v)))
            imgs = []
            for u in dict.fromkeys(re.findall(r'<img[^>]+src="(/upload/[^"]+)"', body)):
                fn = safe(os.path.basename(u))
                try:
                    b, _ = get(BASE + u, raw=True); open(os.path.join(d, fn), 'wb').write(b); imgs.append({'src': u, 'file': fn})
                except Exception as e: print('  img fail', u, e)
            files = []
            for u, n in re.findall(r'<a href="(/egf/bp/common/front/\d+/download)">(.*?)</a>', v, re.S):
                n = txt(n); fn = safe(n)
                try:
                    if not os.path.exists(os.path.join(d, fn)):
                        b, _ = get(BASE + u, raw=True); open(os.path.join(d, fn), 'wb').write(b)
                    files.append({'name': n, 'file': fn, 'size': os.path.getsize(os.path.join(d, fn))})
                except Exception as e: print('  file fail', n, e)
            th = lm.get(sq, {}).get('thumb', '')
            if th and th.startswith('/upload/'):
                fn = 'thumb_' + safe(os.path.basename(th))
                try: b, _ = get(BASE + th, raw=True); open(os.path.join(d, fn), 'wb').write(b); th = fn
                except Exception: pass
            meta = {'board': key, 'board_label': label, 'seq': sq, 'title': title, 'date': date, 'body_html': body, 'body_text': txt(body)[:4000],
                    'youtube': yts, 'images': imgs, 'files': files, 'thumb': th, 'source': f'{BASE}{path} (articleSeq {sq})'}
            json.dump(meta, open(os.path.join(d, 'meta.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
            index.append({k: meta[k] for k in ('board', 'board_label', 'seq', 'title', 'date', 'youtube', 'thumb')} | {'files': len(files), 'images': len(imgs)})
            print(f'  {sq} {date} {title[:50]} | yt {len(yts)} files {len(files)} imgs {len(imgs)}', flush=True)
    prev = []
    ip = os.path.join(OUT, 'index.json')
    if only and os.path.exists(ip): prev = [x for x in json.load(open(ip, encoding='utf-8')) if x['board'] not in only]
    json.dump(prev + index, open(ip, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('done', len(index))

if __name__ == '__main__':
    main()
