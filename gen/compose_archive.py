# -*- coding: utf-8 -*-
"""아카이브 본문 조립기: PDF에서 뽑은 사실(JSON)을 사이트 글 서식(.art-*)으로 조립해 content/archive.json 에 넣는다.
사용: python3 gen/compose_archive.py <facts 폴더>
 - <id>.json 이 있는 글만 바꾼다. 사례(스키마 A: course 키)와 보고서(스키마 B: title 키)를 구분한다.
 - 문서에 없는 항목은 비워 둔다(지어 넣지 않음)."""
import json, os, sys, html, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'content', 'archive.json')
CONTACT = '문의: KELI 사무국 033-248-3242 / contact@keliedu.org'

_PREF = re.compile(r'\s*\((?:p|pp)\.?\s*\d+(?:\s*[–~,-]\s*(?:p\.?)?\d+)*\)')
def e(s):
    s = '' if s is None else str(s)
    s = _PREF.sub('', s).strip()          # 추출 때 붙인 쪽수 표기 "(p.3)" 제거
    return html.escape(s, quote=False)

_SENT = re.compile(r'(?<=[다음함됨임요됐성음]\.)\s+')
def clip(t, n=2):
    """긴 서술을 앞 n문장까지만. 추출 문장이 길어 화면에서 읽기 쉽게 줄인다."""
    t = '' if t is None else str(t).strip()
    parts = _SENT.split(t)
    out = ' '.join(parts[:n]).strip()
    if len(parts) > n and not out.endswith('.'): out += '.'
    return out

def ul(items, cls='art-ul'):
    items = [i for i in (items or []) if i]
    return f'<ul class="{cls}">' + ''.join(f'<li>{e(i)}</li>' for i in items) + '</ul>' if items else ''

def ol(items):
    items = [i for i in (items or []) if i]
    return '<ol class="art-ol">' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>' if items else ''

def chips(words):
    words = [w for w in (words or []) if w]
    return '<div class="chips">' + ''.join(f'<span class="chip">{e(w)}</span>' for w in words) + '</div>' if words else ''

def kv(pairs):
    pairs = [(k, v) for k, v in pairs if v]
    return '<dl class="art-kv">' + ''.join(f'<dt>{e(k)}</dt><dd>{v}</dd>' for k, v in pairs) + '</dl>' if pairs else ''

def h(t):
    return f'<h2 class="art-h">{e(t)}</h2>'

_MID = re.compile(r'(?<=[가-힣\)\]”])\.\s+(?=\S)')
def summary(items):
    items = [_MID.sub(' — ', i).rstrip('.') for i in (items or []) if i]
    return '<div class="art-sum"><span class="k">핵심 요약</span>' + ul(items) + '</div>' if items else ''

def note(lines):
    lines = [l for l in lines if l]
    return '<div class="art-note">' + '<br>'.join(lines) + '</div>'

