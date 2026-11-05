#!/usr/bin/env python3
"""관리자(콘텐츠 스튜디오) 흐름 검사 — GitHub API를 가짜로 대신해 로그인·소식 쓰기·게시·비공개·삭제·아카이브·홈 화면·숨김·게시 기록·배포 실행을 끝까지 돌린다.
사용: python3 gen/qa_admin.py   (저장소 루트에서, Playwright 필요). 화면 캡처는 SHOT 폴더에 남긴다."""
import json, base64, re, os, sys, threading, http.server, socketserver, urllib.parse
from playwright.sync_api import sync_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = 'yoong0520/keli-site'
SHOT = os.environ.get('SHOT') or os.path.join(ROOT, '..', 'qa-shots'); os.makedirs(SHOT, exist_ok=True)
store = {}
for p in ['content/notices.json', 'content/archive.json', 'content/hidden.json', 'content/site.json', 'content/categories.json', 'content/chatbot.json', 'assets/stats.json']:
    store[p] = open(os.path.join(ROOT, p), encoding='utf-8').read()
shas = {p: 'sha0' for p in store}
log = []

def mock(route, request):
    url = request.url; m = request.method
    path = url.split('api.github.com')[1].split('?')[0]
    def ok(body, status=200): route.fulfill(status=status, content_type='application/json', headers={'access-control-allow-origin': '*'}, body=json.dumps(body))
    if path == '/user': return ok({'login': 'yoong0520', 'name': '이유은', 'avatar_url': ''})
    if path == f'/repos/{REPO}': return ok({'permissions': {'push': True}})
    if path.startswith(f'/repos/{REPO}/contents/'):
        fp = urllib.parse.unquote(path[len(f'/repos/{REPO}/contents/'):])
        if m == 'GET':
            if fp not in store: return ok({'message': 'Not Found'}, 404)
            return ok({'sha': shas[fp], 'content': base64.b64encode(store[fp].encode()).decode(), 'size': len(store[fp]), 'download_url': 'x'})
        if m == 'PUT':
            body = json.loads(request.post_data)
            if fp in store and body.get('sha') != shas[fp]: return ok({'message': 'sha mismatch'}, 409)
            raw = base64.b64decode(body['content'])
            store[fp] = raw.decode('utf-8', 'ignore') if fp.endswith('.json') else f'<binary {len(raw)}>'
            shas[fp] = 'sha' + str(len(log) + 1); log.append((fp, body['message']))
            return ok({'content': {'sha': shas[fp]}, 'commit': {'sha': 'c'}})
    if path.startswith(f'/repos/{REPO}/actions/runs'):
        return ok({'workflow_runs': [{'status': 'completed', 'conclusion': 'success', 'created_at': '2026-11-03T05:00:00Z', 'display_title': 'test', 'html_url': 'https://github.com/x'}]})
    if path.startswith(f'/repos/{REPO}/commits'):
        return ok([{'sha': 'abc', 'html_url': 'https://github.com/x', 'author': {'login': 'yoong0520'}, 'commit': {'message': '공지 등록: 테스트', 'author': {'name': '이유은', 'date': '2026-11-03T05:00:00Z'}}}])
    if path.endswith('/dispatches'): log.append(('dispatch', 'pages.yml')); return route.fulfill(status=204, headers={'access-control-allow-origin': '*'}, body='')
    return ok({'message': 'unhandled ' + path}, 500)

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def log_message(self, *a, **k): pass
class Q(socketserver.TCPServer): allow_reuse_address = True
srv = Q(('127.0.0.1', 8781), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
U = 'http://127.0.0.1:8781/admin.html'
with sync_playwright() as p:
    b = p.chromium.launch(); ctx = b.new_context(viewport={'width': 1366, 'height': 900}, locale='ko-KR')
    # 이 검사는 GitHub 토큰 모드용: 사이트 설정의 관리자 서버 주소를 무시한다(서버 모드는 qa_admin_server.py)
    ctx.add_init_script("try{localStorage.removeItem('keli_api')}catch(e){}; Object.defineProperty(window,'KELI_ADMIN',{configurable:true,set:function(v){v.api='';this._ka=v;},get:function(){return this._ka;}});")
    pg = ctx.new_page()
    pg.on('console', lambda msg: errs.append(msg.text) if msg.type == 'error' and 'api.github.com' not in msg.text and 'Failed to load resource' not in msg.text else None)   # 가짜 저장소라 올린 파일(content/files/…)은 실제로 없음 → 404 무시
    pg.on('pageerror', lambda e: errs.append('PAGEERROR ' + str(e)))
    pg.on('dialog', lambda d: d.accept())
    pg.route('https://api.github.com/**', mock)
    pg.goto(U, wait_until='networkidle')
    assert pg.is_visible('#adm-login'), 'login not shown'
    pg.screenshot(path=os.path.join(SHOT, 'adm_login.png'), full_page=True)
    pg.fill('#tok', 'github_pat_test'); pg.click('#tok-go'); pg.wait_for_selector('#adm-app:not([hidden])')
    pg.wait_for_selector('#view .stat'); pg.wait_for_timeout(400)
    assert '대시보드' in pg.inner_text('#view') and pg.inner_text('#u-name') == '이유은'
    pg.screenshot(path=os.path.join(SHOT, 'adm_home.png'), full_page=True)
    # 소식: 목록+편집 2단, 첫 글 자동 선택
    pg.goto(U + '#notices'); pg.wait_for_selector('#editor #nf'); assert pg.locator('.cms-item.on').count() == 1
    pg.screenshot(path=os.path.join(SHOT, 'adm_notices.png'), full_page=True)
    # 새 소식
    pg.goto(U + '#notices/new'); pg.wait_for_selector('#editor #nf')
    pg.fill('#n-title', '관리자 화면 테스트 공지'); pg.select_option('#n-cat', '모집'); pg.fill('#n-summary', '요약 한 줄입니다.')
    pg.click('#ed'); pg.keyboard.type('첫 문단입니다. 두 번째 문장도 있습니다.'); pg.keyboard.press('Enter'); pg.click('[data-ed="h3"]'); pg.keyboard.type('소제목'); pg.keyboard.press('Enter'); pg.click('[data-ed="ul"]'); pg.keyboard.type('목록 하나')
    # 서식 넣기
    pg.click('[data-ed="tpl"]'); pg.wait_for_selector('#modal[data-open="1"] [data-tpl="event"]'); pg.click('[data-tpl="event"]'); pg.wait_for_timeout(300)
    assert 'art-kv' in pg.inner_html('#ed') and '{{' in pg.inner_text('#ed'), 'template inserted'
    pg.click('[data-ed="html"]'); assert pg.is_visible('#ed-src'); src = pg.input_value('#ed-src'); assert '<h3>' in src and '<ul>' in src, src
    pg.fill('#ed-src', src + '<p>HTML 모드에서 덧붙인 문단 <strong>굵게</strong></p>'); pg.click('[data-ed="html"]')
    assert 'HTML 모드에서 덧붙인' in pg.inner_html('#ed')
    pg.set_input_files('#files-in', [{'name': '안내문 2026.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 test'}]); pg.wait_for_selector('.files-box .f')
    pg.set_input_files('#ed-img', [{'name': 'photo.png', 'mimeType': 'image/png', 'buffer': base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==')}]); pg.wait_for_selector('#ed img')
    assert '수정됨' in pg.inner_text('#edit-status')
    pg.check('#n-pin'); pg.click('#n-preview'); pg.wait_for_selector('#modal[data-open="1"] .art'); assert '요약 한 줄' in pg.inner_text('#modal'); pg.screenshot(path=os.path.join(SHOT, 'adm_preview.png')); pg.click('#pv-x')
    pg.screenshot(path=os.path.join(SHOT, 'adm_editor.png'), full_page=True)
    pg.click('#n-save'); pg.wait_for_url(re.compile(r'#notices/n')); pg.wait_for_selector('#editor #nf'); pg.wait_for_timeout(300)
    n = json.loads(store['content/notices.json'])['items']; new = [x for x in n if x['title'] == '관리자 화면 테스트 공지']
    assert new and new[0]['pinned'] and new[0]['cat'] == '모집' and new[0]['summary'] == '요약 한 줄입니다.' and new[0]['published'] is True and new[0]['files'][0]['url'].startswith('content/files/') and '<img src="content/files/' in new[0]['body'], new
    assert re.match(r'\d{4}\.\d{2}\.\d{2}$', new[0]['date']), new[0]['date']
    assert '관리자 화면 테스트 공지' in pg.inner_text('.cms-item.on')
    # 비공개로 저장 → 삭제
    pg.click('#n-draft'); pg.wait_for_timeout(500); assert [x for x in json.loads(store['content/notices.json'])['items'] if x['id'] == new[0]['id']][0]['published'] is False
    pg.wait_for_selector('#n-del'); pg.click('#n-del'); pg.wait_for_selector('#modal[data-open="1"]'); pg.click('#modal [data-x="1"]'); pg.wait_for_timeout(600)
    assert not [x for x in json.loads(store['content/notices.json'])['items'] if x['title'] == '관리자 화면 테스트 공지']
    # 분류 관리: 새 분류 추가 → 저장 → 칩에 나타남
    pg.click('#cats-manage'); pg.wait_for_selector('#modal[data-open="1"] #cat-add'); pg.fill('#cat-new', '연구 소식'); pg.click('#cat-add'); pg.wait_for_timeout(200); pg.click('#cat-ok'); pg.wait_for_timeout(700)
    cj = json.loads(store['content/categories.json']); assert [c for c in cj['notices'] if c['label'] == '연구 소식'], cj
    pg.wait_for_selector('[data-chip]'); assert '연구 소식' in pg.inner_text('.cms-list .chips')
    # 왼쪽 메뉴 하위 항목(분류) → 그 분류로 이동
    pg.wait_for_selector('.cms-nav .sub a[data-sub="연구 소식"]'); pg.click('.cms-nav .sub a[data-sub="연구 소식"]'); pg.wait_for_timeout(500)
    assert pg.locator('.cms-list .chips button.on').text_content().strip() == '연구 소식' and '아직 글이 없습니다' in pg.inner_text('#editor')
    pg.goto(U + '#archive/c/trend'); pg.wait_for_selector('#editor #af'); assert pg.locator('.cms-list .chips button.on').text_content().strip() == '기술 동향·연구'
    pg.goto(U + '#notices'); pg.wait_for_selector('#editor #nf')
    # 목록 검색·분류 칩
    pg.wait_for_selector('[data-search]'); pg.fill('[data-search]', '없는글zzz'); pg.wait_for_timeout(200); assert pg.evaluate("[...document.querySelectorAll('.cms-item')].filter(e=>e.style.display!='none').length") == 0; pg.fill('[data-search]', '')
    # 아카이브 추가(파일 업로드) → 삭제
    pg.goto(U + '#archive/new'); pg.wait_for_selector('#af'); pg.fill('#a-title', '테스트 자료'); pg.select_option('#a-cat', 'trend')
    pg.set_input_files('#a-files-in', [{'name': '보고서.pdf', 'mimeType': 'application/pdf', 'buffer': b'%PDF-1.4 x'}]); pg.wait_for_selector('#a-files .f')
    assert pg.input_value('#a-type') == 'pdf'
    pg.click('#a-save'); pg.wait_for_url(re.compile(r'#archive/a')); pg.wait_for_timeout(400); a = json.loads(store['content/archive.json'])['items']; t = [x for x in a if x['title'] == '테스트 자료']; assert t and t[0]['cat'] == 'trend' and t[0]['files'][0]['url'].startswith('content/files/'), a
    pg.screenshot(path=os.path.join(SHOT, 'adm_archive.png'), full_page=True)
    pg.wait_for_selector('#a-del'); pg.click('#a-del'); pg.click('#modal [data-x="1"]'); pg.wait_for_timeout(600); assert not [x for x in json.loads(store['content/archive.json'])['items'] if x['id'] == t[0]['id']]
    # 홈 화면: 문구 · 배너 · 숫자
    pg.goto(U + '#site'); pg.wait_for_selector('#site-form'); pg.fill('#h-title', '테스트 제목<br>둘째 줄'); pg.check('#b-on'); pg.fill('#b-text', '배너 문구'); pg.fill('#s-univ', '25'); pg.click('#site-save'); pg.wait_for_timeout(700)
    assert json.loads(store['assets/stats.json'])['universities'] == 25 and json.loads(store['content/site.json'])['banner']['on'] is True and json.loads(store['content/site.json'])['hero']['title'] == '테스트 제목<br>둘째 줄'
    pg.screenshot(path=os.path.join(SHOT, 'adm_site.png'), full_page=True)
    # 서비스 숨김 + 보도 + 다시 수집
    pg.goto(U + '#services'); pg.wait_for_selector('.feed-row'); pg.click('button[data-k="services"] >> nth=0'); pg.wait_for_timeout(600); h = json.loads(store['content/hidden.json']); assert len(h['services']) == 1, h
    pg.wait_for_selector('.feed-row.off'); pg.screenshot(path=os.path.join(SHOT, 'adm_services.png'), full_page=True)
    pg.goto(U + '#press'); pg.wait_for_selector('.feed-row'); assert pg.locator('.panel').count() >= 2
    pg.click('#f-dispatch'); pg.wait_for_timeout(300); assert ('dispatch', 'pages.yml') in log
    # 챗봇 설정: 질문 추가 → 저장
    pg.goto(U + '#bot'); pg.wait_for_selector('#bot-form'); pg.click('#faq-add'); pg.wait_for_timeout(200); rows = pg.locator('[data-faq]').count(); pg.fill('[data-faq="' + str(rows - 1) + '"] [data-f="q_ko"]', '주차는 어디에 하나요?'); pg.fill('[data-faq="' + str(rows - 1) + '"] [data-f="a_ko"]', '한림대학교 정문 주차장을 이용해 주세요.'); pg.fill('#b-qko', '질문 하나\n질문 둘')
    pg.click('#bot-save'); pg.wait_for_timeout(700); bj = json.loads(store['content/chatbot.json']); assert bj['enabled'] is True and bj['quick_ko'] == ['질문 하나', '질문 둘'] and [f for f in bj['faq'] if f['q_ko'] == '주차는 어디에 하나요?'], bj
    pg.screenshot(path=os.path.join(SHOT, 'adm_bot.png'), full_page=True)
    # 게시 기록 · 설정
    pg.goto(U + '#history'); pg.wait_for_selector('.hist .h'); assert '공지 등록: 테스트' in pg.inner_text('.hist')
    pg.goto(U + '#settings'); pg.wait_for_selector('#hp-logout'); pg.screenshot(path=os.path.join(SHOT, 'adm_settings.png'), full_page=True); pg.click('#hp-logout'); pg.wait_for_selector('#adm-login:not([hidden])')
    # 모바일 폭
    pg.set_viewport_size({'width': 390, 'height': 800}); pg.fill('#tok', 'github_pat_test'); pg.click('#tok-go'); pg.wait_for_selector('#adm-app:not([hidden])'); pg.goto(U + '#notices'); pg.wait_for_selector('#editor #nf'); pg.wait_for_timeout(300); pg.screenshot(path=os.path.join(SHOT, 'adm_mobile.png'), full_page=True)
    assert pg.evaluate('document.documentElement.scrollWidth<=document.documentElement.clientWidth+1'), 'horizontal scroll'
    b.close()
srv.shutdown()
print('commits:', [l[1] for l in log])
print('console errors:', errs)
assert not errs, errs
print('OK')
