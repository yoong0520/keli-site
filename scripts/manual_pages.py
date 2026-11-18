#!/usr/bin/env python3
"""(일회성·수동 실행) 서비스 매뉴얼 PDF → 페이지 이미지(JPG)·글자(TXT). 체험관 '따라 해 보기' 원고를 만들 때 쓴다.
결과는 _manual_pages/ 에 두고 Actions 아티팩트로 내려받는다(사이트에는 직접 올리지 않음)."""
import json, os, re, subprocess, sys, urllib.request
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, '_manual_pages'); os.makedirs(OUT, exist_ok=True)
mv = json.load(open(os.path.join(ROOT, 'assets', 'manual_videos.json'), encoding='utf-8')).get('items', [])
jobs = []
ONLY = set(filter(None, os.environ.get('KEYS', '').split(',')))
SCALE = os.environ.get('SCALE', '1400')
# PAGES="key:3,5,9;key2:4,8" 이면 그 쪽만(고해상도 화면 잘라내기용) 뽑고, 쪽 안의 그림 위치(pdftohtml -xml)도 함께 남긴다
PAGES = {}
for part in filter(None, os.environ.get('PAGES', '').split(';')):
    k, _, ps = part.partition(':'); PAGES[k.strip()] = [int(x) for x in ps.split(',') if x.strip().isdigit()]
if PAGES: ONLY = set(PAGES)
for it in mv:
    for i, m in enumerate(it.get('manuals') or []):
        k = f"{it['id']}-{i}"
        if not ONLY or k in ONLY: jobs.append((k, m['url'], m.get('label', '')))
idx = []
for key, url, label in jobs:
    d = os.path.join(OUT, key); os.makedirs(d, exist_ok=True); pdf = os.path.join(d, 'm.pdf')
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 KELI-site manual pages'})
        with urllib.request.urlopen(req, timeout=120) as r, open(pdf, 'wb') as f: f.write(r.read())
        if key in PAGES:
            for n in PAGES[key]:
                subprocess.run(['pdftoppm', '-jpeg', '-jpegopt', 'quality=88', '-scale-to', SCALE, '-f', str(n), '-l', str(n), pdf, os.path.join(d, 'p')], check=True, timeout=600)
                subprocess.run(['pdftohtml', '-xml', '-nodrm', '-q', '-f', str(n), '-l', str(n), pdf, os.path.join(d, f'x-{n}')], check=False, timeout=300)
            for x in os.listdir(d):
                if not (x.startswith('p-') or x.endswith('.xml') or x == 'm.pdf'): os.remove(os.path.join(d, x))   # pdftohtml 이 떨군 그림 파일은 버림(위치만 필요)
        else:
            subprocess.run(['pdftoppm', '-jpeg', '-jpegopt', 'quality=82', '-scale-to', SCALE, pdf, os.path.join(d, 'p')], check=True, timeout=600)
            subprocess.run(['pdftotext', '-layout', pdf, os.path.join(d, 'text.txt')], check=True, timeout=120)
        n = len([x for x in os.listdir(d) if x.startswith('p-')])
        os.remove(pdf); idx.append({'key': key, 'url': url, 'label': label, 'pages': n}); print('ok', key, n)
    except Exception as e:
        idx.append({'key': key, 'url': url, 'label': label, 'error': str(e)}); print('fail', key, e, file=sys.stderr)
json.dump(idx, open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
