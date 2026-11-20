#!/usr/bin/env python3
"""영어판 페이지 만들기 — gen/gen2.py 가 만든 한국어 페이지(*.html)마다 영어판 en-<페이지>.html 을 만든다.

- 페이지의 한국어 문구(본문 글자, 안내 글, 버튼, 체험 화면 속 글자, 화면 스크립트 속 글자)를 모아 번역한다.
- 검수한 번역은 content/i18n/en_base.json, 자동 번역은 content/i18n/en.json(Actions 캐시)에 쌓아 두고 다시 쓴다.
  새 문구만 KELI 관리자 서버(Cloudflare 워커)의 /api/translate 로 자동 번역한다(배포 작업의 OIDC 토큰으로 인증).
  번역하지 못한 문구는 한국어 그대로 둔다(배포는 멈추지 않는다).
- 영어판 안의 링크는 영어판끼리 이어지고, ENG 단추는 KOR(같은 페이지의 한국어판)로 바뀐다.
- 사람이 고친 번역은 content/i18n/en_fix.json 에 { "한국어": "English" } 로 넣으면 그것이 먼저 쓰인다.
"""
import glob, json, os, re, sys, time, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'content', 'i18n', 'en.json')
FIX = os.path.join(ROOT, 'content', 'i18n', 'en_fix.json')
HAN = re.compile('[가-힣]')
SKIP = {'admin.html', 'en.html'}
NO_ATTR = {'href', 'src', 'srcset', 'class', 'id', 'style', 'name', 'type', 'for', 'rel', 'target', 'action', 'method', 'download', 'data-vmodal', 'data-embed', 'data-copy', 'data-walk', 'data-try', 'data-trial', 'data-menu', 'data-go', 'data-show', 'data-hide', 'data-show-now', 'data-wait', 'data-echo', 'data-note', 'data-log', 'data-req', 'data-check', 'data-allon', 'data-clear', 'data-step', 'width', 'height', 'loading', 'value'}
MODEL = os.environ.get('EN_MODEL', 'openai/gpt-4.1-mini')
GLOSSARY = """Glossary (always use these English forms):
한림대학교/한림대 = Hallym University; ○○대학교 = ○○ University; KELI 사무국 = KELI Secretariat; KELI 협의체 = KELI Consortium; AI교육혁신원 = Institute for AI Education Innovation; AI교육확산센터 = Center for AI Education Advancement;
이음이 = Ieum-i; 이루미 = Iru-mi (the two KELI mascots); HAI 체험관 = HAI Experience Center; 바로 체험 = Try it now; 직접 해 보기 = Try it yourself; AI 미니 체험 = AI mini demo; 실제 서비스 체험 = Real service trial; 추후 공개 = Coming soon;
데모 신청 = Request a demo; 도입 문의 = Contact us; 전체 데모 영상 = All demo videos; 매뉴얼 = manual; 아카이브 = Archive; 소식 = News; 공지사항 = Notices; 행사 = Events; 뉴스레터 · 보도자료 = Newsletter & press;
AI 학습 지원 = AI Learning Support; AI 교수 지원 = AI Teaching Support; AI 연구 지원 = AI Research Support; AI 진로·취업 = AI Career & Jobs; AI 플랫폼 = AI Platforms; AI 의료교육 = AI Medical Education; AI 행정 지원 = AI Administration; AI 운영 지원 = AI Operations;
글로컬대학30 = Glocal University 30; 교육부 = Ministry of Education; 미션 = mission; 힌트 = hint. Keep product names (HAI-Tutor, HAI-GPT, LXP, KELI, Marketplace …) as they are."""


def norm(t):
    return re.sub(r'\s+', ' ', t.replace('⁠', '')).strip()


