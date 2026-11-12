#!/usr/bin/env python3
"""old-keli 교육센터 글(edu-*)은 화면 구조가 달라 제목·본문을 view.html 에서 다시 뽑는다."""
import json, os, re, html, glob
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def txt(h): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', h or ''))).strip()
for mp in glob.glob(os.path.join(ROOT, 'old-keli', 'edu-*', '*', 'meta.json')):
    d = os.path.dirname(mp); v = open(os.path.join(d, 'view.html'), encoding='utf-8').read(); m = json.load(open(mp, encoding='utf-8'))
    t = re.search(r'<div class="content-title">\s*<h3>(.*?)</h3>', v, re.S)
    if not t: continue
    m['title'] = txt(t.group(1))
    dt = re.search(r'<div class="content-title">.*?<span>[^<]*</span>\s*<span>([\d.]+)</span>', v, re.S)
    if dt: m['date'] = dt.group(1).replace('.', '-')
    course = re.search(r'<div class="course">\s*(<ul>.*?</ul>)', v, re.S)
    box = re.search(r'<div class="content-box">(.*?)</div>\s*(?:<div class="(?:file|attach|btn)|</div>)', v, re.S)
    info = ''
    if course:
        info = '<dl class="art-kv">' + ''.join(f'<dt>{txt(a)}</dt><dd>{txt(b)}</dd>' for a, b in re.findall(r'<strong>(.*?)</strong>\s*<span>(.*?)</span>', course.group(1), re.S)) + '</dl>'
    m['body_html'] = info + (box.group(1) if box else '')
    m['body_text'] = txt(m['body_html'])[:4000]
    # 첨부 그림(포스터)은 본문 그림으로
    for f in list(m.get('files') or []):
        if re.search(r'\.(jpe?g|png|gif)$', f['file'], re.I):
            m.setdefault('images', []).append({'src': '__poster__' + f['file'], 'file': f['file']})
            m['body_html'] = f'<figure class="art-fig"><img src="__poster__{f["file"]}" alt="{html.escape(m["title"])}"></figure>' + m['body_html']
            m['files'].remove(f)
    json.dump(m, open(mp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(m['board'], m['seq'], m['date'], m['title'][:50])
ip = os.path.join(ROOT, 'old-keli', 'index.json'); idx = json.load(open(ip, encoding='utf-8'))
for x in idx:
    mp = os.path.join(ROOT, 'old-keli', x['board'], x['seq'], 'meta.json')
    if os.path.exists(mp):
        m = json.load(open(mp, encoding='utf-8')); x['title'] = m['title']; x['date'] = m['date']
json.dump(idx, open(ip, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
