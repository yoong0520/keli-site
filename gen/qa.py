#!/usr/bin/env python3
"""사이트 점검: 깨진 내부 링크 · 브라우저 콘솔 오류 · 휴대전화 폭(390px) 가로 스크롤.
사용: python3 gen/qa.py            (저장소 루트에서, Playwright 필요)
      python3 gen/qa.py --links    (링크만, 브라우저 없이)"""
import os, re, sys, glob, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pages = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.html')) if not p.endswith('index.artifact.html'))
names = set(pages)

def check_links():
    bad = []
    for f in pages:
        s = open(os.path.join(ROOT, f), encoding='utf-8').read()
        for h in re.findall(r'(?:href|src)="([^"]+)"', s):
            h = html.unescape(h)
            if h.startswith(('http', 'mailto:', 'tel:', '#', 'data:', 'javascript:')):
                continue
            b = h.split('#')[0].split('?')[0]
            if b and b not in names and not os.path.exists(os.path.join(ROOT, b)):
                bad.append((f, h))
    return bad

def check_browser():
    from playwright.sync_api import sync_playwright
    import threading, functools, http.server, socketserver
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
        def log_message(self, *a, **k): pass
    Handler = H
    class Q(socketserver.TCPServer):
        allow_reuse_address = True
    srv = Q(('127.0.0.1', 8899), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    errors, hscroll = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={'width': 1280, 'height': 900})
        pg.on('console', lambda m: errors.append((pg.url.split('/')[-1], m.text[:160])) if m.type == 'error' else None)
        pg.on('pageerror', lambda e: errors.append((pg.url.split('/')[-1], str(e)[:160])))
        m = b.new_page(viewport={'width': 390, 'height': 800})
        for f in pages:
            if f == 'admin.html':
                continue
            pg.goto(f'http://127.0.0.1:8899/{f}', wait_until='load'); pg.wait_for_timeout(150)
            m.goto(f'http://127.0.0.1:8899/{f}', wait_until='load'); m.wait_for_timeout(150)
            if m.evaluate('document.documentElement.scrollWidth > document.documentElement.clientWidth + 1'):
                hscroll.append(f)
        b.close()
    srv.shutdown()
    # 외부 자원 차단(데이터센터 IP의 YouTube 등)은 사이트 오류가 아니므로 제외
    errors = [e for e in errors if 'Failed to load resource' not in e[1] or '127.0.0.1' in e[1]]
    return errors, hscroll

if __name__ == '__main__':
    bad = check_links()
    print('pages', len(pages)); print('broken links', bad[:20])
    if '--links' in sys.argv:
        sys.exit(1 if bad else 0)
    errors, hscroll = check_browser()
    print('console errors', errors[:20]); print('horizontal scroll at 390px', hscroll)
    sys.exit(1 if (bad or errors or hscroll) else 0)