# ---------------------------------------------------------------- 문구 찾기 · 바꾸기 (collect 와 apply 를 같은 길로)
def walk_html(h, fn):
    """HTML 조각 h 에서 한국어 문구를 fn(문구)->새 문구 로 바꾼다. script 는 walk_js, style 은 그대로."""
    out, pos = [], 0
    for m in re.finditer(r'(<script\b[^>]*>)(.*?)(</script>)|<style\b.*?</style>|<!--.*?-->', h, flags=re.S | re.I):
        out.append(_html_part(h[pos:m.start()], fn))
        if m.group(1) is not None:
            js = m.group(2)
            out.append(m.group(1) + (js if 'application/ld+json' in m.group(1) else walk_js(js, fn)) + m.group(3))
        else:
            out.append(m.group(0))
        pos = m.end()
    out.append(_html_part(h[pos:], fn))
    return ''.join(out)


def _attr(m, fn):
    name, q, val = m.group(1), m.group(2), m.group(3)
    if name.lower() in NO_ATTR or not HAN.search(val):
        return m.group(0)
    if name == 'data-set' and '|' in val:
        sel, _, txt = val.partition('|')
        return f' {name}={q}{sel}|{_esc_attr(fn(txt), q)}{q}'
    return f' {name}={q}{_esc_attr(fn(val), q)}{q}'


def _esc_attr(t, q):
    return t.replace(q, '&quot;' if q == '"' else '&#39;')


def _text(m, fn):
    t = m.group(1)
    if not HAN.search(t):
        return m.group(0)
    lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', t, flags=re.S).groups()
    return '>' + lead + fn(core) + trail + '<'


def _html_part(h, fn):
    h = re.sub(r'\s([\w:-]+)=(["\'])(.*?)\2', lambda m: _attr(m, fn), h, flags=re.S)
    return re.sub(r'>([^<>]+)<', lambda m: _text(m, fn), h)


def walk_js(code, fn):
    """JS 코드 안의 문자열 글자 가운데 한국어가 든 것만 바꾼다(주석·정규식은 건드리지 않음)."""
    out, i, n, last_sig = [], 0, len(code), ''
    while i < n:
        c = code[i]
        if c in '\'"`':
            j = i + 1
            while j < n and code[j] != c:
                j += 2 if code[j] == '\\' else 1
            raw = code[i + 1:j]
            out.append(c + (_js_str(raw, c, fn) if HAN.search(raw) and c != '`' else raw) + c)
            i = j + 1; last_sig = 'x'; continue
        if c == '/' and i + 1 < n and code[i + 1] == '/':
            j = code.find('\n', i); j = n if j < 0 else j
            out.append(code[i:j]); i = j; continue
        if c == '/' and i + 1 < n and code[i + 1] == '*':
            j = code.find('*/', i + 2); j = n if j < 0 else j + 2
            out.append(code[i:j]); i = j; continue
        if c == '/' and (last_sig in '' or last_sig in '(,=:[!&|?{};+-*%<>~^'):
            j, cls = i + 1, False
            while j < n and (code[j] != '/' or cls) and code[j] != '\n':
                if code[j] == '\\': j += 1
                elif code[j] == '[': cls = True
                elif code[j] == ']': cls = False
                j += 1
            out.append(code[i:j + 1]); i = j + 1; last_sig = 'x'; continue
        out.append(c)
        if not c.isspace():
            last_sig = c if c in '(,=:[!&|?{};+-*%<>~^' else 'x'
        i += 1
    return ''.join(out)


def _js_str(raw, q, fn):
    try:
        val = json.loads('"' + raw.replace("\\'", "'") + '"') if q == '"' else json.loads('"' + raw.replace('"', '\\"').replace("\\'", "'") + '"')
    except Exception:
        return raw
    new = walk_html(val, fn) if re.search(r'<[a-z/][^>]*>', val) else _plain(val, fn)
    if new == val:
        return raw
    enc = json.dumps(new, ensure_ascii=False)[1:-1].replace('</', '<\\/')
    if q == "'":
        enc = enc.replace('\\"', '"').replace("'", "\\'")
    return enc


