#!/usr/bin/env python3
"""관리자 서버 모드 검사 — 워커(가짜 R2 · 가짜 GitHub)를 Node 로 띄우고, 관리자 화면에서
첫 관리자 만들기 → 아이디·비밀번호 로그인 → 큰 파일 조각 올리기 → 공지 게시(서버 대리 커밋) → 사용자 추가 → 로그아웃/재로그인 까지 돌린다.
사용: python3 gen/qa_admin_server.py   (저장소 루트, Node 18+ · Playwright 필요)"""
import os, re, json, time, subprocess, threading, http.server, socketserver, urllib.request
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOT = os.environ.get('SHOT') or os.path.join(ROOT, '..', 'qa-shots'); os.makedirs(SHOT, exist_ok=True)
W = 8787; S = 8790
proc = subprocess.Popen(['node', os.path.join(ROOT, 'worker', 'test_worker.mjs'), 'serve', str(W)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
for _ in range(50):
    try: urllib.request.urlopen(f'http://127.0.0.1:{W}/api/ping', timeout=2); break
    except Exception: time.sleep(0.2)
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a, **k): pass
class Q(socketserver.TCPServer): allow_reuse_address = True
srv = Q(('127.0.0.1', S), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
U = f'http://127.0.0.1:{S}/admin.html'
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1366, 'height': 900}, locale='ko-KR')
        # 서버 주소를 이 브라우저에 넣고, 조각 크기를 작게(1MB) 해서 조각 올리기를 빨리 검사
        ctx.add_init_script("try{localStorage.setItem('keli_api','http://127.0.0.1:%d')}catch(e){}; Object.defineProperty(window,'KELI_ADMIN',{configurable:true,set:function(v){v.part=1048576;v.single=2*1048576;this._ka=v;},get:function(){return this._ka;}});" % W)
        pg = ctx.new_page(); pg.on('dialog', lambda d: d.accept())
        pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
        pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
        pg.goto(U, wait_until='networkidle')
        assert pg.is_visible('#login-pw') and not pg.is_visible('#login-tok'), 'password form expected'
        pg.wait_for_selector('#setup-card:not([hidden])'); pg.screenshot(path=os.path.join(SHOT, 'srv_login.png'), full_page=True)
        # 첫 관리자
        pg.fill('#setup-id', 'keli'); pg.fill('#setup-name', 'KELI 사무국'); pg.fill('#setup-pass', 'password123'); pg.fill('#setup-key', 'setup-123'); pg.click('#setup-go')
        pg.wait_for_selector('#adm-app:not([hidden])'); pg.wait_for_selector('#view .stat'); assert pg.inner_text('#u-name') == 'KELI 사무국'
        # 큰 파일(5MB → 1MB 조각 5개) 첨부 + 공지 게시
        pg.goto(U + '#notices/new'); pg.wait_for_selector('#editor #nf'); pg.fill('#n-title', '서버 모드 테스트')
        pg.set_input_files('#files-in', [{'name': '큰 자료.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 ' + b'x' * (5 * 1048576)}]); pg.wait_for_selector('.files-box .f', timeout=60000)
        assert '큰 자료.pdf' in pg.inner_text('.files-box')
        pg.set_input_files('#files-in', [{'name': '작은 자료.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 small'}]); pg.wait_for_function("document.querySelectorAll('.files-box .f').length==2")
        pg.click('#n-save'); pg.wait_for_url(re.compile(r'#notices/n')); pg.wait_for_timeout(500)
        lst = json.load(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{W}/files/list?prefix=content/', headers={'Authorization': 'Bearer ' + pg.evaluate("localStorage.getItem('keli_admin_session')")})))
        sizes = sorted(f['size'] for f in lst['files']); assert sizes == [14, 5 * 1048576 + 9], sizes
        big = [f for f in lst['files'] if f['size'] > 1000][0]['key']
        r = urllib.request.urlopen(f'http://127.0.0.1:{W}/files/' + urllib.parse.quote(big)); assert r.status == 200 and r.headers['Content-Type'] == 'application/pdf' and len(r.read()) == 5 * 1048576 + 9
        pg.screenshot(path=os.path.join(SHOT, 'srv_notice.png'), full_page=True)
        # 사용자 추가 → 로그아웃 → 직원으로 로그인
        pg.goto(U + '#settings'); pg.wait_for_selector('#user-add'); pg.wait_for_selector('#users-list .hist')
        pg.fill('#ua-id', 'staff1'); pg.fill('#ua-name', '직원 1'); pg.fill('#ua-pass', 'staffpass1'); pg.click('#ua-go'); pg.wait_for_function("document.querySelectorAll('#users-list .h').length==2")
        pg.screenshot(path=os.path.join(SHOT, 'srv_users.png'), full_page=True)
        pg.click('#hp-logout'); pg.wait_for_selector('#adm-login:not([hidden])'); assert not pg.is_visible('#setup-card')
        pg.fill('#login-id', 'staff1'); pg.fill('#login-pass', 'wrong'); pg.click('#tok-go'); pg.wait_for_selector('#tok-msg:not(:empty)'); assert '맞지 않' in pg.inner_text('#tok-msg')
        pg.fill('#login-pass', 'staffpass1'); pg.click('#tok-go'); pg.wait_for_selector('#adm-app:not([hidden])'); pg.wait_for_selector('#view .stat'); assert pg.inner_text('#u-name') == '직원 1'
        pg.goto(U + '#settings'); pg.wait_for_selector('#users-list'); pg.wait_for_timeout(400); assert '관리자만' in pg.inner_text('#users-list')
        b.close()
    print('console errors:', errs); assert not errs, errs; print('OK')
finally:
    srv.shutdown(); proc.terminate()