def table(rows, head=('항목', '내용')):
    rows = [r for r in (rows or []) if r and r[0]]
    if not rows: return ''
    return ('<div class="tbl-wrap"><table class="tbl"><thead><tr>' + ''.join(f'<th>{e(x)}</th>' for x in head) + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join(f'<td>{e(c)}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table></div>')

def sem_label(s):
    """'2025-2' → '2025학년도 2학기'."""
    if not s: return ''
    m = re.match(r'(20\d\d)\s*[-–/]\s*([12])', str(s))
    return f'{m.group(1)}학년도 {m.group(2)}학기' if m else str(s)

def join(*parts, sep=' · '):
    return sep.join(str(p) for p in parts if p)

# ---------------------------------------------------------------- 사례(스키마 A)
def compose_case(f, item):
    prof = f.get('professor') or item.get('author') or ''
    dept = f.get('dept') or ''
    def num(v, unit):
        v = str(v or '').strip()
        return (v + unit) if v and not v.endswith(unit) else v
    details = join(f.get('course_type'), num(f.get('credits'), '학점'), num(f.get('grade'), '학년'), sep=', ')
    course_line = join(f.get('course'), f'({details})' if details else '', sep=' ')
    st_ = str(f.get('students') or '').strip()
    sem_line = join(sem_label(f.get('semester')), (f'수강생 {num(st_, "명")}' if st_ else ''))
    tools = f.get('ai_tools') or []
    head = kv([
        ('교과목', e(course_line)),
        ('교수', e(join(prof + (' 교수' if prof and not prof.endswith('교수') else ''), f'({dept})' if dept else '', sep=' '))),
        ('대학', e(f.get('university') or '한림대학교')),
        ('학기', e(sem_line)),
        ('활용 AI 도구', e(', '.join(tools)) if isinstance(tools, list) else e(tools)),
    ])
    sm = summary(f.get('summary'))
    lead = f'<p class="art-lead">{e(clip(f.get("overview"), 3))}</p>' if f.get('overview') else ''
    goals = (h('수업 목표') + ul([clip(g, 1) for g in (f.get('goals') or [])][:3])) if f.get('goals') else ''
    plan = f.get('plan') or []
    steps = []
    for p in plan:
        if not isinstance(p, dict): continue
        st = e(p.get('stage')); act = e(clip(p.get('activity'), 2)); ai = e(clip(p.get('ai_use'), 1))
        body = ' — '.join(x for x in (act,) if x)
        if ai: body += f' <span class="muted">(AI 활용: {ai})</span>' if body else f'AI 활용: {ai}'
        steps.append(f'<strong>{st}</strong>' + (f' — {body}' if body else ''))
    method = (h('적용 방법') + ol(steps)) if steps else ''
    weekly = (h('주요 주차') + ul([clip(w, 2) for w in (f.get('weekly_highlights') or [])][:4])) if f.get('weekly_highlights') else ''
    rows = [(r.get('item'), r.get('value')) for r in (f.get('results') or []) if isinstance(r, dict) and r.get('item') and r.get('value')]
    short = [r for r in rows if len(str(r[1])) <= 60][:8]          # 수치·짧은 결과는 표로
    long_ = [r for r in rows if len(str(r[1])) > 60][:4]           # 서술형 결과는 목록으로
    results = ''
    if short or long_ or f.get('effects'):
        results = h('결과') + table(short)
        if long_:
            results += '<ul class="art-ul">' + ''.join(f'<li><strong>{e(k)}</strong> — {e(clip(v, 2))}</li>' for k, v in long_) + '</ul>'
        if f.get('effects'):
            results += ('<p class="art-k">교육적 효과</p>' if (short or long_) else '') + ul([clip(x, 2) for x in (f.get('effects') or [])][:4])
    diff = (h('어려웠던 점') + ul([clip(x, 2) for x in (f.get('difficulties') or [])][:3])) if f.get('difficulties') else ''
    diff += (h('개선 방향') + ul([clip(x, 2) for x in (f.get('improvements') or [])][:3])) if f.get('improvements') else ''
    q = f.get('instructor_quote') or {}
    quote = ''
    if isinstance(q, dict) and q.get('text'):
        quote = f'<blockquote class="art-quote">“{e(q["text"])}”<cite>— {e(prof)} 교수</cite></blockquote>'
    kw = (h('키워드') + chips(f.get('keywords'))) if f.get('keywords') else ''
    toc = h('자료 구성') + ol(['AI 활용 수업 계획서', 'AI 활용 수업 주차별 세부 계획서', 'AI 활용 수업 결과보고서'])
    nt = note(['※ 사례집 전문(PDF)은 위 "PDF 바로 보기" 또는 아래 "자료 파일"에서 볼 수 있습니다.',
               f'· 인용: {e(prof)}({item.get("date", "")[:4]}), AI 활용 수업 사례 — {e(f.get("course"))}, 한림대학교 · KELI 사무국',
               '· ' + CONTACT])
    return sm + head + lead + goals + method + weekly + results + diff + quote + kw + toc + nt

# ---------------------------------------------------------------- 보고서(스키마 B)
def compose_report(f, item):
    authors = f.get('authors') or ([item.get('author')] if item.get('author') else [])
    pages = f.get('pages')
    date = f.get('date') or item.get('period') or item.get('date')
    sm = summary(f.get('summary') or [x.get('text') if isinstance(x, dict) else x for x in (f.get('findings') or [])][:3])
    head = kv([
        ('발행', e(join(date, f.get('org') or item.get('org')))),
        ('저자', e(', '.join(authors))),
        ('분량', e(f'{pages}쪽 · PDF') if pages else ''),
        ('분석 자료', e(f.get('data'))),
    ])
    intro = ''
    if f.get('purpose') or f.get('method'):
        intro = h('보고서 소개') + ''.join(f'<p>{e(x)}</p>' for x in (f.get('purpose'), f.get('method')) if x)
    finds = [x.get('text') if isinstance(x, dict) else x for x in (f.get('findings') or [])]
    findings = (h('주요 분석 결과' if f.get('data') else '주요 내용') + ul(finds)) if finds else ''
    impl = (h('시사점과 제언') + ul(f.get('implications'))) if f.get('implications') else ''
    toc = (h('구성') + ol([e(t) for t in f['toc']])) if f.get('toc') else ''
    kw = (h('키워드') + chips(f.get('keywords'))) if f.get('keywords') else ''
    first = (authors[0].split('(')[0].strip() if authors else (item.get('org') or 'KELI 사무국'))
    nt = note(['※ 보고서 전문(PDF)은 위 "PDF 바로 보기" 또는 아래 "자료 파일"에서 볼 수 있습니다.',
               f'· 인용: {e(first)}({str(item.get("date", ""))[:4]}), {e(f.get("title") or item.get("title"))}, {e(f.get("org") or item.get("org") or "KELI 사무국")}',
               '· ' + CONTACT])
    return sm + head + intro + findings + impl + toc + kw + nt

def main(folder):
    d = json.load(open(P, encoding='utf-8'))
    items = d if isinstance(d, list) else d['items']
    done = []
    for it in items:
        fp = os.path.join(folder, it['id'] + '.json')
        if not os.path.exists(fp): continue
        f = json.load(open(fp, encoding='utf-8'))
        it['body'] = compose_case(f, it) if f.get('course') else compose_report(f, it)
        done.append(it['id'])
    json.dump(d, open(P, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('composed:', ' '.join(done))

if __name__ == '__main__':
    main(sys.argv[1])
