#!/usr/bin/env python3
"""영어판 페이지 만들기 — gen/gen2.py 가 만든 한국어 페이지(*.html)마다 영어판 en-<페이지>.html 을 만든다.

- 페이지의 한국어 문구(본문 글자, 안내 글, 버튼, 체험 화면 속 글자, 화면 스크립트 속 글자)를 모아 번역한다.
- 번역은 content/i18n/en.json 에 쌓아 두고 다시 쓴다. 새 문구만 GitHub Models(AI 번역)로 번역한다
  (GITHUB_TOKEN 이 있고 models 권한이 있을 때). 번역하지 못한 문구는 한국어 그대로 둔다(배포는 멈추지 않는다).
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

def translate_batch(items, token):
    if FAILS[0] >= 4:
        return None
    prompt = ('Translate each Korean UI/web text in the JSON array into natural, concise English for a university EdTech website. '
              'Return ONLY a JSON array of the same length and order. Keep numbers, dates, URLs, file names, product names, emoji, '
              'symbols like ①·→★ and any HTML entities as they are. Replace Korean corner brackets 「」 with double quotes. '
              'If an item is a fragment, translate it as a fragment. Do not add explanations.\n' + GLOSSARY + '\n\n' + json.dumps(items, ensure_ascii=False))
    body = json.dumps({'model': MODEL, 'temperature': 0.1, 'messages': [{'role': 'user', 'content': prompt}]}).encode()
    for attempt in range(5):
        req = urllib.request.Request('https://models.github.ai/inference/chat/completions', data=body,
                                     headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json', 'Accept': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read().decode('utf-8', 'replace')
            try:
                txt = json.loads(raw)['choices'][0]['message']['content'].strip()
            except Exception:
                print('  bad response:', raw[:300].replace('\n', ' '), file=sys.stderr)
                FAILS[0] += 1
                return None
            txt = re.sub(r'^```(?:json)?\s*|\s*```$', '', txt)
            arr = json.loads(txt)
            if isinstance(arr, list) and len(arr) == len(items):
                return [str(x) for x in arr]
            print('  length mismatch', len(arr), len(items), file=sys.stderr)
            return None
        except urllib.error.HTTPError as e:
            wait = int(e.headers.get('retry-after') or 0) or (20 * (attempt + 1))
            print('  http', e.code, 'wait', wait, file=sys.stderr)
            if e.code in (401, 403) or wait > 600:
                return None
            time.sleep(wait)
        except Exception as e:
            print('  error', e, file=sys.stderr); FAILS[0] += 1; time.sleep(3)
        if FAILS[0] >= 4:
            return None
    return None


def fill(missing, cache, token, budget):
    missing = sorted(missing, key=len)
    batch, size, sent = [], 0, 0
    def flush():
        nonlocal batch, size, sent
        if not batch: return
        if sent >= budget or FAILS[0] >= 4: batch, size = [], 0; return
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
        if size + len(k) > 2500 or len(batch) >= 60:
            flush()
        batch.append(k); size += len(k)
    flush()


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
    missing = [k for k in need if k not in cache and k not in fix]
    print(f'pages {len(pages)} · strings {len(need)} · cached {len(need) - len(missing)} · new {len(missing)}', flush=True)
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if missing and token and os.environ.get('EN_MT', '') == '1':   # 자동 번역 서버는 EN_MT=1 일 때만(GitHub Models 는 2026년 서비스 종료로 응답하지 않음)
        fill(missing, cache, token, int(os.environ.get('EN_BUDGET', '140')))
    elif missing:
        print('  no token: untranslated strings stay Korean', flush=True)
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)

    def tr(t):
        k = norm(t)
        return fix.get(k) or cache.get(k) or t
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
        e = re.sub(r'<a class="txt" href="en[^"]*" data-lang-switch>ENG</a>', f'<a class="txt" href="{p}" lang="ko">KOR</a>', e)
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