def _plain(val, fn):
    if not HAN.search(val):
        return val
    if re.fullmatch(r'[a-z0-9_-]+\.html(#.*)?', val):
        return val
    lead, core, trail = re.match(r'^(\s*)(.*?)(\s*)$', val, flags=re.S).groups()
    return lead + fn(core) + trail


# ---------------------------------------------------------------- 번역(GitHub Models)
FAILS = [0]   # 번역 서버가 계속 실패하면 멈추고, 번역 못 한 글자는 한국어로 둔 채 배포를 이어 간다

def site_api():
    try:
        return (json.load(open(os.path.join(ROOT, 'content', 'site.json'), encoding='utf-8')).get('admin') or {}).get('api', '')
    except Exception:
        return ''


def oidc_token():
    """GitHub Actions 가 서명한 신분증(OIDC). 워커가 이것으로 '우리 저장소의 배포 작업'인지 확인한다."""
    u, t = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL'), os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')
    if not (u and t): return None
    req = urllib.request.Request(u + '&audience=keli-translate', headers={'Authorization': 'Bearer ' + t})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())['value']


def translate_batch(items, url):
    """KELI 관리자 서버(Cloudflare 워커)의 /api/translate 로 보낸다. 실패하면 None(한국어 그대로 둠)."""
    if FAILS[0] >= 3:
        return None
    for attempt in range(3):
        try:
            tok = oidc_token()
            if not tok: FAILS[0] = 99; return None
            req = urllib.request.Request(url, data=json.dumps({'items': items}, ensure_ascii=False).encode('utf-8'),
                                         headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json', 'Origin': 'https://keli-aied.org', 'User-Agent': 'KELI-build'})
            with urllib.request.urlopen(req, timeout=180) as r:
                arr = json.loads(r.read().decode('utf-8', 'replace')).get('items')
            if isinstance(arr, list) and len(arr) == len(items):
                FAILS[0] = 0
                out = [x if (x and not HAN.search(x.replace('한국어', ''))) else '' for x in map(str, arr)]
                # 검색 목록처럼 소문자로 바꾼 원문은 번역도 소문자로
                return [(y.lower() if (y and k == k.lower() and re.search('[a-z]', k)) else y) for k, y in zip(items, out)]
            print('  bad response length', file=sys.stderr); return None
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')[:200]
            print('  http', e.code, body, file=sys.stderr)
            if e.code in (401, 403, 404, 405, 503):   # 워커가 아직 옛 코드이거나 AI 가 없음 → 이번 배포에서는 그만
                FAILS[0] = 99; return None
            FAILS[0] += 1
            if FAILS[0] >= 3: return None
            time.sleep(5 * (attempt + 1))
        except Exception as e:
            print('  error', e, file=sys.stderr); FAILS[0] += 1; time.sleep(5)
    return None


def fill(missing, cache, token, budget):
    missing = sorted(missing, key=len)
    batch, size, sent = [], 0, 0
    def flush():
        nonlocal batch, size, sent
        if not batch: return
        if sent >= budget or FAILS[0] >= 3: batch, size = [], 0; return
        res = translate_batch(batch, token); sent += 1
        if res is None and len(batch) > 1:   # 한꺼번에 실패하면 반씩 나눠 다시
            half = len(batch) // 2; a, b = batch[:half], batch[half:]
            for part in (a, b):
                r2 = translate_batch(part, token); sent += 1
                if r2: cache.update({k: v for k, v in zip(part, r2) if v})
        elif res:
            cache.update({k: v for k, v in zip(batch, res) if v})
        batch, size = [], 0
        json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
        print(f'  translated {len(cache)} total', flush=True)
    for k in missing:
        if size + len(k) > 2000 or len(batch) >= 25:
            flush()
        batch.append(k); size += len(k)
    flush()



# ---------------------------------------------------------------- 날마다 바뀌는 숫자·날짜 문구(포털 집계 등)는 틀로 번역
DOW = {'월': 'Mon', '화': 'Tue', '수': 'Wed', '목': 'Thu', '금': 'Fri', '토': 'Sat', '일': 'Sun'}
def _d(m):  # 2026. 11. 19. -> 2026.11.19
    return f'{m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}'
PATTERNS = [
    (r'(\d+)개 서비스', lambda m: f'{m.group(1)} services'),
    (r'(\d+)개 서비스 · 영상 (\d+)건\.', lambda m: f'{m.group(1)} services · {m.group(2)} videos.'),
    (r'기준 (\d+)개 서비스 · 영상 (\d+)건\.', lambda m: f'— {m.group(1)} services · {m.group(2)} videos.'),
    (r'수업 설계부터 평가·분석까지, (\d+)개 서비스\.', lambda m: f'From class design to assessment and analytics: {m.group(1)} services.'),
    (r'운영 중 (\d+) · 오픈 예정 (\d+) · 포털 (\d{4})\. (\d+)\. (\d+)\. 기준', lambda m: f'{m.group(1)} live · {m.group(2)} coming soon · portal as of {m.group(3)}.{int(m.group(4)):02d}.{int(m.group(5)):02d}'),
    (r'(.*?)에 등록된 정보를 자동으로 가져옵니다 \((\d{4})\. (\d+)\. (\d+)\. 기준\)\.', lambda m: (m.group(1) + ' ' if m.group(1) else ' ') + f'is the source; its registered information is pulled automatically (as of {m.group(2)}.{int(m.group(3)):02d}.{int(m.group(4)):02d}).'),
    (r'(\d{4})\. (\d+)\. (\d+)\. 기준', lambda m: f'As of {m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}'),
    (r'(\d{4}\.\d{2}\.\d{2})\(([월화수목금토일])\)(.*)', lambda m: f'{m.group(1)} ({DOW[m.group(2)]}){m.group(3)}' if not re.search('[가-힣]', m.group(3)) else None),
]
PATTERNS += [
    (r'(\d[\d,]*)개', lambda m: m.group(1)),
    (r'(\d[\d,]*)건', lambda m: f'{m.group(1)} items'),
    (r'기준 (\d+)개\)\.', lambda m: f'— {m.group(1)} in total).'),
    (r'기준 (\d+)건\.', lambda m: f'— {m.group(1)} items.'),
    (r'서비스 (\d+)', lambda m: f'Services {m.group(1)}'),
    (r'조회수 ([\d,]+)회', lambda m: f'{m.group(1)} views'),
    (r'(\d+)개월 전', lambda m: f'{m.group(1)} month{"s" if m.group(1) != "1" else ""} ago'),
    (r'(\d+)년 전', lambda m: f'{m.group(1)} year{"s" if m.group(1) != "1" else ""} ago'),
    (r'(\d+)주 전', lambda m: f'{m.group(1)} week{"s" if m.group(1) != "1" else ""} ago'),
    (r'(\d+)일 전', lambda m: f'{m.group(1)} day{"s" if m.group(1) != "1" else ""} ago'),
    (r'목록은 한림 AI 교육 포털\(ai\.hallym\.ac\.kr/hallym-ai\)에서 매일 자동으로 가져옵니다 · (\d{4})\. (\d+)\. (\d+)\. 기준\.', lambda m: f'The list is pulled automatically every day from the Hallym AI Education Portal (ai.hallym.ac.kr/hallym-ai) · as of {m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}.'),
    (r'한림대학교 보도자료\(hallym\.ac\.kr › 홍보 › 보도자료\) 중 제목에 KELI 또는 켈리가 들어간 글 (\d+)건과, 한국대학신문\(news\.unn\.net\)에서 「한림대 KELI」·「한림대 켈리」로 검색한 기사 (\d+)건을 자동으로 가져옵니다\.', lambda m: f'Pulled automatically: {m.group(1)} Hallym University press releases (hallym.ac.kr › PR › Press releases) with KELI in the title, and {m.group(2)} Korea University News (news.unn.net) articles found by searching "Hallym KELI."'),
]
def pattern(k, look=None):
    for rx, f in PATTERNS:
        m = re.fullmatch(rx, k)
        if m:
            r = f(m)
            if r: return r
    w = re.sub(r'\(([월화수목금토일])\)', lambda m: f' ({DOW[m.group(1)]})', k)   # 날짜 뒤 요일
    if w != k and not HAN.search(w): return w
    m = re.fullmatch(r'(.+?)\(시범 운영 서비스\) (데모 영상|영상 보기)', k)
    if m and not HAN.search(m.group(1)):
        return f'{m.group(1)} (pilot service) ' + ('demo video' if m.group(2) == '데모 영상' else 'watch video')
    if look:
        m = re.fullmatch(r'(.+?) \| KELI (플랫폼|아카이브) · 한림대학교', k)
        if m:
            y = look(m.group(1)) or pattern(m.group(1), look)
            if y and not HAN.search(y): return f'{y} | KELI {"Platform" if m.group(2) == "플랫폼" else "Archive"} · Hallym University'
        m = re.fullmatch(r'(.+?) 대표 사진', k)
        if m:
            y = look(m.group(1)) or pattern(m.group(1), look)
            if y and not HAN.search(y): return f'{y} — main photo'
    if look and ' · ' in k:   # "행사 · 날짜" 처럼 가운뎃점으로 이은 문구는 조각마다 번역
        parts = []
        for x in k.split(' · '):
            y = x if not HAN.search(x) else (look(x) or pattern(x, look))
            if not y or HAN.search(y): return None
            parts.append(y)
        return ' · '.join(parts)
    return None

# ---------------------------------------------------------------- 영어판 쓰기
def main():
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
    BASE = os.path.join(ROOT, 'content', 'i18n', 'en_base.json')   # 사무국이 검수해 저장소에 넣어 둔 번역
    if os.path.exists(BASE):
        cache.update(json.load(open(BASE, encoding='utf-8')))   # 검수한 번역이 자동 번역 캐시보다 먼저
    fix = json.load(open(FIX, encoding='utf-8')) if os.path.exists(FIX) else {}
    pages = [os.path.basename(f) for f in sorted(glob.glob(os.path.join(ROOT, '*.html'))) if not os.path.basename(f).startswith('en') and os.path.basename(f) not in SKIP]
    site_js = open(os.path.join(ROOT, 'assets', 'site.js'), encoding='utf-8').read()
    need = set()
    def collect(t):
        k = norm(t)
        if k and HAN.search(k): need.add(k)
        return t
    for p in pages:
        walk_html(open(os.path.join(ROOT, p), encoding='utf-8').read(), collect)
    walk_js(site_js, collect)
    missing = [k for k in need if k not in cache and k not in fix and not pattern(k, lambda x: fix.get(x) or cache.get(x))]
    for k in sorted(missing)[:80]: print('    new:', k[:160], flush=True)
    print(f'pages {len(pages)} · strings {len(need)} · cached {len(need) - len(missing)} · new {len(missing)}', flush=True)
    url = os.environ.get('TRANSLATE_URL') or ((site_api().rstrip('/') + '/api/translate') if site_api() else '')
    if missing and url and os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL'):   # GitHub Actions 배포 때만 자동 번역
        print(f'  auto-translate {len(missing)} new strings via {url}', flush=True)
        fill(missing, cache, url, int(os.environ.get('EN_BUDGET', '60')))
        if FAILS[0] >= 3: print('  auto-translate stopped (worker not ready?) — untranslated strings stay Korean', flush=True)
    elif missing:
        print('  (local build) untranslated strings stay Korean', flush=True)
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)

    def tr(t):
        k = norm(t)
        return fix.get(k) or cache.get(k) or pattern(k, lambda x: fix.get(x) or cache.get(x)) or t
    ko = set(pages) | {'index.html'}
    def link(m):
        pg, rest = m.group(2), m.group(3) or ''
        if pg == 'index.html': return f'{m.group(1)}en.html{rest}'
        if pg in ko: return f'{m.group(1)}en-{pg}{rest}'
        return m.group(0)
    open(os.path.join(ROOT, 'assets', 'site.en.js'), 'w', encoding='utf-8').write(walk_js(site_js, tr))
    left, skipped = 0, []
    for p in pages:
        h = open(os.path.join(ROOT, p), encoding='utf-8').read()
        e = walk_html(h, tr)
        e = re.sub(r'(href=")([a-z0-9_-]+\.html)((?:#[^"]*)?")', link, e)   # 영어판끼리 잇기(먼저)
        e = re.sub(r'<a class="txt( lang)?"[^>]*data-lang-switch>ENG</a>', lambda m: f'<a class="txt{m.group(1) or ""}" href="{p}" lang="ko" aria-label="한국어">KOR</a>', e)
        e = re.sub(r'<a href="en[^"]*" data-lang-switch>English</a>', f'<a href="{p}" lang="ko">한국어</a>', e)
        e = e.replace('<a href="en.html">English</a>', f'<a href="{p}" lang="ko">한국어</a>')
        e = re.sub(r'("page":\s*")([a-z0-9_-]+\.html)(")', link, e)
        e = re.sub(r'<html lang="ko"', '<html lang="en"', e, count=1)
        e = e.replace('assets/site.js?', 'assets/site.en.js?').replace('class="kchat" id="kchat" data-lang="ko"', 'class="kchat" id="kchat" data-lang="en"')
        e = re.sub(r'<link rel="canonical" href="([^"]*?)' + re.escape(p) + '">', lambda m: f'<link rel="canonical" href="{m.group(1)}en-{p}">', e)
        rest = set(norm(t) for t in re.findall(r'>([^<>]*[가-힣][^<>]*)<', re.sub(r'<script.*?</script>', '', e, flags=re.S)))
        allk = set(norm(t) for t in re.findall(r'>([^<>]*[가-힣][^<>]*)<', re.sub(r'<script.*?</script>', '', h, flags=re.S)))
        ep = os.path.join(ROOT, 'en-' + p)
        if allk and len(rest) / len(allk) > 0.15:   # 아직 번역이 덜 된 페이지: 영어판을 내지 않는다
            if os.path.exists(ep): os.remove(ep)
            kh = h.replace(f'href="en-{p}" data-lang-switch', 'href="en.html" data-lang-switch')
            if kh != h: open(os.path.join(ROOT, p), 'w', encoding='utf-8').write(kh)
            skipped.append(p); continue
        open(ep, 'w', encoding='utf-8').write(e)
        left += len(rest)
    # 영어판이 없는 페이지로 가는 링크는 한국어 페이지로
    for p in pages:
        ep = os.path.join(ROOT, 'en-' + p)
        if not os.path.exists(ep): continue
        e = open(ep, encoding='utf-8').read()
        e2 = re.sub(r'href="en-([a-z0-9_-]+\.html)', lambda m: m.group(0) if m.group(1) not in skipped else 'href="' + m.group(1), e)
        if e2 != e: open(ep, 'w', encoding='utf-8').write(e2)
    # 영어 홈(en.html)도 영어판끼리 잇는다
    hp = os.path.join(ROOT, 'en.html')
    if os.path.exists(hp):
        h = open(hp, encoding='utf-8').read()
        h = re.sub(r'(href=")([a-z0-9_-]+\.html)((?:#[^"]*)?")', lambda m: m.group(0) if m.group(2) in ('en.html', 'index.html') or m.group(2) in skipped else link(m), h)
        h = h.replace('assets/site.js?', 'assets/site.en.js?')
        open(hp, 'w', encoding='utf-8').write(h)
    print(f'wrote {len(pages) - len(skipped)} English pages · skipped (not translated yet) {len(skipped)} · untranslated text nodes left ≈ {left}', flush=True)


if __name__ == '__main__':
    main()
