#!/usr/bin/env python3
"""실증 사례집 표지를 KELI 스타일로 만든다(HTML → 이미지). 관리자가 직접 올린 표지(cover_style 없음)는 건드리지 않는다.
   사용: python3 gen/make_covers.py  → media/archive/<id>-keli.jpg 를 만들고 content/archive.json 의 cover 를 바꾼다."""
import json, os, re, sys, html
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'content', 'archive.json')
PALETTES = [('#0b57a4', '#2997ff'), ('#0e6b55', '#20b2a3'), ('#4b2fbf', '#8f7bff'), ('#b02457', '#ff7aa8'), ('#a14a00', '#ff9d3b'), ('#3b6b10', '#8bd44a')]

TPL = '''<!doctype html><html lang="ko"><head><meta charset="utf-8"><style>
@font-face { font-family: KR; src: local("Noto Sans CJK KR"), local("Noto Sans KR"); }
* { box-sizing: border-box; margin: 0; }
body { background: #fff; }
.cv { position: relative; width: 900px; height: 1200px; overflow: hidden; font-family: KR, "Noto Sans CJK KR", "Noto Sans KR", sans-serif; color: #1d1d1f; background: linear-gradient(180deg, #ffffff 0%, #f3f7fb 100%); }
.blob { position: absolute; right: -360px; bottom: -400px; width: 880px; height: 880px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, {c2} 0%, {c1} 60%, {c1} 100%); opacity: .96; }
.blob2 { position: absolute; left: -180px; top: 520px; width: 420px; height: 420px; border-radius: 50%; background: {c2}; opacity: .10; }
.ring { position: absolute; right: 70px; top: 120px; width: 320px; height: 320px; border-radius: 50%; border: 2px solid {c1}; opacity: .14; }
.top { position: absolute; left: 72px; top: 72px; right: 72px; display: flex; justify-content: space-between; align-items: center; }
.kelilogo { font-weight: 900; font-size: 30px; letter-spacing: .06em; color: {c1}; }
.no { font-size: 20px; font-weight: 600; color: #6e6e73; letter-spacing: .04em; }
.series { position: absolute; left: 72px; top: 200px; font-size: 24px; font-weight: 700; color: {c1}; letter-spacing: .02em; }
.series small { display: block; margin-top: 8px; font-size: 18px; font-weight: 500; color: #6e6e73; letter-spacing: .02em; }
.title { position: absolute; left: 72px; top: 330px; width: 640px; font-size: {fs}px; line-height: 1.22; font-weight: 800; letter-spacing: -.02em; word-break: keep-all; }
.meta { position: absolute; left: 72px; top: {mt}px; font-size: 26px; line-height: 1.5; color: #3a3a3c; }
.meta b { font-weight: 700; color: #1d1d1f; }
.bar { position: absolute; left: 72px; top: {bt}px; width: 120px; height: 8px; border-radius: 4px; background: {c1}; }
.foot { position: absolute; left: 72px; bottom: 72px; max-width: 330px; font-size: 19px; color: #6e6e73; line-height: 1.6; }
.foot b { color: #1d1d1f; }
.wm { position: absolute; right: 64px; bottom: 56px; color: #fff; font-weight: 900; font-size: 44px; letter-spacing: .08em; text-shadow: 0 2px 10px rgba(0,0,0,.18); }
.wm small { display: block; font-size: 16px; font-weight: 600; letter-spacing: .12em; opacity: .9; margin-top: -4px; }
</style></head><body><div class="cv">
<div class="blob2"></div><div class="ring"></div><div class="blob"></div>
<div class="top"><div class="kelilogo">KELI</div><div class="no">{no}</div></div>
<div class="series">{series}<small>{sub}</small></div>
<div class="title">{title}</div>
<div class="meta">{meta}</div>
<div class="bar"></div>
<div class="foot"><b>한림대학교</b> AI교육혁신원 · KELI 사무국<br>고등교육 AI 공유 플랫폼</div>
<div class="wm">KELI<small>HAI ECOSYSTEMS</small></div>
</div></body></html>'''

def esc(s): return html.escape(str(s or ''))

def main():
    d = json.load(open(P, encoding='utf-8'))
    items = [a for a in d['items'] if a.get('cat') == 'case' and (not a.get('cover') or a.get('cover_style') == 'keli' or str(a.get('cover', '')).startswith('media/archive/'))]
    os.makedirs(os.path.join(ROOT, 'media', 'archive'), exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 900, 'height': 1200}, device_scale_factor=2)
        for i, a in enumerate(items):
            c1, c2 = PALETTES[i % len(PALETTES)]
            title = a['title']
            fs = 72 if len(title) <= 9 else 60 if len(title) <= 14 else 50
            lines = 1 if len(title) <= 9 else 2
            mt = 330 + int(fs * 1.22 * lines) + 44
            org = re.sub(r'^한림대학교\s*', '', a.get('org') or '')
            is_report = not org and not a.get('author') in ('', None) and '사례' in title
            series = 'AI 활용 수업 사례집' if not is_report else '실증 사례'
            sub = '2026 · 한림대학교 AI교육혁신원'
            meta = ''
            if a.get('author'): meta += f'<b>{esc(a["author"])}</b> 교수' if not is_report else f'<b>{esc(a["author"])}</b>'
            if org: meta += (' · ' if meta else '') + esc(org)
            no = f'2026 · KELI · {esc(str(a["id"]).lstrip("o")).zfill(3)}'
            h = TPL.replace('{c1}', c1).replace('{c2}', c2).replace('{fs}', str(fs)).replace('{mt}', str(mt)).replace('{bt}', str(mt + 110)).replace('{no}', no).replace('{series}', esc(series)).replace('{sub}', esc(sub)).replace('{title}', esc(title)).replace('{meta}', meta)
            pg.set_content(h); pg.wait_for_timeout(150)
            out = os.path.join(ROOT, 'media', 'archive', f'{a["id"]}-keli.jpg')
            pg.locator('.cv').screenshot(path=out, type='jpeg', quality=88)
            a['cover'] = f'media/archive/{a["id"]}-keli.jpg'; a['cover_style'] = 'keli'
            print('cover', a['id'], title, c1)
        b.close()
    json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()
