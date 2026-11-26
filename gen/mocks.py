# -*- coding: utf-8 -*-
"""HAI 체험관 「직접 해 보기」 — 실제로 눌리고 입력되는 체험용 화면(목업).
매뉴얼·소개자료에 실린 화면을 본떠 HTML로 다시 만든 것이며, 실제 서비스와 연결되지 않는다(입력 내용은 어디에도 보내지 않음).
화면 안 요소에 붙이는 속성(gen2.py WALK_JS 가 해석):
  data-goal        이 요소를 누르면(폼이면 보내면, 검색칸이면 입력하면) 미션 성공
  data-on          누르면 형제들 가운데 이것만 .on
  data-filter=K    [data-cat] 가운데 K 만 보이기(all = 전부)   · data-search  입력한 글자가 들어간 [data-cat] 만 보이기
  data-show-now=S  바로 보이기 · data-wait=S  잠깐(1.1초) 보였다 숨기기(입력 중 표시) · data-show=S  그 뒤에 보이기 · data-hide=S  숨기기
  data-echo=S      폼에 쓴 글을 S 에 넣기 · data-set="S|글"  S 의 글자를 바꾸기 · data-step=N  [data-stepper] 의 N 번째까지 .on
  data-check="묶음|정답번호"  묶음 안에서 .on 인 것이 정답이면 [data-right], 아니면 [data-wrong], 안 골랐으면 [data-need] 보이기(any = 아무거나 정답)
  data-tg          누를 때마다 .on 켜고 끄기(안의 small 글자를 ON/OFF 로)
  data-allon=S     S 묶음마다 .on 이 하나씩 있어야 함(없으면 [data-need])
  data-req=S       S 칸에 글이 없으면 [data-need] 를 보이고 멈춤
  canvas[data-draw] 손글씨 칸(목표면 조금 그렸을 때 성공) · data-clear=S  손글씨 지우기
  data-go=N        N번째 미션 화면으로 가기(옆 메뉴) · data-fill=글  폼 입력칸에 글 넣기 · form[data-form data-sample=예시 data-note=S data-log=S data-more=글]
"""
from html import escape as E

def ic(name, s=16):
    P = {
        'home': '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
        'chat': '<path d="M4 5h16v11H9l-5 4z"/>',
        'doc': '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 13h6M9 17h6"/>',
        'edit': '<path d="M5 4h9l5 5v11H5z"/><path d="M9 15l5-5 2 2-5 5H9z"/>',
        'mark': '<path d="M6 3h12v18l-6-4-6 4z"/>',
        'bell': '<path d="M6 16V10a6 6 0 0112 0v6l2 2H4z"/><path d="M10 21h4"/>',
        'chart': '<path d="M4 20V4"/><path d="M4 20h16"/><path d="M8 16v-5M12 16V8M16 16v-3"/>',
        'gear': '<circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M5.6 18.4l2.1-2.1M16.3 7.7l2.1-2.1"/>',
        'help': '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-.9.6-1.5 1.1-1.5 2.2"/><path d="M12 17v.01"/>',
        'search': '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/>',
        'clip': '<path d="M8 12l6-6a3 3 0 014 4l-8 8a5 5 0 01-7-7l8-8"/>',
        'send': '<path d="M5 4l15 8-15 8 3-8z"/>',
        'shield': '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
        'down': '<path d="M12 4v11"/><path d="M7 11l5 5 5-5"/><path d="M5 20h14"/>',
        'check': '<path d="M5 12l5 5 9-10"/>',
        'user': '<circle cx="12" cy="8" r="4"/><path d="M4 21c1-4 4-6 8-6s7 2 8 6"/>',
    }
    return f'<svg class="mk-ic" width="{s}" height="{s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{P[name]}</svg>'

def side(brand, sub, groups, active, user=None, foot=(), go=None, light=False, top='', mid=''):
    go = go or {}
    h = f'<aside class="mk-side{" light" if light else ""}"><div class="mk-brand"><strong>{brand}</strong>{("<small>" + sub + "</small>") if sub else ""}</div>'
    h += top
    for label, items in groups:
        h += (f'<span class="mk-grp">{label}</span>' if label else '') + ''.join((f'<button type="button" class="mk-nav{" on" if k == active else ""}" data-go="{go[k]}">{ic(i)}{t}</button>' if k in go else f'<span class="mk-nav{" on" if k == active else ""}">{ic(i)}{t}</span>') for k, i, t in items)
    h += mid + '<span class="mk-sp"></span>' + ''.join(f'<span class="mk-nav">{ic(i)}{t}</span>' for i, t in foot)
    if user: h += f'<div class="mk-user"><span class="mk-uav">{ic("user", 14)}</span><span><b>{user[0]}</b><small>{user[1]}</small></span></div>'
    return h + '</aside>'

def frame(theme, side_html, top, main, aside=''):
    return (f'<div class="mk" style="{theme}">{side_html}<div class="mk-main"><div class="mk-top"><b>{top[0]}</b><span>{top[1]}</span></div>{main}</div>{aside}</div>')

def login(theme, hero, panel, fields, btns, done='로그인되었어요. 「다음」을 눌러 안으로 들어가 보세요.', foot='', extra=''):
    """로그인 화면. hero=(작은 글, 큰 제목, 설명[, 칩들]) · fields=[(이름, 자리글, type)] · btns=[(글, 주단추?, 목표?)]"""
    chips = ''.join(f'<i>{c}</i>' for c in (hero[3] if len(hero) > 3 else []))
    # 체험 화면이라 브라우저에 저장된 실제 아이디·비밀번호가 자동으로 채워지지 않게 한다(읽기 전용으로 두었다가 누르면 풀림)
    f = ''.join(f'<label>{n}<input type="{t}" placeholder="{ph}" autocomplete="{"new-password" if t == "password" else "off"}" name="mk-{k}-{abs(hash(ph)) % 9999}" data-lpignore="true" data-1p-ignore readonly data-ro></label>' for k, (n, ph, t) in enumerate(fields))
    b = ''.join(f'<button type="button" class="mk-btn wide{"" if pri else " soft"}" data-show="[data-done]"{" data-goal" if goal else ""}>{t}</button>' for t, pri, goal in btns)
    return (f'<div class="mk mk-login" style="{theme}"><div class="mk-hero"><small>{hero[0]}</small><b>{hero[1]}</b><span>{hero[2]}</span><div class="mk-hchips">{chips}</div></div>'
            f'<div class="mk-lg"><small>{panel[0]}</small><h3>{panel[1]}</h3>{f}{extra}{b}<p class="mk-ok" data-done hidden>{ic("check", 15)}{done}</p>{("<p class=mk-ref>" + foot + "</p>") if foot else ""}</div></div>')

def me(text='', attrs=''): return f'<div class="mk-msg me" {attrs}><div class="mk-bub" data-q>{text}</div></div>'
def ai(html, attrs='', av='AI'): return f'<div class="mk-msg ai" {attrs}><span class="mk-av">{av}</span><div class="mk-bub">{html}</div></div>'
def dots(av='AI'): return f'<div class="mk-msg ai" data-dots hidden><span class="mk-av">{av}</span><div class="mk-bub mk-dots"><i></i><i></i><i></i></div></div>'
def inbar(sample, ph, goal=False, show='[data-a]', hide='[data-hello]', pre='', post='', more='체험판에서는 예시 질문 하나에만 답해 드려요. 실제 서비스에서는 올린 자료와 대화 내용을 바탕으로 답합니다.', log='#mklog'):
    """대화 입력줄: 보내면 [data-q] 에 쓴 글 → [data-qa] 보이기 → 입력 중 표시 → show 보이기. 예시와 다른 글이면 [data-demo] 안내."""
    return (f'<form class="mk-inbar" data-form data-sample="{sample}" data-echo="[data-q]" data-hide="{hide}" data-show-now="[data-qa]" data-wait="[data-dots]" data-show="{show}" data-note="[data-demo]" data-log="{log}" data-more="{more}"{" data-goal" if goal else ""}>'
            f'{pre}<input type="text" data-in placeholder="{ph}" aria-label="입력" autocomplete="off">{post}<button type="submit" class="mk-send" aria-label="보내기">{ic("send", 15)}</button></form>')
def demo(q): return f'<p class="mk-demo" data-demo hidden>체험판에서는 예시 「{q}」의 답변을 보여 드려요.</p>'
def toast(key, text): return f'<p class="mk-ok" {key} hidden>{ic("check", 15)}{text}</p>'

# ------------------------------------------------------------------ HAI-Docs (소개자료의 문서 라이브러리 · AI 대화 · DocsGen 화면)
def _docs():
    TH = '--mk:#1d4ed8;--mk-side:#0b2a5b'
    def sd(active):
        return side('HAI-Docs <i>AI</i>', '○○ UNIVERSITY', [
            ('WORKSPACE', [('home', 'home', '홈'), ('chat', 'chat', 'AI 대화'), ('lib', 'doc', '문서 라이브러리'), ('gen', 'edit', '문서 생성'), ('mark', 'mark', '북마크'), ('rem', 'bell', '리마인드')]),
            ('ADMIN', [('dash', 'chart', '대시보드'), ('sys', 'gear', '시스템 관리')])], active, user=('박직원', '교무팀 · 직원'), foot=[('gear', '설정'), ('help', '도움말')], go={'lib': 0, 'chat': 2, 'gen': 4})
    DOCS = [('○○대학교_학사운영규정', 'PDF', '2.4 MB', '2026.03.15', '완료', '규정'), ('교원인사규정', 'HWP', '1.8 MB', '2026.03.12', '진행중', '규정'), ('자체평가계획서', 'PDF', '3.1 MB', '2026.03.10', '완료', '보고서'),
            ('학칙시행세칙', 'HWP', '1.2 MB', '2026.03.08', '완료', '규정'), ('수업평가_실시안내', 'PDF', '0.9 MB', '2026.03.05', '진행중', '공지'), ('교내장학금규정', 'DOCX', '1.5 MB', '2026.03.01', '완료', '규정')]
    cards = ''.join(f'<div class="mk-card mk-doc" data-cat="{c}"><div class="mk-row"><span class="mk-file {t.lower()}">{ic("doc", 18)}</span><span class="mk-st {"ing" if st == "진행중" else "ok"}">{st}</span></div>'
                    f'<strong>{n}</strong><span class="mk-chip">{t}</span><div class="mk-row mk-meta"><span>{sz}</span><span>{d}</span></div></div>' for n, t, sz, d, st, c in DOCS)
    def lib(goal):
        tabs = ''.join(f'<button type="button" class="{"on" if k == "all" else ""}" data-filter="{k}" data-on{" data-goal" if goal == "tab" and k == "규정" else ""}>{t}</button>' for k, t in [('all', '전체'), ('규정', '규정'), ('업무', '업무'), ('공지', '공지'), ('보고서', '보고서')])
        main = (f'<div class="mk-h"><h3>문서 라이브러리</h3><span class="mk-badge">총 128건</span></div>'
                f'<div class="mk-bar"><div class="mk-tabs">{tabs}</div><label class="mk-search">{ic("search", 15)}<input type="search" placeholder="문서 검색..." aria-label="문서 검색" autocomplete="off" data-search{" data-goal" if goal == "search" else ""}></label></div>'
                f'<div class="mk-grid">{cards}</div><p class="mk-empty" data-empty hidden>조건에 맞는 문서가 없습니다. (체험판에는 문서 6건만 들어 있어요)</p>')
        return frame(TH, sd('lib'), ('HAI-Docs', '문서 라이브러리'), main)
    Q = '교원 연구년 제도의 가입 대상과 기간은 어떻게 되나요?'
    SRC = [('1', '교원인사규정', '제27조(연구년)', 'PDF', 'p. 12'), ('2', '교원 연구년 운영 지침', '제4조(기간 및 절차)', 'PDF', 'p. 4'), ('3', '연구년 신청 안내 공지', '(교무처-2026-12)', 'HWP', 'p. 1')]
    def chat(answered, goal):
        hid = '' if answered else ' hidden'
        src = ''.join(f'<button type="button" class="mk-src" data-on data-hide=".mk-cite" data-show="#mkc{n}"{" data-goal" if goal == "src" and n == "1" else ""}><span class="mk-row"><b>[{n}]</b>{ic("doc", 14)}</span><strong>{t}</strong><span>{a}</span><span class="mk-row mk-meta"><span class="mk-chip">{f}</span><span>{p}</span></span></button>' for n, t, a, f, p in SRC)
        cites = ''.join(f'<div class="mk-cite" id="mkc{n}" hidden>{ic("doc", 15)}<span><b>근거 원문 위치</b> {t} {a} · {f} {p.replace("p. ", "")}쪽</span></div>' for n, t, a, f, p in SRC)
        ans = (f'<div class="mk-msg me" data-qa{hid}><div class="mk-bub" data-q>{Q if answered else ""}</div></div>'
               f'<div class="mk-msg ai" data-dots hidden><span class="mk-av">AI</span><div class="mk-bub mk-dots"><i></i><i></i><i></i></div></div>'
               f'<div class="mk-msg ai" data-a{hid}><span class="mk-av">AI</span><div class="mk-bub"><p class="mk-demo" data-demo hidden>체험판에서는 예시 질문 「{Q}」의 답변을 보여 드려요.</p>'
               f'<p>○○대학교 교원 연구년 제도는 다음과 같이 운영됩니다.</p><ul class="mk-ck"><li><b>대상:</b> 전임교원(조교수 이상)으로 재직기간 3년 이상인 자</li><li><b>기간:</b> 1년 또는 2년(단, 연속 2회 초과 불가)</li></ul>'
               f'<p class="mk-ref">(근거: ○○대학교 교원인사규정 제27조(연구년))</p></div></div>'
               f'<div class="mk-block" data-a{hid}><div class="mk-row"><b>참고 문서 <small>(원문 근거)</small></b><span class="mk-link">모두 보기</span></div><div class="mk-srcs">{src}</div>{cites}'
               f'<p class="mk-note">{ic("shield", 15)}<span>AI 응답은 등록된 ○○대학교 공식 문서를 기반으로 생성되었습니다. 부정확한 정보 발견 시 피드백을 통해 개선에 참여해주세요.</span></p>'
               f'<div class="mk-sub">관련 질문 제안</div><div class="mk-chips"><button type="button" data-fill="연구년 신청 절차">연구년 신청 절차</button><button type="button" data-fill="연구년 중 강의 배정">연구년 중 강의 배정</button><button type="button" data-fill="연구년 종료 후 의무">연구년 종료 후 의무</button></div></div>')
        start = '' if answered else f'<div class="mk-hello" data-hello><b>무엇을 도와드릴까요?</b><span>규정·공지·양식 등 등록된 행정 문서를 근거로 답해 드려요.</span><div class="mk-chips"><button type="button" data-fill="{Q}">예시 질문: {Q}</button></div></div>'
        form = (f'<form class="mk-inbar" data-form data-sample="{Q}" data-echo="[data-q]" data-hide="[data-hello]" data-show-now="[data-qa]" data-wait="[data-dots]" data-show="[data-a],[data-res]" data-note="[data-demo]" data-log="#mklog" '
                f'data-more="체험판에서는 예시 질문 하나에만 답해 드려요. 실제 서비스에서는 등록된 문서를 근거로 답합니다."{" data-goal" if goal == "ask" else ""}>'
                f'<input type="text" data-in placeholder="행정 문서에 대해 질문해 주세요..." aria-label="질문" autocomplete="off"><span class="mk-ghost">{ic("clip", 16)}</span><button type="submit" class="mk-send" aria-label="보내기">{ic("send", 15)}</button></form>')
        RES = [('교원인사규정', 'PDF · 2.4 MB'), ('교원 연구년 운영 지침', 'HWP · 1.2 MB'), ('연구년 신청 안내 공지', 'PDF · 0.8 MB'), ('교원 복무 관련 FAQ', 'PDF · 0.6 MB'), ('연구활동 지원 규정', 'HWP · 1.5 MB')]
        aside = (f'<aside class="mk-aside" data-res{hid}><b>검색 결과 <small>128건</small></b>' + ''.join(f'<div class="mk-res"><span class="mk-file {m.split(" ")[0].lower()}">{ic("doc", 15)}</span><span><strong>{t}</strong><small>{m}</small></span></div>' for t, m in RES) + '<span class="mk-link">검색 결과 더보기</span></aside>')
        main = f'<div class="mk-h"><h3>AI 대화</h3></div><div class="mk-log" id="mklog">{start}{ans}</div>{form}'
        return frame(TH, sd('chat'), ('HAI-Docs', 'AI 대화'), main, aside)
    EX = ['교원 해외여행 결과보고 미제출자에게 제출을 안내하는 공문', '전임교원 겸직 신청 절차와 제출서류를 안내하는 내부 공지', '교원 업적평가 연구영역 자료 제출 요청 공문을 작성해줘']
    TPL = [('공문서 기본 템플릿', '제목과 주요 내용을 바탕으로 ○○대학교 행정 공문서 초안을 생성합니다.'), ('공지사항 기본 템플릿', '공지 대상, 기간, 안내사항을 중심으로 게시용 공지 초안을 생성합니다.'), ('회의록 기본 템플릿', '회의명, 참석자, 안건, 결정사항을 중심으로 회의록 초안을 생성합니다.'),
           ('계획서 기본 템플릿', '목적, 추진 일정, 담당 부서를 중심으로 계획서 초안을 생성합니다.'), ('보고서 기본 템플릿', '보고 배경, 주요 결과, 후속 조치를 중심으로 보고서 초안을 생성합니다.'), ('요청서 기본 템플릿', '요청 배경, 요청 사항, 기한을 중심으로 요청서 초안을 생성합니다.')]
    def gen():
        tpl = ''.join(f'<button type="button" class="mk-card mk-tpl" data-on data-step="1" data-set="[data-tname]|{t}" data-show="[data-draft]"{" data-goal" if k == 0 else ""}><span class="mk-row"><strong>{t}</strong>{ic("edit", 15)}</span><span>{d}</span></button>' for k, (t, d) in enumerate(TPL))
        main = (f'<div class="mk-h"><h3>DocsGen 문서 생성</h3></div>'
                f'<div class="mk-stepper" data-stepper><span class="on"><i>1</i><b>요청 입력</b><small>문서 유형·내용</small></span><span><i>2</i><b>초안 검토</b><small>초안 검토</small></span><span><i>3</i><b>확정 다운로드</b><small>최종 파일</small></span></div>'
                f'<div class="mk-fields"><label>문서 유형<select aria-label="문서 유형"><option>공문</option><option>공지</option><option>회의록</option><option>계획서</option><option>보고서</option><option>요청서</option></select></label>'
                f'<div><span>출력 형식</span><div class="mk-seg"><button type="button" class="on" data-on data-set="[data-fmt]|PDF">PDF</button><button type="button" data-on data-set="[data-fmt]|DOCX">DOCX</button><button type="button" data-on data-set="[data-fmt]|HWPX">HWPX</button></div></div></div>'
                f'<div class="mk-guide"><b>교원인사팀 우선 문서생성 기준</b><span>현재 문서생성은 교원인사팀 실무에 맞춰, 규정, 복무, 임용, 평가, 위원회 관련 공문·공지 초안을 우선 검증합니다.</span>'
                f'<div class="mk-chips">' + ''.join(f'<button type="button" class="{"on" if k == 2 else ""}" data-on data-set="[data-req]|{x}">{x}</button>' for k, x in enumerate(EX)) + '</div></div>'
                f'<div class="mk-row"><b>부서별 DocsGen 템플릿</b><small>사용 가능 10개 / 전체 18개</small></div>'
                f'<div class="mk-tabs mk-pill">' + ''.join(f'<button type="button" class="{"on" if k == 0 else ""}" data-on>{x}</button>' for k, x in enumerate(['교원인사팀', '교무팀', '교육혁신센터', '학생지원', '행정지원', '대외협력', '입학'])) + '</div>'
                f'<div class="mk-grid two">{tpl}</div>'
                f'<div class="mk-paper" data-draft hidden><div class="mk-row"><b>초안 검토 · <span data-tname>공문서 기본 템플릿</span></b><span class="mk-badge">체험용 예시 초안</span></div>'
                f'<div class="mk-sheet"><p class="c">한 림 대 학 교</p><p><b>수신</b> 수신자 참조</p><p><b>제목</b> <span data-req>{EX[2]}</span></p><hr><p>1. 귀 부서의 무궁한 발전을 기원합니다.</p><p>2. 위 제목과 관련하여 아래와 같이 안내하오니 기한 내에 협조하여 주시기 바랍니다.</p><p class="in">가. 대상: (요청 내용에 따라 작성)</p><p class="in">나. 기한: (요청 내용에 따라 작성)</p><p class="in">다. 제출 방법: (요청 내용에 따라 작성)</p><p>붙임 관련 서식 1부. 끝.</p></div>'
                f'<p class="mk-demo">체험용으로 만든 예시 초안이에요. 실제 서비스가 만드는 초안과는 다를 수 있어요.</p>'
                f'<div class="mk-row end"><button type="button" class="mk-btn" data-step="2" data-show="[data-done]">{ic("down", 15)}확정 · <span data-fmt>PDF</span> 다운로드</button></div><p class="mk-ok" data-done hidden>{ic("check", 15)}확정했어요. 체험판이라 파일은 내려받아지지 않아요.</p></div>')
        return frame(TH, sd('gen'), ('HAI-Docs', '문서 생성'), main)
    I = 'media/walk/hai-docs/'
    return [
        dict(title='행정 문서를 라이브러리에 모아요', text='규정·공지·양식 같은 HWP/PDF/DOCX 문서를 문서 라이브러리에 모으면 AI가 구조화해 찾기 쉽게 만들어요. 분류 탭으로 필요한 종류만 골라 볼 수 있어요.',
             do='문서 라이브러리에서 「규정」 탭을 눌러 규정 문서만 모아 보세요.', ui=lib('tab'), img=I + '2.jpg'),
        dict(title='필요한 문서를 바로 찾아요', text='문서 이름으로 검색하면 맞는 문서만 바로 추려 보여 줘요.',
             do='문서 검색 칸에 「장학」을 입력해 문서를 찾아보세요.', ui=lib('search'), img=I + '2.jpg'),
        dict(title='AI 대화로 질문해요', text='궁금한 행정 업무를 물으면 관련 규정과 문서를 찾아 근거와 함께 답해 줘요. 함께 찾은 문서 목록도 보여 줘요.',
             do='입력창에 질문을 쓰고 보내 보세요. 비워 둔 채 보내면 예시 질문이 입력돼요.', ui=chat(False, 'ask'), img=I + '3.jpg'),
        dict(title='근거를 검증하고 출처를 확인해요', text='답변마다 참고 문서가 붙어 있어 어느 문서의 어느 조항·쪽을 근거로 했는지 바로 확인할 수 있어요.',
             do='참고 문서 [1] 「교원인사규정」을 눌러 근거 위치를 확인해 보세요.', ui=chat(True, 'src'), img=I + '3.jpg'),
        dict(title='DocsGen으로 문서 초안을 만들어요', text='문서 유형과 출력 형식을 정하고 부서별 템플릿을 고르면 초안이 만들어져요. 담당자가 검토한 뒤 확정해 내려받아요.',
             do='「공문서 기본 템플릿」을 눌러 문서 초안을 만들어 보세요.', ui=gen(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Tutor (교수용 AI 조교 매뉴얼)
def _tutor():
    # AI 조교(HAI-Tutor) 사용자 매뉴얼 Ver 2.0 (01 로그인 ~ 07 마이페이지) 순서대로
    TH = '--mk:#2f6fed;--mk-side:#0b2a66'
    HIST = ['이번 학기 수업계획서를 생성해 주세요.', '창의적인 프론트엔드 기술에 대해 쉬운…', '메모리 관리에 관해 쉬운 단답식 1문제…']
    NAV = [('new', 'chat', '새로운 대화'), ('src', 'doc', '소스 문서 관리'), ('con', 'edit', '콘텐츠 관리'), ('stu', 'user', '수강생 관리'), ('exam', 'chart', '문제출제 및 시험관리')]
    SUB = {'gen': '문제생성', 'bank': '문제은행', 'old': '기출 시험지', 'quiz': '퀴즈 관리', 'grade': '시험지 채점'}
    def sd(active, sub=None):
        mid = ''
        if active == 'exam':
            mid = ''.join(f'<span class="mk-nav" style="padding-left:30px;{"opacity:1;font-weight:700;background:#e8eefc;color:#1e3a8a" if k == sub else ""}">{t}</span>' for k, t in SUB.items())
        h = side('AI 조교 <i>v1.1.4</i>', '', [('', NAV)], active, user=('홍길동 교수님', '교수'), light=True,
                 top='<div class="mk-course"><small>← 나의 강의실 · 2025학년도 2학기</small><b>창의코딩-모두의웹</b></div><div class="mk-tabs mk-pill" style="margin:0 6px 6px"><button type="button" class="on">AI 조교</button><button type="button">코스웨어</button></div>',
                 mid=mid + '<span class="mk-grp">대화내역</span>' + ''.join(f'<span class="mk-hist">{x}</span>' for x in HIST))
        return h
    Q = '올린 자료로 쉬운 단답식 3개와 어려운 객관식 2개를 만들어 줘'
    def chat(answered, goal):
        hid = '' if answered else ' hidden'
        hello = '' if answered else ('<div class="mk-hello" data-hello><b>강의 준비에 필요한 <span style="color:var(--mk)">자료를 생성해 보세요</span></b><span>업로드한 강의 자료를 바탕으로 AI가 시험 문제, 수업 자료 등을 만들어 드립니다.</span>'
                                    '<div class="mk-chips"><button type="button" data-show="[data-guide]">' + ic('help', 14) + ' 더 똑똑한 문제 생성 가이드</button><button type="button" data-fill="' + Q + '">예시 요청 넣기</button></div>'
                                    '<p class="mk-note" data-guide hidden><span>문제의 형식·난이도·개수를 함께 알려 주면 더 좋은 문항을 만들 수 있어요. 강의 자료를 먼저 첨부하면 그 자료를 근거로 만들어요. 여러 파일과 이미지를 함께 첨부하거나 끌어다 놓아도 돼요.</span></p></div>')
        body = (demo(Q) + '<p><b>[객관식 · 어려움]</b> 다음 설명 중 \'과제별 특성 반영\' 기준에 해당하는 것을 고르세요.</p><p>A. 반복 없이 다양한 표현을 사용했다.<br>B. 서론-본론-결론이 명확하고 연결이 자연스럽다.<br>C. 문법적 오류가 적고 문장이 명확하다.<br>D. 논설문은 설득력, 설명문은 정보의 정확성과 다양성을 평가한다.</p><p><b>정답: D</b></p>'
                '<p class="mk-ref">요청하신 쉬운 단답형 3개 + 어려운 객관식 2개 조건에 맞춰 만들었습니다. 같은 기준으로 더 만들어 드릴까요?</p>')
        src = (f'<div class="mk-block" data-a{hid}><div class="mk-row"><span class="mk-lbl">원본 출처</span><span class="mk-pills"><button type="button" data-show="[data-copied]">복사</button><button type="button" data-show="[data-saved]">파일로 저장</button></span></div>'
               f'<div class="mk-rowbtn" style="cursor:default"><span><span class="mk-filechip">{ic("doc", 14)}pro16_영작 평가 기준 안내.pdf</span></span><button type="button" class="mk-btn sm line" data-show="[data-open]"{" data-goal" if goal == "src" else ""}>열기</button></div>'
               '<div class="mk-paper" data-open hidden><div class="mk-row"><b>pro16_영작 평가 기준 안내.pdf</b><span class="mk-badge">원본 문서</span></div><div class="mk-sheet"><p><b>영작 평가 기준</b></p><p>1. 과제별 특성 반영 — 논설문은 설득력, 설명문은 정보의 정확성과 다양성을 평가한다.</p><p>2. 구성 — 서론·본론·결론의 연결이 자연스러운지 본다.</p></div><p class="mk-ref">답변의 근거가 된 원본 문서가 오른쪽에 펼쳐져요.</p></div>'
               + toast('data-copied', '답변을 복사했어요.') + toast('data-saved', '답변을 파일로 저장했어요. (체험판에서는 파일이 만들어지지 않아요)') + '</div>')
        main = (f'<div class="mk-log" id="mklog">{hello}{me(Q if answered else "", "data-qa" + hid)}{dots()}{ai(body, "data-a" + hid)}{src}</div>'
                + inbar(Q, '메시지를 입력하세요…', goal == 'ask', pre=f'<span class="mk-ghost" title="강의 자료 첨부">{ic("clip", 16)}</span>', post='<span class="mk-chip" style="align-self:center">MODEL GPT 5.2</span>'))
        return frame(TH, sd('new'), ('AI 조교', '새로운 대화'), main)
    def srcdoc():
        F = [('1주차_웹의 이해.pdf', 'PDF', '2.1 MB', '업로드'), ('2주차_HTML 기초.pptx', 'PPT', '4.8 MB', '업로드'), ('강의영상_3주차.mp4', '영상', '182 MB', '업로드')]
        main = ('<div class="mk-row"><div class="mk-h"><h3>소스 문서 관리</h3></div><button type="button" class="mk-btn" data-show="[data-up]" data-goal>' + ic('down', 14) + '소스 문서 업로드</button></div>'
                '<p class="mk-ref">「소스 문서」는 챗봇이 답할 때 참고하는 모든 문서예요. 수업 자료와 강의 영상을 직접 올리고, 스마트리드 자료와 공지사항은 골라서 동기화할 수 있어요(개발 예정).</p>'
                '<div class="mk-tabs mk-pill"><button type="button" class="on" data-on>직접 업로드</button><button type="button" data-on>스마트리드 자료</button><button type="button" data-on>스마트리드 공지사항</button></div>'
                '<table class="mk-tbl"><tr><th>파일명</th><th>형식</th><th>크기</th><th>방식</th></tr>' + ''.join(f'<tr><td><b>{n}</b></td><td>{t}</td><td>{z}</td><td>{w}</td></tr>' for n, t, z, w in F)
                + '<tr data-up hidden><td><b>4주차_CSS 레이아웃.pdf</b></td><td>PDF</td><td>3.2 MB</td><td><span class="mk-st">학습 완료</span></td></tr></table>'
                + toast('data-up', '「4주차_CSS 레이아웃.pdf」를 올렸어요. 이제 챗봇이 이 자료를 근거로 답해요.'))
        return frame(TH, sd('src'), ('AI 조교', '소스 문서 관리'), main)
    QS = [('객관식', '어려움', "JavaScript에서 흔히 사용하는 'Mark-and-Sweep' 방식의 가비지 컬렉션에 대한 설명으로 옳은 것을 고르시오.", '2026.04.14'),
          ('객관식', '쉬움', 'HTML에서 attribute(속성)에 대한 올바른 설명은 무엇인가?', '2026.04.24'),
          ('객관식', '쉬움', '다음 중 창의적인 프론트엔드 디자인에서 색상, 글꼴, 배치를 담당하는 기술은 무엇입니까?', '2026.04.14'),
          ('객관식', '보통', 'HTML, CSS, JavaScript 중 HTML의 주된 역할을 가장 적절하게 설명한 것은 무엇인가?', '2026.04.24')]
    def gen():
        main = ('<div class="mk-row"><div class="mk-h"><h3>문제생성</h3></div></div><div class="mk-box"><div class="mk-two"><div class="mk-f">문제 형식<div class="mk-seg" data-ft><button type="button" data-on>객관식</button><button type="button" data-on>OX형</button><button type="button" data-on>단답형</button><button type="button" data-on>서술형</button></div></div>'
                '<div class="mk-f">난이도<div class="mk-seg" data-dl><button type="button" data-on>쉬움</button><button type="button" data-on>보통</button><button type="button" data-on>어려움</button></div></div></div>'
                '<div class="mk-two"><label class="mk-f">문항 수<select><option>3개</option><option selected>5개</option><option>10개</option></select></label><label class="mk-f">키워드<input class="mk-in" value="CSS 박스 모델" aria-label="키워드"></label></div>'
                '<p class="mk-demo" data-need hidden>문제 형식과 난이도를 하나씩 골라 주세요.</p><div class="mk-row end"><button type="button" class="mk-btn" data-allon="[data-ft],[data-dl]" data-wait="[data-gw]" data-show="[data-gq]" data-goal>바로 생성</button></div></div>'
                '<p class="mk-note" data-gw hidden>' + ic('gear', 15) + '<span>문제를 만들고 있어요…</span></p>'
                '<div class="mk-box" data-gq hidden><div class="mk-row"><b>생성된 문제 <small>5건</small></b><span class="mk-row"><span class="mk-btn sm line" style="cursor:default">문항 수정</span><span class="mk-btn sm dark" style="cursor:default">미등록 5건 일괄 등록</span></span></div>'
                '<p><b>Q1.</b> CSS 박스 모델에서 요소의 테두리 바깥쪽 여백을 정하는 속성은?</p><p class="mk-opt on" style="cursor:default">margin</p><p class="mk-ref">한 문항씩 검토하고, 「미등록 문제 일괄 등록」을 누르면 문제은행에 한꺼번에 저장돼요.</p></div>')
        return frame(TH, sd('exam', 'gen'), ('AI 조교', '문제생성'), main)
    def bank():
        rows = ''.join(f'<tr data-on><td><span class="mk-cb"></span></td><td>{t}</td><td style="color:{"#dc2626" if d == "어려움" else ("#16a34a" if d == "쉬움" else "#2563eb")}">{d}</td><td>{q}</td><td>{dt}</td></tr>' for t, d, q, dt in QS)
        main = ('<div class="mk-row"><div class="mk-h"><h3>문제은행 <span style="color:var(--mk)">34개의 문제</span></h3></div><span class="mk-row"><span class="mk-btn sm line" style="cursor:default">문제 불러오기</span><span class="mk-btn sm line" style="cursor:default">직접 생성</span></span></div>'
                '<div class="mk-bar"><select aria-label="문제유형"><option>문제유형 전체</option></select><select aria-label="난이도"><option>문항 난이도 전체</option></select><label class="mk-search">' + ic('search', 15) + '<input type="search" placeholder="질문/정답/해설 검색" aria-label="검색" autocomplete="off"></label></div>'
                '<div class="mk-quad3" style="grid-template-columns:minmax(0,1.5fr) minmax(0,1fr)"><table class="mk-tbl" data-pick><tr><th></th><th>유형</th><th>난이도</th><th>문항</th><th>등록일</th></tr>' + rows + '</table>'
                '<div class="mk-box"><div class="mk-row"><b>시험지 미리보기</b><span class="mk-chip">보관함 3</span></div><label class="mk-f">시험지 제목 *<input class="mk-in" id="mkexam" placeholder="예: 2학기 중간고사" aria-label="시험지 제목"></label>'
                '<p class="mk-ref">왼쪽에서 문항을 누르면 「시험지에 추가」돼요. 배점은 직접 쓰거나 「균등배점」을 켜면 자동으로 들어가요.</p>'
                '<div class="mk-row"><span class="mk-row"><span class="mk-tgl"></span><small>균등배점</small></span><b>총점 100점</b></div>'
                '<p class="mk-demo" data-need hidden>문항을 하나 이상 고르고 시험지 제목을 써 주세요.</p>'
                '<div class="mk-row end"><span class="mk-btn sm line" style="cursor:default">PDF 시험지 생성</span><button type="button" class="mk-btn sm dark" data-allon="[data-pick]" data-req="#mkexam" data-show="[data-qz]" data-goal>퀴즈 생성</button></div>'
                + toast('data-qz', '퀴즈를 만들었어요. 「퀴즈 관리」에서 공개 여부와 일정을 정할 수 있어요.') + '</div></div>')
        return frame(TH, sd('exam', 'bank'), ('AI 조교', '문제은행'), main)
    def quiz():
        main = ('<div class="mk-h"><h3>퀴즈 관리</h3></div><table class="mk-tbl"><tr><th>퀴즈명</th><th>문항</th><th>공개</th><th>응시 기간</th></tr>'
                '<tr><td><b>2학기 중간 퀴즈</b></td><td>4</td><td><button type="button" class="mk-btn sm line" data-set="[data-pub]|공개" data-show="[data-sch]" data-goal><span data-pub>비공개</span></button></td><td><span data-sch hidden>2026.10.20 09:00 ~ 10.22 23:59</span></td></tr>'
                '<tr><td>1주차 퀴즈</td><td>5</td><td><span class="mk-st">공개</span></td><td>2026.09.03 ~ 09.05</td></tr></table>'
                '<div class="mk-box" data-sch hidden><b>퀴즈 일정 편집</b><div class="mk-two"><label class="mk-f">시작일<input class="mk-in" value="2026-10-20 09:00" aria-label="시작일"></label><label class="mk-f">종료일<input class="mk-in" value="2026-10-22 23:59" aria-label="종료일"></label></div><p class="mk-ref">정한 시작 일시부터 종료 일시까지 수강생이 퀴즈에 응시할 수 있어요.</p></div>')
        return frame(TH, sd('exam', 'quiz'), ('AI 조교', '퀴즈 관리'), main)
    def grade():
        R = [('창의코딩_1주차 퀴즈(학생 A)', '0.93', '30점'), ('창의코딩_1주차 퀴즈(학생 B)', '0.95', '40점'), ('창의코딩_1주차 퀴즈(학생 C)', '0.89', '50점')]
        rows = ''.join(f'<tr><td><b>{n}</b></td><td>5</td><td>{o}</td><td>{sc}</td><td><span class="mk-st">채점 완료</span></td><td>' + (f'<button type="button" class="mk-btn sm line" data-show="[data-sheet]" data-goal>시험지 열기</button>' if k == 0 else '<span class="mk-chip">시험지 열기</span>') + '</td></tr>' for k, (n, o, sc) in enumerate(R))
        main = ('<div class="mk-h"><h3>시험지 채점</h3></div><p class="mk-ref">학생 시험지를 골라 OCR 결과를 검수하고 채점 현황을 빠르게 확인할 수 있어요.</p>'
                '<div class="mk-stats"><div class="mk-stat"><small>응시자 수</small><b>3명</b></div><div class="mk-stat"><small>평균 점수</small><b>40.00점</b></div><div class="mk-stat"><small>최고 / 최저 점수</small><b>50점 / 30점</b></div></div>'
                '<div class="mk-row"><small>● 신뢰도 높음 ● 정확도 낮음 — OCR 정확도가 낮으면 재검수·재채점을 권장해요.</small><span class="mk-btn sm dark" style="cursor:default">학생 시험지 업로드 →</span></div>'
                '<table class="mk-tbl"><tr><th>시험지명(학생명)</th><th>문항수</th><th>OCR 신뢰도</th><th>채점 결과</th><th>상태</th><th></th></tr>' + rows + '</table>'
                '<div class="mk-two" data-sheet hidden><div class="mk-sheet"><p><b>학생 시험지 (스캔)</b></p><p>1. margin ✔</p><p>2. ② CSS ✔</p><p>3. &lt;head&gt; ✘</p></div><div class="mk-box"><b>문항 상세 · 채점 근거</b><p><b>3번</b> 답안 「&lt;head&gt;」 → 0점</p><p class="mk-ref">근거: 해설에 따라 &lt;body&gt; 태그만 정답으로 인정. OCR 인식이 틀렸다면 여기서 직접 고쳐 다시 채점할 수 있어요.</p></div></div>')
        return frame(TH, sd('exam', 'grade'), ('AI 조교', '시험지 채점'), main)
    def stu():
        main = ('<div class="mk-h"><h3>수강생 관리</h3></div><div class="mk-tabs"><button type="button" class="on" data-on data-hide="[data-qh]" data-show="[data-ph]">학습자 예습 · 복습 이력</button><button type="button" data-on data-hide="[data-ph]" data-show="[data-qh]" data-goal>학습자 퀴즈 이력</button><button type="button" data-on>대시보드</button></div>'
                '<table class="mk-tbl" data-ph><tr><th>학생</th><th>예습</th><th>복습</th><th>AI 튜터 질문</th></tr><tr><td>학생 A</td><td>5회</td><td>3회</td><td>12회</td></tr><tr><td>학생 B</td><td>2회</td><td>1회</td><td>4회</td></tr></table>'
                '<table class="mk-tbl" data-qh hidden><tr><th>학생</th><th>1주차 퀴즈</th><th>중간 퀴즈</th><th>제출</th></tr><tr><td>학생 A</td><td>80점</td><td>-</td><td><span class="mk-st">제출</span></td></tr><tr><td>학생 B</td><td>60점</td><td>-</td><td><span class="mk-st ing">미제출</span></td></tr></table>'
                '<p class="mk-ref">수강생이 AI 튜터로 얼마나 예습·복습하는지, 퀴즈에 참여했는지와 성적까지 한눈에 볼 수 있어요.</p>')
        return frame(TH, sd('stu'), ('AI 조교', '수강생 관리'), main)
    I = 'media/walk/hai-tutor/'
    return [
        dict(title='사번으로 로그인해요', text='별도 회원가입 없이 ○○대학교 사번 ID와 비밀번호로 로그인해요. 아이디 저장 기능도 있어요. (매뉴얼 01)', do='「통합 로그인」 단추를 눌러 로그인해 보세요.', img=I + 'm1.jpg',
             ui=login(TH, ('UNIVERSITY AI TEACHING ASSISTANT', '교수 활동 지원 시스템', '검색부터 자료 생성까지 모두 가능한 AI 조교와의 대화를 시작해 보세요.', ['AI Chat', 'Lecture Prep', 'Smart Assist']),
                      ('SECURE ACCESS', 'Sign in'), [('아이디', '아이디', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', False, False), ('통합 로그인', True, True)])),
        dict(title='자료를 첨부하고 대화를 시작해요', text='입력창 왼쪽 첨부 단추로 강의 자료·이미지를 여러 개 올리면 그 자료를 근거로 답해요. 「더 똑똑한 문제 생성 가이드」로 요청 요령도 볼 수 있어요. (매뉴얼 02)', do='입력창에 요청을 쓰고 보내 보세요. 비워 둔 채 보내면 예시 요청이 입력돼요.', ui=chat(False, 'ask'), img=I + 'm2.jpg'),
        dict(title='답변의 출처를 확인해요', text='답변 아래에 근거가 된 원본 자료가 표시돼요. 「열기」를 누르면 출처 문서가 오른쪽에 펼쳐지고, 답변은 복사하거나 파일로 저장할 수 있어요. (매뉴얼 02 · 답변의 출처 표기)', do='원본 출처의 「열기」를 눌러 보세요.', ui=chat(True, 'src'), img=I + 'm3.jpg'),
        dict(title='소스 문서를 올려요', text='챗봇이 참고할 수업 자료·강의 영상을 「소스 문서 관리」에 올려 두면, 대화할 때마다 그 자료를 근거로 답해요. (매뉴얼 03)', do='「소스 문서 업로드」를 눌러 강의 자료를 올려 보세요.', ui=srcdoc(), img=I + 'm4.jpg'),
        dict(title='조건을 정해 문제를 생성해요', text='[문제출제 및 시험관리 > 문제생성]에서 형식·난이도·개수와 키워드를 정하고 [바로 생성]을 눌러요. 한 문항씩 검토하고 문제은행에 일괄 등록해요. (매뉴얼 06 · 문제생성)', do='문제 형식과 난이도를 하나씩 고른 뒤 「바로 생성」을 눌러 보세요.', ui=gen(), img=I + 'm5.jpg'),
        dict(title='문제은행에서 시험지·퀴즈를 만들어요', text='문제은행에서 문항을 골라 「시험지에 추가」하고 시험지 제목과 배점을 정해요. PDF 시험지로 내려받거나 [퀴즈 생성]으로 퀴즈를 만들어요. (매뉴얼 06 · 문제은행)', do='문항을 하나 이상 누르고 시험지 제목을 쓴 뒤 「퀴즈 생성」을 눌러 보세요.', ui=bank(), img=I + 'm6.jpg'),
        dict(title='퀴즈를 공개하고 일정을 정해요', text='[퀴즈 관리]에서 퀴즈의 공개 여부를 켜고 시작·종료 일시를 정하면, 그 기간 동안 수강생이 응시할 수 있어요. (매뉴얼 06 · 퀴즈 현황)', do='「2학기 중간 퀴즈」의 공개 단추를 눌러 보세요.', ui=quiz(), img=I + 'm7.jpg'),
        dict(title='종이 시험지를 OCR로 채점해요', text='학생 시험지를 올리면 바로 OCR 채점이 진행돼요. OCR 신뢰도와 점수를 보고, [시험지 열기]로 원본과 채점 근거를 비교하며 직접 고칠 수 있어요. (매뉴얼 06 · 시험지 채점)', do='첫 번째 시험지의 「시험지 열기」를 눌러 보세요.', ui=grade(), img=I + 'm8.jpg'),
        dict(title='수강생 학습 현황을 봐요', text='[수강생 관리]에서 학생별 AI 튜터 예습·복습 이력과 퀴즈 참여·성적, 활용 빈도 대시보드를 확인해요. (매뉴얼 05)', do='「학습자 퀴즈 이력」 탭을 눌러 보세요.', ui=stu(), img=I + 'm9.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Mate (학생용 매뉴얼)
def _mate():
    # 2026학년도 2학기 교수자·학생 사용 매뉴얼(창의코딩파이썬-1 기준 화면)을 그대로 따라 만든 화면
    TH = '--mk:#2563eb;--mk-side:#0b2a66'
    PRO = [('mat', 'doc', '자료 관리'), ('gen', 'edit', '문제 생성'), ('pre', 'check', '예복습 문제'), ('quiz', 'chart', '퀴즈'), ('stu', 'user', '수강생 관리')]
    STU = [('chat', 'chat', '챗봇 튜터'), ('lib', 'doc', '학습 자료'), ('pre', 'check', '예복습 문제'), ('quiz', 'chart', '퀴즈')]
    def sd(active, prof=True, go=None):
        return side('HAI-Mate', '', [('', PRO if prof else STU)], active, user=('AIED 교수 1' if prof else 'AIED 학생 1', '교수자' if prof else '학생'), light=True, go=go or {},
                    top='<div class="mk-course"><small>2026학년도 2학기</small><b>창의코딩파이썬-1</b></div>')
    def lg():
        return login(TH, ('○○ UNIVERSITY AI TEACHING SYSTEM', '교수 활동 지원 시스템', 'HAI-Mate와 함께 강의 자료 관리부터 문제 생성·배포·학습 결과 확인까지 한곳에서.', ['자료 관리', '문제 생성', '퀴즈', '수강생 관리']),
                     ('HAI-Mate', 'Sign in'), [('아이디', '아이디', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', False, False), ('○○대 통합 로그인', True, True)],
                     done='로그인했어요. 학년도·학기를 확인하고 강좌의 [바로가기]를 누르면 「자료 관리」 화면이 열려요.')
    FILES = [('c9장_배열.pptx', '9주차', 'HAI-Mate', '5.93 MB', 'PPT', False), ('byte_of_python_5장.pdf', '공통', 'HAI-Mate', '2.13 MB', 'PDF', True), ('파이썬_기초문법.pdf', '공통', '스마트리드', '267.95 KB', 'PDF', False)]
    def mat():
        rows = ''.join(f'<tr><td><span class="mk-cb"></span></td><td><b>{n}</b></td><td><span class="mk-chip">{w}</span></td><td><span class="mk-chip">{src}</span></td><td>{sz}</td><td><span class="mk-file {t.lower()}">{ic("doc", 14)}</span></td>'
                       f'<td>{"<span class=mk-st>배포</span>" if on else (chr(60) + "button type=button class=" + chr(34) + "mk-btn sm line" + chr(34) + " data-set=" + chr(34) + "[data-dist]|배포" + chr(34) + " data-hide=[data-undist] data-show=[data-distok] data-goal><span data-dist>비공개</span></button>" if n.startswith("파이썬") else "<span class=mk-chip>비공개</span>")}</td></tr>'
                       for n, w, src, sz, t, on in FILES)
        main = ('<div class="mk-h"><h3>자료 관리</h3></div><div class="mk-bar"><label class="mk-search">' + ic('search', 15) + '<input type="search" placeholder="검색어 입력" aria-label="검색어" autocomplete="off"></label>'
                '<span class="mk-row"><button type="button" class="mk-btn sm line">' + ic('down', 14) + '업로드</button><span class="mk-btn sm soft" style="cursor:default">주차 수정</span><span class="mk-btn sm soft" style="cursor:default">삭제</span><span class="mk-btn sm soft" style="cursor:default">다운로드</span></span></div>'
                '<table class="mk-tbl"><tr><th></th><th>파일명</th><th>주차</th><th>출처</th><th>크기</th><th>형식</th><th>학생 배포</th></tr>' + rows + '</table>'
                '<p class="mk-ref">스마트리드에 올린 자료는 자동으로 불러오고, 출처에 [스마트리드]로 표시돼요. 상태가 「완료」인 자료는 문제 생성의 소스 자료로 쓸 수 있어요.</p>'
                + toast('data-distok', '「파이썬_기초문법.pdf」를 학생에게 공개했어요. 학생 화면의 「학습 자료」에 나타나요.'))
        return frame(TH, sd('mat'), ('HAI-Mate', '자료 관리'), main)
    WEEKS = [('9주차', '출제완료', '완료'), ('10주차', '출제완료', '완료'), ('11주차', '미작성', '미완료'), ('12주차', '미작성', '미완료')]
    LOS = ['파이썬에서 주석을 사용하여 코드의 의도를 설명할 수 있다.', '리터럴 상수와 변수의 차이를 설명하고 이를 사용하여 코드를 작성할 수 있다.', '파이썬의 문자열 포맷팅 기능을 활용하여 다양한 형식의 문자열을 생성할 수 있다.', '다양한 편집기를 사용하여 파이썬 프로그램을 작성하고 실행할 수 있다.']
    def wk(sel):
        return ('<div class="mk-box"><b>대상 주차</b><table class="mk-tbl" data-wk><tr><th>주차</th><th>상태</th><th>예습</th><th>복습</th><th>라이브</th></tr>'
                + ''.join(f'<tr class="{"on" if (sel and w == "11주차") else ""}"{" data-on" if not sel else ""}><td><b>{w}</b></td><td><span class="mk-st{" ing" if st == "미작성" else ""}">{st}</span></td><td><span class="mk-chip">미완료</span></td><td><span class="mk-chip">미완료</span></td><td><span class="mk-st{"" if lv == "완료" else " ing"}">{lv}</span></td></tr>' for w, st, lv in WEEKS) + '</table></div>')
    def prep():
        src = ('<div class="mk-box"><div class="mk-row"><b>소스 자료</b><small>스마트리드·HAI-Mate 자료</small></div><div data-srcsel>'
               '<button type="button" class="mk-rowbtn" data-on><span><span class="mk-cb"></span> <b>byte_of_python_5장.pdf</b> <small style="display:inline">2.1 MB</small></span><span class="mk-st">완료</span></button>'
               '<button type="button" class="mk-rowbtn" data-on style="margin-top:6px"><span><span class="mk-cb"></span> <b>파이썬_기초문법.pdf</b> <small style="display:inline">268 KB</small></span><span class="mk-st">완료</span></button></div>'
               '<p class="mk-demo" data-need hidden>먼저 「11주차」 행과 소스 자료를 하나씩 눌러 골라 주세요.</p>'
               '<div class="mk-row end"><button type="button" class="mk-btn" data-allon="[data-wk],[data-srcsel]" data-show="[data-los]" data-goal>✨ 학습 목표 추출</button></div></div>')
        los = ('<div class="mk-paper" data-los hidden><div class="mk-row"><b>추출된 학습 목표</b><span class="mk-badge">AI 추출</span></div>'
               + ''.join(f'<p class="mk-rowbtn" style="cursor:default"><span><span class="mk-cb on"></span> {x}</span></p>' for x in LOS)
               + '<div class="mk-row end"><span class="mk-btn sm line" style="cursor:default">취소</span><span class="mk-btn sm" style="cursor:default">선택 항목 적용</span></div><p class="mk-ref">사용할 목표를 체크해 적용하면 오른쪽 「학습 목표」에 들어가요. 적용한 뒤에도 직접 고치거나 더할 수 있어요.</p></div>')
        main = '<div class="mk-row"><div class="mk-h"><h3>문제 생성</h3></div><span class="mk-btn sm line" style="cursor:default">문제 생성하기</span></div>' + wk(False) + src + los
        return frame(TH, sd('gen'), ('HAI-Mate', '문제 생성'), main)
    def cond():
        main = ('<div class="mk-row"><div class="mk-h"><h3>문제 생성</h3><span class="mk-badge">11주차</span></div>'
                '<button type="button" class="mk-btn" data-allon="[data-use],[data-lv]" data-wait="[data-gening]" data-show="[data-gendone]" data-goal>문제 생성하기</button></div>'
                '<div class="mk-two"><div class="mk-box"><b>문제 설정</b><div class="mk-f">용도<div class="mk-seg" data-use><button type="button" data-on>예습용</button><button type="button" data-on>복습용</button><button type="button" data-on>퀴즈</button></div></div>'
                '<div class="mk-f">난이도<div class="mk-seg" data-lv><button type="button" data-on>하</button><button type="button" data-on>중</button><button type="button" data-on>상</button></div></div>'
                '<div class="mk-two"><div class="mk-f">문제 유형<span class="mk-chip">객관식</span></div><label class="mk-f">문항 수 <b>5문항</b><input type="range" min="1" max="10" value="5" aria-label="문항 수"></label></div>'
                '<button type="button" class="mk-rowbtn" data-on><span><span class="mk-cb"></span> <b>LLM 오케스트레이션 여부</b><small>여러 AI를 함께 써서 더 꼼꼼히 만들어요. 생성 시간이 조금 더 걸릴 수 있어요.</small></span></button>'
                '<p class="mk-demo" data-need hidden>용도와 난이도를 하나씩 골라 주세요.</p></div>'
                '<div class="mk-box"><b>학습 목표</b>' + ''.join(f'<p class="mk-rowbtn" style="cursor:default"><span><span class="mk-chip">AI 추출</span> {x}</span></p>' for x in LOS[:3]) + '</div></div>'
                '<p class="mk-note" data-gening hidden>' + ic('gear', 15) + '<span>11주차 문제를 생성하고 있어요… 작업을 멈추지 말고 기다려 주세요.</span></p>'
                '<div class="mk-note" data-gendone hidden>' + ic('check', 15) + '<span>문제 생성이 끝났어요. <b>[검토하기]</b>를 누르면 문항 검토 화면으로 가요. (다음 미션)</span></div>')
        return frame(TH, sd('gen'), ('HAI-Mate', '문제 생성'), main)
    QL = ['다음 중 파이썬 주석(comment)에 대한 설명으로 옳은 것은?', "다음 중 파이썬에서 '변수(variable)'의 특징을 올바르게 설명한 것은?", "format() 메소드를 사용한 다음 코드의 결과로 옳은 것은?", "파이썬에서 '물리적 명령행'과 '논리적 명령행'의 관계에 대한…", 'PyCharm에서 예제 파이썬 프로그램을 인수와 함께 실행할 때 올바른 절차는?']
    OPT = ['주석을 작성하려면 세 개의 따옴표로 문자열 블록을 만들어야 한다.', '주석 내용은 실행 시 화면에 출력되므로 배포 전 반드시 삭제해야 한다.', "주석의 주된 목적은 코드가 '무엇'을 하는지를 상세히 기술하는 것이다.", "# 문자 뒤에 작성되며 '왜' 그 코드를 작성했는지를 설명한다."]
    EXP = "정답인 '# 문자 뒤에 작성되며 왜 그 코드를 작성했는지를 설명한다'는 근거 문헌에서 주석은 # 뒤에 오는 문장으로 작성되며, 코드는 '어떻게(how)'를 말하지만 주석은 '왜(why)'를 말해야 한다고 명시하고 있어 정확하다."
    SRC = '<div class="mk-box"><div class="mk-row"><b>출처</b><span class="mk-chip">byte_of_python_5장.pdf p.1</span></div><div class="mk-sheet"><p><b>5장. 기초</b></p><p><b>5.1 주석</b></p><p>주석은 # 문자 뒤에 따라오는 문장입니다. 주로 소스 코드를 읽는 사람들을 위해 주석을 남기는 용도로 빈번하게 사용됩니다.</p><p class="mk-code" style="min-height:0">print(\'hello world\')  # print는 함수입니다</p></div></div>'
    def review():
        lst = ''.join(f'<span class="mk-rowbtn{" on" if k == 0 else ""}" style="cursor:default"><span><b>Q{k + 1}</b> <span class="mk-chip">객관식</span> <span class="mk-chip">보통</span><br><small>{q}</small></span><span class="mk-chip" data-rv{k}>검수 대기</span></span>' for k, q in enumerate(QL))
        opts = ''.join(f'<p class="mk-opt{" on" if k == 3 else ""}" style="cursor:default">{"<b>정답</b> " if k == 3 else ""}{k + 1}. {t}</p>' for k, t in enumerate(OPT))
        main = ('<div class="mk-row"><div class="mk-h"><h3>문제 생성</h3><span class="mk-badge">검토</span></div><span class="mk-row"><span class="mk-btn sm line" style="cursor:default">문제 설정</span>'
                '<button type="button" class="mk-btn" data-set="[data-rv0]|검수 완료" data-show="[data-saved]" data-goal>저장하기</button></span></div>'
                f'<div class="mk-quad3"><div class="mk-opts">{lst}</div><div class="mk-box"><div class="mk-row"><b>Q1</b><span class="mk-chip">문항 삭제</span></div><span class="mk-lbl">문제</span><p>{QL[0]}</p><span class="mk-lbl">문항 · 정답</span><div class="mk-opts">{opts}</div>'
                f'<span class="mk-lbl">해설</span><p>{EXP}</p><div class="mk-row"><input class="mk-in" placeholder="✨ AI에게 수정 요청 — 예: 보기 ③을 더 헷갈리게" aria-label="AI 수정 요청"><span class="mk-btn sm line" style="cursor:default">AI 수정</span></div></div>{SRC}</div>'
                + toast('data-saved', '5개 문항을 저장했어요. 예습·복습 문제는 「예복습 문제」 목록으로, 퀴즈는 「퀴즈 > 문제 관리」로 옮겨져요.'))
        return frame(TH, sd('gen'), ('HAI-Mate', '문제 검토'), main)
    def dist():
        main = ('<div class="mk-row"><div class="mk-h"><h3>문제 배포</h3></div><span class="mk-chip">예복습 문제 › 문제 배포</span></div>'
                '<div class="mk-box"><div class="mk-two"><label class="mk-f">주차<select><option>11주차</option><option>10주차</option></select></label><div class="mk-f">구분<div class="mk-seg"><button type="button" class="on" data-on>예습</button><button type="button" data-on>복습</button></div></div></div>'
                '<div class="mk-two"><label class="mk-f">공개 시작<input class="mk-in" type="text" value="2026-11-09 09:00" aria-label="공개 시작"></label><label class="mk-f">공개 종료<input class="mk-in" type="text" value="2026-11-15 23:59" aria-label="공개 종료"></label></div>'
                '<table class="mk-tbl"><tr><th>배포</th><th>문항</th><th>유형</th><th>난이도</th></tr>' + ''.join(f'<tr><td><span class="mk-cb on"></span></td><td>Q{k + 1}. {q}</td><td>객관식</td><td>보통</td></tr>' for k, q in enumerate(QL[:3])) + '</table>'
                '<div class="mk-row end"><button type="button" class="mk-btn" data-set="[data-dst]|배포 중" data-show="[data-dok]" data-goal>배포</button></div></div>'
                '<table class="mk-tbl"><tr><th>주차</th><th>구분</th><th>문항 수</th><th>공개 기간</th><th>상태</th></tr><tr><td>11주차</td><td>예습</td><td>5</td><td>11.09 ~ 11.15</td><td><span class="mk-st ing" data-dst>배포 전</span></td></tr></table>'
                + toast('data-dok', '11주차 예습이 「배포 중」이 되었어요. 학생의 「예복습 문제」 목록에 바로 나타나요.'))
        return frame(TH, sd('pre'), ('HAI-Mate', '문제 배포'), main)
    def solve():
        opts = ''.join(f'<button type="button" class="mk-opt" data-on>{k + 1}. {t}</button>' for k, t in enumerate(OPT))
        main = ('<div class="mk-row"><div class="mk-h"><h3>← 11주차 예습</h3></div><span class="mk-row"><small>정답 확인 0/5</small><span class="mk-btn sm soft" style="cursor:default">제출 (0/5)</span></span></div>'
                '<div class="mk-pills"><span class="on">1</span><span>2</span><span>3</span><span>4</span><span>5</span></div>'
                f'<div class="mk-two"><div class="mk-box"><span class="mk-chip">문제 1</span><p><b>Q. {QL[0]}</b></p><div class="mk-opts" id="mko">{opts}</div>'
                '<p class="mk-demo" data-need hidden>먼저 답을 하나 골라 주세요.</p><div class="mk-box tint" data-right hidden><b>정답이에요! (정답 4번)</b><span>' + EXP + '</span></div><div class="mk-box tint" data-wrong hidden><b>아쉬워요. 정답은 4번이에요.</b><span>' + EXP + '</span></div>'
                '<div class="mk-row end"><button type="button" class="mk-btn" data-check="#mko|3" data-goal>정답 확인</button></div></div>' + SRC + '</div>'
                '<p class="mk-ref">문항 번호를 눌러 남은 문제도 같은 방식으로 풀고, 정답 확인 수가 전체 문항 수와 같아지면 [제출]이 열려요.</p>')
        return frame(TH, sd('pre', False), ('HAI-Mate', '예습·복습 문제 풀이'), main)
    def live():
        ST = [('aied_st1', 'AIED 학생 1', '제출'), ('aied_st2', 'AIED 학생 2', '제출'), ('aied_st3', 'AIED 학생 3', '미제출')]
        main = ('<div class="mk-row"><div class="mk-h"><h3>퀴즈 배포</h3><span class="mk-badge">11주차 · 5문항 선별됨</span></div><span class="mk-st ing" data-qst>배포전</span></div>'
                '<div class="mk-box"><div class="mk-f">배포 방식<div class="mk-seg"><button type="button" class="on" data-on>라이브 배포</button><button type="button" data-on>예약 배포</button></div></div>'
                '<div class="mk-row end"><button type="button" class="mk-btn" data-set="[data-qst]|진행 중" data-show="[data-live]" data-goal>▶ 라이브 시작</button></div></div>'
                '<div class="mk-box" data-live hidden><div class="mk-row"><b>참여 현황 <small>참여 3명 · 제출 2명</small></b><div class="mk-tabs"><button type="button" class="on" data-filter="all" data-on>전체</button><button type="button" data-filter="제출" data-on>제출</button><button type="button" data-filter="미제출" data-on>미제출</button></div></div>'
                '<table class="mk-tbl"><tr><th>학번</th><th>이름</th><th>제출 여부</th></tr>' + ''.join(f'<tr data-cat="{st}"><td>{i}</td><td>{n}</td><td><span class="mk-st{"" if st == "제출" else " ing"}">{st}</span></td></tr>' for i, n, st in ST) + '</table>'
                '<p class="mk-ref">학생은 「퀴즈」에서 진행 중인 퀴즈에 들어가 답을 고르고 [제출]해요. 종료하면 상태가 「종료」로 바뀌고, 그 뒤에도 학생별 제출 여부를 볼 수 있어요.</p></div>')
        return frame(TH, sd('quiz'), ('HAI-Mate', '퀴즈 배포'), main)
    def grade():
        OX = [('aied_st3', 'AIED 학생 3', '-----'), ('aied_st1', 'AIED 학생 1', 'OOXOO'), ('aied_st2', 'AIED 학생 2', 'OOOOO')]
        cell = lambda s: '<span class="mk-ox">' + ''.join(f'<i><small>{k + 1}</small>{c}</i>' for k, c in enumerate(s)) + '</span>'
        main = ('<div class="mk-h"><h3>수강생 관리</h3></div><div class="mk-bar"><label class="mk-search">' + ic('search', 15) + '<input type="search" placeholder="학번 또는 이름 검색" aria-label="학번 또는 이름" autocomplete="off"></label>'
                '<select aria-label="주차"><option>11주차</option><option>10주차</option></select><select aria-label="위험도"><option>위험도: 전체</option><option>위험</option><option>주의</option></select>'
                '<button type="button" class="mk-btn sm line" data-show="[data-xl]" data-goal>' + ic('down', 14) + '엑셀 다운로드</button></div>'
                '<table class="mk-tbl"><tr><th>No</th><th>학번</th><th>이름</th><th>주차</th><th>예습</th><th>복습</th></tr>' + ''.join(f'<tr><td>{k + 1}</td><td>{i}</td><td>{n}</td><td>11주차</td><td>{cell(o)}</td><td><span class="mk-chip">배포 없음</span></td></tr>' for k, (i, n, o) in enumerate(OX)) + '</table>'
                '<p class="mk-ref">정답은 O, 오답은 X로 표시돼요. 아직 풀지 않은 문항은 - 로 보여요.</p>' + toast('data-xl', '정오표를 엑셀 파일로 받았어요. (체험판이라 파일은 만들어지지 않아요)'))
        return frame(TH, sd('stu'), ('HAI-Mate', '수강생 관리'), main)
    I = 'media/walk/hai-mate/'
    return [
        dict(title='로그인하고 강좌로 들어가요', text='아이디·비밀번호 또는 학교 통합 로그인으로 들어가요. 학년도·학기를 확인하고 강좌의 [바로가기]를 누르면 그 강좌의 「자료 관리」 화면과 왼쪽 메뉴가 열려요. (교수자 매뉴얼 1)', do='「○○대 통합 로그인」을 눌러 보세요.', ui=lg(), img=I + 'm1.jpg'),
        dict(title='학습 자료를 관리해요', text='문제 생성과 학생 학습에 쓸 PDF·PPT 자료를 올리고, 주차와 출처, 학생 배포 상태를 관리해요. 「학생 배포」 단추로 학생 공개 여부를 바꿔요. (교수자 매뉴얼 2)', do='「파이썬_기초문법.pdf」의 학생 배포 단추를 눌러 학생에게 공개해 보세요.', ui=mat(), img=I + 'm2.jpg'),
        dict(title='대상 주차와 소스 자료로 학습 목표를 뽑아요', text='[문제 생성]에서 대상 주차를 고르고 소스 자료를 체크한 뒤 [학습 목표 추출]을 누르면 AI가 자료에서 학습 목표를 뽑아 줘요. 쓸 목표를 골라 적용해요. (교수자 매뉴얼 3)', do='대상 주차에서 「11주차」, 소스 자료에서 PDF 하나를 누른 뒤 「학습 목표 추출」을 눌러 보세요.', ui=prep(), img=I + 'm3.jpg'),
        dict(title='문제 조건을 정하고 AI로 생성해요', text='용도(예습용·복습용·퀴즈), 난이도, 문항 수를 정하고 필요하면 「LLM 오케스트레이션」을 켠 뒤 [문제 생성하기]를 눌러요. 생성이 끝나면 [검토하기]가 나타나요. (교수자 매뉴얼 4·5)', do='용도 「예습용」과 난이도를 하나씩 고른 뒤 「문제 생성하기」를 눌러 보세요.', ui=cond(), img=I + 'm4.jpg'),
        dict(title='생성된 문항을 검토하고 저장해요', text='문항·보기·정답·해설을 오른쪽 출처 PDF와 함께 검토해요. 직접 고치거나 「AI에게 수정 요청」을 쓴 뒤, 검수가 끝나면 [저장하기]를 눌러요. (교수자 매뉴얼 6)', do='문항과 출처를 살펴본 뒤 「저장하기」를 눌러 보세요.', ui=review(), img=I + 'm5.jpg'),
        dict(title='예습 문제를 배포해요', text='[예복습 문제] > [문제 배포]에서 주차와 예습·복습을 고르고, 배포할 문항과 공개 기간을 정해 배포해요. 상태가 「배포 중」이면 학생 목록에 나타나요. (교수자 매뉴얼 7)', do='공개 기간을 확인하고 「배포」를 눌러 보세요.', ui=dist(), img=I + 'm6.jpg'),
        dict(title='학생은 풀고 바로 정답을 확인해요', text='학생은 [예복습 문제]에서 공개된 문제를 골라 답을 고르고 [정답 확인]으로 정오·해설·출처를 바로 봐요. 모든 문항을 확인하면 제출해요. (학생 매뉴얼 4·5)', do='보기 가운데 답을 하나 고르고 「정답 확인」을 눌러 보세요.', ui=solve(), img=I + 'm7.jpg'),
        dict(title='퀴즈를 라이브로 진행해요', text='고른 퀴즈 문항은 [퀴즈 배포]에서 라이브로 바로 시작하거나 예약해 공개해요. 진행 중에는 참여 인원과 학생별 제출 여부를 실시간으로 봐요. (교수자 매뉴얼 8·9)', do='「라이브 시작」을 눌러 퀴즈를 시작해 보세요.', ui=live(), img=I + 'm8.jpg'),
        dict(title='수강생 학습 결과를 확인해요', text='[수강생 관리]에서 주차와 위험도를 골라 학생별 예습·복습 제출과 문항별 정오표(O/X)를 봐요. 학번·이름으로 찾거나 엑셀로 내려받을 수 있어요. (교수자 매뉴얼 10)', do='「엑셀 다운로드」를 눌러 정오표를 받아 보세요.', ui=grade(), img=I + 'm9.jpg'),
    ]

EG = '<span class="mk-eg">체험용 예시 답변</span>'

# ------------------------------------------------------------------ HAI-GPT (빠른 시작 안내)
def _gpt():
    TH = '--mk:#6d3fe0;--mk-side:#2a1a66'
    HIST = ['첨부된 견적서의 서비스의…', 'RAG 기반 LLM 챗봇 설계…', '오늘의 날씨 정보 확인 및 조회', '프로그래밍 조건문의 개념과…']
    def sd():
        return side('HAI-GPT', '', [('', [('new', 'chat', '새 채팅'), ('stu', 'edit', '스튜디오'), ('sto', 'mark', '스토어'), ('prj', 'doc', '프로젝트')]),
                                    ('에이전트', [('dr', 'search', 'Deep Research'), ('kd', 'chart', 'Korea in Data'), ('ld', 'shield', 'Law in Data'), ('im', 'edit', '이미지 생성'), ('vd', 'send', '비디오 생성'), ('pt', 'doc', '프레젠테이션'), ('vo', 'bell', '음성 대화'), ('mt', 'doc', '회의록')])],
                    'new', go={'new': 1}, light=True, mid='<span class="mk-grp">내 채팅 내역</span>' + ''.join(f'<span class="mk-hist">{h}</span>' for h in HIST))
    def top(agent, goal=False):
        return ('<div class="mk-topbar"><div class="mk-pills" title="모델 선택"><button type="button" class="' + ('' if agent else 'on') + '" data-on data-hide="[data-sa]" data-show="[data-nm]">Grok 4.1 Fast</button>'
                '<button type="button" class="' + ('on' if agent else '') + '" data-on data-hide="[data-nm]" data-show="[data-sa]"' + (' data-goal' if goal else '') + '>Super Agent</button></div><span class="mk-chip">○○대학교 구성원</span></div>')
    Q1 = '프로그래밍 조건문의 개념을 쉽게 설명해 줘'
    def main_chat():
        hello = '<div class="mk-hello" data-hello><b>무엇을 도와드릴까요?</b><div class="mk-chips"><button type="button" data-fill="' + Q1 + '">예시: ' + Q1 + '</button></div></div>'
        body = demo(Q1) + "<p>조건문은 <b>'만약 ~라면 ~한다'</b>처럼, 조건이 참인지 거짓인지에 따라 서로 다른 명령을 실행하게 하는 문장이에요.</p><p>예를 들어 점수가 60점 이상이면 '합격', 아니면 '불합격'을 출력하게 할 수 있어요. 대부분의 언어에서 <b>if / else</b>로 써요.</p>" + EG
        return frame(TH, sd(), ('HAI-GPT', '새 채팅'), top(False) + '<div class="mk-log" id="mklog">' + hello + me('', 'data-qa hidden') + dots() + ai(body, 'data-a hidden') + '</div>' + inbar(Q1, '메시지를 입력하세요.', True))
    def agent_pick():
        return frame(TH, sd(), ('HAI-GPT', '모델 선택'), top(False, True) + '<div class="mk-log"><div class="mk-hello" data-nm><b>무엇을 도와드릴까요?</b><span>위쪽 모델 선택에서 쓰고 싶은 모델을 고를 수 있어요.</span></div>'
                     '<div class="mk-hello" data-sa hidden><b style="color:var(--mk)">Super Agent</b><b>물어보기만 하세요.<br>나머지는 알아서 합니다.</b><span>도구 이름이나 옵션을 외울 필요가 없어요. 한국어 한 줄로 원하는 것을 말하면 돼요.</span></div></div>'
                     '<div class="mk-inbar" style="position:static"><input type="text" placeholder="메시지를 입력하세요." aria-label="입력"><span class="mk-send" style="opacity:.5">' + ic('send', 15) + '</span></div>')
    Q2 = '이 논문 두 편 핵심 비교표 만들고, 발표용 PPT 5장 같이 만들어 줘.'
    RES = ('<p>요청하신 작업을 한 번에 진행했어요.</p><ul class="mk-ck"><li>논문 두 편의 핵심 내용 정리</li><li>핵심 비교표 작성</li><li>발표용 PPT 5장 구성</li></ul>'
           f'<p><span class="mk-filechip">{ic("doc", 13)}<span data-f1>논문_비교_발표자료.pptx</span></span> <span class="mk-filechip">{ic("doc", 13)}논문_비교_발표자료.pdf</span></p><span class="mk-eg">체험용 예시 결과 · 파일은 만들어지지 않아요</span>')
    def make():
        hello = ('<div class="mk-hello" data-hello><b style="color:var(--mk)">Super Agent</b><b>물어보기만 하세요. 나머지는 알아서 합니다.</b><div class="mk-chips"><button type="button" data-fill="' + Q2 + '">' + Q2 + '</button>'
                 '<button type="button" data-fill="매출 엑셀 분석해서 월별 트렌드 차트 그리고 PDF 한 권으로 묶어 줘.">매출 엑셀 분석해서 월별 트렌드 차트 그리고 PDF 한 권으로 묶어 줘.</button></div></div>')
        return frame(TH, sd(), ('HAI-GPT', 'Super Agent'), top(True) + '<div class="mk-log" id="mklog">' + hello + me('', 'data-qa hidden') + dots() + ai(demo(Q2) + RES, 'data-a hidden') + '</div>'
                     + inbar(Q2, '만들고 싶은 것을 한 줄로 말해 보세요.', True, pre=f'<span class="mk-ghost" title="파일 첨부">{ic("clip", 16)}</span>'))
    Q3 = '3페이지 표를 막대차트로 바꿔 줘'
    def fix():
        body = demo(Q3) + f'<p>3페이지의 표만 막대차트로 바꿨어요. 나머지 페이지는 그대로예요.</p><p><span class="mk-filechip">{ic("doc", 13)}논문_비교_발표자료_수정.pptx</span></p><span class="mk-eg">체험용 예시 결과</span>'
        return frame(TH, sd(), ('HAI-GPT', 'Super Agent'), top(True) + '<div class="mk-log" id="mklog">' + me(Q2).replace(' data-q', '') + ai(RES) + me('', 'data-qa hidden') + dots() + ai(body, 'data-a hidden')
                     + '<div class="mk-chips" data-hello><button type="button" data-fill="' + Q3 + '">' + Q3 + '</button><button type="button" data-fill="한글 요약본도 같이 만들어 줘">한글 요약본도 같이 만들어 줘</button></div></div>' + inbar(Q3, '고치고 싶은 부분만 말해 보세요.', True))
    I = 'media/walk/hai-gpt/'
    return [
        dict(title='학교 계정으로 로그인해요', text='기존 학교 계정(SSO) 그대로 로그인하면 HAI-GPT 메인 채팅 화면으로 들어가요.', do='「로그인」을 눌러 학교 계정으로 들어가 보세요.', img=I + '1.jpg',
             ui=login(TH, ('○○ UNIVERSITY', 'The New University,<br>K-University of the Future', '○○대학교 통합 로그인'), ('한국어 · English', '로그인'), [('ID', 'ID', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', True, True)], foot='비밀번호 초기화 · 도움말')),
        dict(title='메인 채팅 화면에서 시작해요', text='로그인하면 HAI-GPT 메인 채팅 화면이 열려요. 아래 입력창에 궁금한 것을 바로 물어볼 수 있어요.', do='입력창에 궁금한 것을 쓰고 보내 보세요. 비워 둔 채 보내면 예시 질문이 입력돼요.', ui=main_chat(), img=I + '2.jpg'),
        dict(title='Super Agent 모드를 켜요', text='상단 모델 선택에서 「Super Agent」를 눌러요. 도구 이름을 외울 필요 없이 원하는 것을 한국어 한 줄로 말하면 돼요.', do='위쪽 모델 선택에서 「Super Agent」를 눌러 보세요.', ui=agent_pick(), img=I + '3.jpg'),
        dict(title='무엇이든 만들어 달라고 해요', text='문서(한글·PDF), PPT, 이미지, 짧은 영상, 음악, 음성, 웹페이지, 다이어그램, 데이터 분석까지 한 번에 만들 수 있어요.', do='만들고 싶은 것을 한 줄로 써서 보내 보세요. 예시 요청을 눌러도 돼요.', ui=make(), img=I + '4.jpg'),
        dict(title='결과를 부분만 고쳐요', text='“3페이지 표를 막대차트로 바꿔 줘”처럼 후속 요청으로 일부만 고치면 처음부터 다시 만들지 않아도 돼요. 첨부 파일을 먼저 올리고 요청해도 좋아요.', do='고치고 싶은 부분만 후속 메시지로 보내 보세요.', ui=fix(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-MathTutor (학생용 매뉴얼)
def _math():
    TH = '--mk:#4f46e5;--mk-side:#1e1b4b'
    PROB = '극한 lim<sub>n→∞</sub> <sup>n</sup>√(n!) / n 의 값은?'
    def sd(active):
        return side('HAI-MathTutor', '', [('', [('home', 'home', '홈'), ('tut', 'user', '내 튜터'), ('hw', 'edit', '내 과제')])], active, user=('학생', '수학 튜터'), light=True, go={'home': 0})
    def home():
        T = [('2026년 1학기 선형대수 튜터', 4, 3), ('중간고사 대비 튜터', 4, 3), ('중간고사 대비 수학튜터', 2, 3), ('2027년 1학기 중간고사 튜터', 2, 3)]
        rows = ''.join(f'<div class="mk-rowbtn" style="cursor:default"><span><b>{n}</b> <span style="color:var(--mk)">0%</span></span><small>자율학습 {a}문제 중 0풀이 · 과제 {b}문제 중 0풀이</small></div>' for n, a, b in T)
        stats = ''.join(f'<div class="mk-stat"><small>{l}</small><b>{v}</b></div>' for l, v in [('총 풀이', '0문제'), ('전체 정답률', '0%'), ('AI 질문 횟수', '0회'), ('연속 학습일', '0일'), ('평균 풀이 시간', '0분')])
        main = ('<p class="mk-ref">4월 9일 목요일 · 나른한 오후네요. 잠시 집중해서 실력을 쌓아봐요!</p><div class="mk-h"><h3>나의 학습 현황</h3></div>' + rows + f'<div class="mk-stats">{stats}</div>'
                '<div class="mk-box tint" data-list hidden><b>내 튜터 4개</b><span>나에게 배정된 튜터 목록이에요. 튜터를 고르면 자율학습 문제와 과제를 풀 수 있어요.</span><div class="mk-pills">' + ''.join(f'<span>{n}</span>' for n, a, b in T) + '</div></div>')
        return frame(TH, sd('home').replace('<span class="mk-nav">' + ic('user') + '내 튜터</span>', '<button type="button" class="mk-nav" data-on data-show="[data-list]" data-goal>' + ic('user') + '내 튜터</button>'), ('HAI-MathTutor', '홈'), main)
    def tools(guide_goal=False):
        return ('<div class="mk-topbar"><div class="mk-h"><h3>함수의 극한</h3><span class="mk-badge">MATH</span></div><span class="mk-row"><button type="button" class="mk-btn sm line" data-show="[data-guide]"' + (' data-goal' if guide_goal else '') + '>' + ic('doc', 14) + '가이드</button>'
                '<button type="button" class="mk-btn sm line" data-go="4">' + ic('chat', 14) + 'AI 튜터</button></span></div><div class="mk-box"><span class="mk-chip">문제</span><p style="font-size:15px"><b>' + PROB + '</b></p></div>')
    GUIDE = ('<div class="mk-modal" data-guide hidden><div class="mk-row"><b>가이드 · 함수의 극한</b><button type="button" class="mk-btn sm line" data-hide="[data-guide]">닫기</button></div><span class="mk-lbl">필요한 개념</span>'
             '<p>1. 극한(limits): 수열이나 함수의 값이 무한히 가까워지는 값을 평가하는 개념입니다.<br>2. 계승(factorial): n!은 1부터 n까지의 모든 자연수의 곱입니다.<br>3. 멱(power): a<sup>n</sup>은 a가 n번 곱해진 것입니다.</p>'
             '<span class="mk-lbl">관련 공식·정리</span><p>1. 스털링 근사(Stirling\'s Approximation): n! ≈ √(2πn) (n/e)<sup>n</sup><br>2. (1 + 1/n)<sup>n</sup> 형태의 극한은 e로 수렴합니다.</p></div>')
    def write(goal):
        pad = ('<div class="mk-f">최종 답안을 작성해주세요<div class="mk-drawwrap"><canvas data-draw id="mkans"' + (' data-goal' if goal == 'draw' else '') + ' aria-label="답안 손글씨 칸"></canvas><span data-drawhint>여기에 손가락이나 마우스로 답을 써 보세요</span></div></div>'
               '<div class="mk-f">풀이 과정을 작성해주세요 (수식/숫자/영어 가능)<div class="mk-drawwrap"><canvas data-draw id="mksol" style="height:110px" aria-label="풀이 손글씨 칸"></canvas></div></div>'
               '<div class="mk-row"><button type="button" class="mk-btn sm line" data-clear="#mkans,#mksol">지우기</button><button type="button" class="mk-btn" data-show="[data-sent]">답안 제출</button></div>' + toast('data-sent', '답안을 제출했어요. 자동으로 채점돼 결과를 바로 볼 수 있어요.'))
        return frame(TH, sd('tut'), ('HAI-MathTutor', '문제 풀이'), tools(goal == 'guide') + GUIDE + pad)
    def result():
        main = (tools() + GUIDE + '<div class="mk-modal"><div class="mk-row"><b>결과</b><span class="mk-st ing">오답</span></div><div class="mk-box"><span class="mk-lbl">내 답안</span><b>27</b></div>'
                '<button type="button" class="mk-rowbtn" data-show="[data-sol]" data-goal><b>정답 및 해설 보기</b><span>›</span></button><button type="button" class="mk-rowbtn" data-show="[data-fr]"><b>친구 풀이 보기</b><span>›</span></button>'
                '<div class="mk-box tint" data-sol hidden><b>정답: 1/e</b><span>스털링 근사 n! ≈ √(2πn)(n/e)<sup>n</sup>을 쓰면 <sup>n</sup>√(n!)은 n이 커질수록 n/e에 가까워져요. 따라서 n으로 나눈 값은 1/e로 수렴해요.</span><span class="mk-eg">체험용 예시 해설</span></div>'
                '<p class="mk-demo" data-fr hidden>체험판에는 친구 풀이가 들어 있지 않아요. 실제 서비스에서는 다른 학생의 풀이를 볼 수 있어요.</p></div>')
        return frame(TH, sd('tut'), ('HAI-MathTutor', '채점 결과'), main)
    Q = '극한이 뭐예요?'
    def tutor():
        body = demo(Q) + '<p><b>극한의 정의</b><br>극한은 x가 어떤 값에 가까워질 때, 함수값 f(x)가 어떤 값에 가까워지는지를 보는 개념이에요.</p><p>예를 들어 f(x) = 2x + 1 에서 x가 3에 가까워지면 f(x)는 7에 가까워져요. 이것을 lim<sub>x→3</sub> (2x + 1) = 7 이라고 써요.</p>'
        aside = ('<aside class="mk-aside" style="width:250px"><b>' + ic('chat', 14) + ' AI 튜터</b><small style="color:#6b7280">문제에 대해 궁금한 것을 질문해 보세요</small><div class="mk-log" id="mklog" style="min-height:160px">'
                 + '<div class="mk-chips" data-hello><button type="button" data-fill="' + Q + '">' + Q + '</button></div>' + me('', 'data-qa hidden') + dots('T') + ai(body, 'data-a hidden', 'T') + '</div>' + inbar(Q, '질문을 입력하세요…', True) + '</aside>')
        main = tools() + GUIDE + '<div class="mk-f">최종 답안을 작성해주세요<div class="mk-drawwrap"><canvas data-draw id="mkans" aria-label="답안 손글씨 칸"></canvas><span data-drawhint>손글씨 답안 칸</span></div></div>'
        return frame(TH, sd('tut'), ('HAI-MathTutor', 'AI 튜터'), main, aside).replace('class="mk-aside" style', 'class="mk-aside mk-keep" style')
    I = 'media/walk/hai-mathtutor/'
    return [
        dict(title='나의 학습 현황을 봐요', text='홈에서 배정된 튜터별 진도와 정답률, 풀이 기록을 한눈에 봐요. 「내 튜터」를 누르면 나에게 배정된 튜터 목록이 나와요.', do='왼쪽 메뉴에서 「내 튜터」를 눌러 배정된 튜터 목록을 열어 보세요.', ui=home(), img=I + '1.jpg'),
        dict(title='답을 손글씨로 써요', text='문제를 보고 최종 답안과 풀이 과정을 손글씨로 자유롭게 써요. 이미지로 올려 제출할 수도 있어요.', do='「최종 답안」 칸에 손가락이나 마우스로 답을 써 보세요.', ui=write('draw'), img=I + '2.jpg'),
        dict(title='막히면 가이드를 열어요', text='「가이드」를 누르면 문제에 필요한 개념과 관련 공식을 정리해 보여 줘요.', do='「가이드」를 눌러 문제에 필요한 개념을 확인해 보세요.', ui=write('guide'), img=I + '3.jpg'),
        dict(title='바로 채점 결과를 확인해요', text='답안을 제출하면 자동으로 채점돼 정답인지 바로 알 수 있어요. 정답과 해설, 친구 풀이도 볼 수 있어요.', do='「정답 및 해설 보기」를 눌러 풀이를 확인해 보세요.', ui=result(), img=I + '4.jpg'),
        dict(title='AI 튜터에게 물어봐요', text='「AI 튜터」 창에서 개념을 물으면 예시와 함께 차근차근 설명해 줘요.', do='AI 튜터 입력칸에 궁금한 개념을 써서 보내 보세요.', ui=tutor(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ LXP (학습자 매뉴얼)
def _lxp():
    TH = '--mk:#2563eb;--mk-side:#1447b8'
    WEEKS = ['1주차 8월 04일 - 8월 10일', '2주차 8월 11일 - 8월 17일', '3주차 8월 18일 - 8월 24일', '4주차 8월 25일 - 8월 31일', '5주차 9월 01일 - 9월 07일']
    def sd(active, grade_goal=False):
        h = side('생성형 AI 입문과 활용', '', [('', [('home', 'home', '강의실 홈'), ('info', 'doc', '강의실 정보'), ('ntc', 'bell', '공지사항'), ('qna', 'chat', '질의응답'), ('ana', 'chart', '학습 분석'), ('grade', 'check', '성적 조회'), ('room', 'chat', '대화방'), ('ait', 'user', 'AI 튜터')]),
                                           ('주차별 학습', [('ov', 'doc', '강의 개요'), ('w1', 'edit', WEEKS[0])])], active, go={'home': 1, 'w1': 2, 'grade': 4},
                 mid=''.join(f'<span class="mk-hist" style="color:inherit;opacity:.55">{w}</span>' for w in WEEKS[1:]))
        return h.replace('data-go="4">', 'data-on data-goal data-show="[data-gr]" data-hide="[data-gr0]">') if grade_goal else h
    BAN = '<div class="mk-box" style="background:linear-gradient(120deg,#ede9fe,#dbeafe);border:0"><b style="font-size:16px">생성형 AI 입문과 활용</b><small>임교수 · 3학점</small></div>'
    def home():
        main = (BAN + '<button type="button" class="mk-card" data-on data-show="[data-wk]" data-goal><span class="mk-row"><strong>1주차 <small>2026-08-04 ~ 2026-08-10</small></strong><span class="mk-link">자세히 보기</span></span>'
                '<span class="mk-two"><span><span class="mk-lbl">학습 목표</span><br>1주차 | 인공지능의 이해</span><span class="mk-stats"><span class="mk-stat"><small>학습활동 진행</small><b>58.3%</b></span><span class="mk-stat"><small>출석</small><b>55.6%</b></span></span></span></button>'
                '<div class="mk-box tint" data-wk hidden><b>주요 학습 내용 및 방법</b><span>인공지능이 무엇인지에 대한 기본 개념을 학습합니다. 활용 사례를 통해 인공지능 기술이 어떻게 발전해 왔는지 이해하고, 향후 AI 기술이 사회와 산업 전반에 미칠 영향을 살펴봅니다.</span></div>'
                '<div class="mk-box"><b>미채점 활동 1개</b><table class="mk-tbl"><tr><th>주차</th><th>학습활동명</th><th>활동 유형</th><th>제출 여부</th></tr><tr><td>2주차</td><td>2주차_생성형 AI 활용 사례 과제</td><td>과제</td><td>제출</td></tr></table></div>'
                '<div class="mk-box"><b>질문과 답변</b><span class="mk-ref">등록된 질문과 답변이 없습니다.</span></div>')
        return frame(TH, sd('home'), ('LXP', '강의실 홈'), main)
    ACT = [('동영상', '1주차_인공지능이란?', '2026-08-04 00:00 ~ 2026-08-10 23:59 마감', '완료'), ('파일', '1주차_참고자료 파일', '', ''), ('토론', '생성형 AI란 무엇인가요?', '', '완료'), ('투표', '중간고사 일정 투표', '2026-08-04 00:00 ~ 2026-08-14 23:59 참여 가능', '미완료'), ('채팅', '1주차 채팅방', '2026-08-14 00:00 ~ 제한 없음', '')]
    def week(goal):
        rows = ''.join(f'<button type="button" class="mk-rowbtn" data-cat="{t}" data-on data-hide="[data-v]" data-show="[data-v={chr(39)}{k if k == 0 else 9}{chr(39)}]"{" data-goal" if goal == "open" and k == 0 else ""}><span><span class="mk-chip">{t}</span> <b>{n}</b><small>{d}</small></span>'
                       + (f'<span class="mk-st {"ok" if st == "완료" else "ing"}">{st}</span>' if st else '<span></span>') + '</button>' for k, (t, n, d, st) in enumerate(ACT))
        flt = ''.join(f'<button type="button" class="{"on" if k == "all" else ""}" data-filter="{k}" data-on{" data-goal" if goal == "filter" and k == "동영상" else ""}>{t}</button>' for k, t in [('all', '전체'), ('동영상', '동영상'), ('파일', '파일'), ('토론', '토론'), ('투표', '투표'), ('채팅', '채팅')])
        main = (BAN + '<div class="mk-box"><b>1주차 <small>8월 04일 - 8월 10일</small></b><span class="mk-lbl">학습 목표</span><span>1주차 | 인공지능의 이해</span></div>'
                f'<div class="mk-row"><b>학습활동</b><div class="mk-tabs">{flt}</div></div><div class="mk-opts">{rows}</div><p class="mk-empty" data-empty hidden>이 유형의 학습활동이 없습니다.</p>'
                '<div class="mk-modal" data-v="0" hidden><div class="mk-row"><b>1주차_인공지능이란?</b><span class="mk-st ok">완료</span></div><button type="button" class="mk-up" style="background:#0b1020;color:#fff;border:0" data-show="[data-play]">▶ 동영상 강의 재생</button>'
                + toast('data-play', '동영상 강의를 재생해요. 다 보면 진도가 「완료」로 바뀌어요. (체험판에는 영상이 들어 있지 않아요)') + '</div>'
                '<p class="mk-demo" data-v="9" hidden>체험판에는 첫 번째 활동(동영상 강의)만 열려요. 실제 강의실에서는 파일·토론·투표·채팅 활동에도 참여할 수 있어요.</p>')
        return frame(TH, sd('w1'), ('LXP', '주차별 학습'), main)
    def grade():
        G = [('시험', '중간고사', '25.00', '0–55', '45.46 %'), ('과제', '2주차_생성형 AI 활용 사례 과제', '14.00', '0–15', '93.33 %'), ('퀴즈', '1주차 퀴즈', '5.00', '0–5', '100.00 %')]
        tb = '<table class="mk-tbl"><tr><th>구분</th><th>성적 항목</th><th>성적</th><th>범위</th><th>백분율</th></tr>' + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for a, b, c, d, e in G) + '</table>'
        main = (BAN + '<div class="mk-box" data-gr0><span class="mk-ref">왼쪽 메뉴에서 「성적 조회」를 누르면 학습활동별 성적과 교수님 피드백을 볼 수 있어요.</span></div>'
                f'<div class="mk-box" data-gr hidden><div class="mk-row"><b>성적 조회</b><span class="mk-eg">체험용 예시 점수</span></div>{tb}<span class="mk-ref">성적은 교수님이 공개한 시점부터 볼 수 있어요.</span></div>')
        return frame(TH, sd('home', True), ('LXP', '성적 조회'), main)
    I = 'media/walk/lxp/'
    return [
        dict(title='학번/사번으로 로그인해요', text='○○대학교 LXP 접속 페이지에서 개인 계정으로 로그인하면 강의실에 들어갈 수 있어요.', do='학번(사번)과 비밀번호 칸을 확인하고 「로그인」을 눌러 보세요.', img=I + '1.jpg',
             ui=login(TH, ('○○ UNIVERSITY', '○○대학교 LXP', '인공지능(AI) 기반 학습 경험 플랫폼'), ('LXP', '로그인'), [('학번/사번', '학번 또는 사번', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', True, True)], foot='○○대학교 LXP에 오신 것을 환영합니다.')),
        dict(title='강의실 홈에 들어가요', text='강의실 홈에서는 이번 주 학습 목표와 진행률, 아직 채점되지 않은 활동, 질문과 답변을 한 화면에서 확인해요.', do='강의실 홈에서 「1주차」 학습 영역을 눌러 이번 주 학습을 확인해 보세요.', ui=home(), img=I + '2.jpg'),
        dict(title='주차별 학습을 확인해요', text='주차별 학습에서는 그 주의 학습 목표와 학습활동 목록, 기간과 완료 여부를 확인하고 활동을 눌러 바로 학습해요.', do='학습활동 목록에서 첫 번째 활동 「1주차_인공지능이란?」을 눌러 보세요.', ui=week('open'), img=I + '3.jpg'),
        dict(title='학습활동을 진행해요', text='동영상·파일·토론·투표·채팅 같은 학습활동을 유형별로 모아 보고, 기간 안에 참여해 완료해요.', do='학습활동 필터에서 「동영상」을 눌러 동영상 활동만 모아 보세요.', ui=week('filter'), img=I + '4.jpg'),
        dict(title='성적을 조회해요', text='강의에 참여한 학습활동별 성적과 교수님이 입력한 점수·피드백을 확인해요.', do='왼쪽 메뉴에서 「성적 조회」를 눌러 보세요.', ui=grade(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Forum (학생용 매뉴얼)
def _forum():
    TH = '--mk:#2563eb;--mk-side:#0f172a'
    def sd(active):
        return side('HAI-Forum', '', [('', [('dash', 'home', '대시보드'), ('crs', 'doc', '내 강좌'), ('cls', 'send', '수업'), ('hw', 'edit', '과제'), ('gr', 'chart', '성적'), ('set', 'gear', '설정')])], active, user=('학생', '수강 중인 강좌 2개'), light=True, go={'dash': 0, 'hw': 1, 'cls': 3})
    def dash():
        stats = ''.join(f'<div class="mk-stat"><small>{l}</small><b>{v}</b></div>' for l, v in [('수강 과목', '2'), ('완료한 과제', '1'), ('대기 중 과제', '0'), ('평균 점수', '80점')])
        main = ('<div class="mk-box" style="background:linear-gradient(120deg,#16a34a,#0d9488);color:#fff;border:0"><b style="font-size:15px">안녕하세요, 학생님!</b><span>오늘 예정된 수업 0개, 마감 임박 과제 0건이 있습니다.</span></div>'
                '<div class="mk-box" style="background:#fff8ec;border-color:#fde6c3"><b>내 학업 위험 알림 (2건)</b><span class="mk-row"><span>고급시스템프로그래밍 <small>과제 제출 지연</small></span><span class="mk-st ing">위험</span></span><span class="mk-row"><span>해부생리학 <small>출석 주의</small></span><span class="mk-st ing">주의</span></span></div>'
                f'<div class="mk-stats">{stats}</div><div class="mk-two"><div class="mk-box"><b>오늘 일정</b><span class="mk-ref">오늘 예정된 수업이 없습니다.</span></div><div class="mk-box"><b>마감 임박 과제</b><span class="mk-ref">마감 임박 과제가 없습니다.</span></div></div>'
                '<div class="mk-two"><div class="mk-box"><b>내 강좌</b><button type="button" class="mk-rowbtn" data-on data-show="[data-crs]" data-goal><span><b>고급시스템프로그래밍</b></span><span>›</span></button><button type="button" class="mk-rowbtn" data-on><span><b>해부생리학</b></span><span>›</span></button></div>'
                '<div class="mk-box"><b>최근 성적</b><span class="mk-row"><span>과제 0: 환경 설정</span><b>40/50 · 80%</b></span></div></div>'
                + toast('data-crs', '고급시스템프로그래밍 강좌로 들어왔어요. 수업·콘텐츠·과제·성적을 볼 수 있어요.'))
        return frame(TH, sd('dash'), ('HAI-Forum', '대시보드'), main)
    def hw():
        main = ('<div class="mk-h"><h3>과제 1: 조건문과 반복문</h3><span class="mk-badge">과제</span></div><p class="mk-ref">마감 2026년 6월 12일 오후 11:59 · 만점 100점 · 지각 제출 감점 10%</p>'
                '<div class="mk-box"><b>설명</b><span>조건문(if-else)과 반복문(for, while)을 활용하여 간단한 계산기 프로그램을 작성하세요.</span></div>'
                '<div class="mk-box"><b>제출하기</b><textarea id="mkhw" placeholder="제출 내용을 입력하세요..." aria-label="제출 내용"></textarea><div class="mk-row"><span class="mk-ref">' + ic('clip', 14) + ' 첨부 파일이 없습니다.</span><button type="button" class="mk-btn sm line" data-show="[data-file]">파일 추가</button></div>'
                '<span class="mk-filechip" data-file hidden>' + ic('doc', 13) + 'calculator.py (체험용)</span><p class="mk-demo" data-need hidden>제출 내용을 먼저 써 주세요.</p>'
                '<div class="mk-row end"><button type="button" class="mk-btn" data-req="#mkhw" data-show="[data-sent]" data-goal>' + ic('send', 14) + '제출</button></div>' + toast('data-sent', '과제를 제출했어요. 마감 전에는 다시 제출할 수 있어요.') + '</div>')
        return frame(TH, sd('hw'), ('HAI-Forum', '과제 제출'), main)
    def code():
        main = ('<div class="mk-row"><div class="mk-h"><h3>코드 제출 &amp; 실행</h3></div><label class="mk-f" style="flex-direction:row;align-items:center">언어<select><option>Python</option><option>Java</option><option>C++</option><option>JavaScript</option></select></label></div>'
                '<textarea class="mk-code" id="mkcode" spellcheck="false" aria-label="코드 편집기" rows="6"># 표준 입력으로부터 읽고 표준 출력으로 답안 출력\n# 예: print(input())\nprint(input())</textarea>'
                '<div class="mk-row"><span class="mk-ref">제출 시 모든 테스트 케이스에 대해 코드를 실행합니다.</span><button type="button" class="mk-btn" data-req="#mkcode" data-show="[data-res]" data-goal>' + ic('send', 14) + '제출 + 실행</button></div><p class="mk-demo" data-need hidden>코드를 먼저 작성해 주세요.</p>'
                '<div class="mk-box tint" data-res hidden><div class="mk-row"><b>테스트 결과</b><span class="mk-st ok">COMPLETED</span></div><span>테스트 케이스 3개 중 3개 통과 · 예상 출력과 실제 출력이 일치해요.</span><span class="mk-eg">체험용 예시 결과 · 코드는 실제로 실행되지 않아요</span></div>'
                '<div class="mk-box"><b>제출 이력</b><span class="mk-row"><span><span class="mk-chip">python</span> 2026. 6. 9. 오전 12:15:36</span><span class="mk-row"><span class="mk-st ok">COMPLETED</span><span class="mk-link">재실행</span><span class="mk-link">결과</span></span></span></div>')
        return frame(TH, sd('hw'), ('HAI-Forum', '코딩 과제'), main)
    def live():
        main = ('<div class="mk-h"><h3>수업 관리</h3></div><div class="mk-rowbtn" style="cursor:default"><span><span class="mk-st ing">LIVE</span> <b>제19장 심장</b></span><span class="mk-btn sm" style="cursor:default">입장</span></div>'
                '<div class="mk-modal"><b style="text-align:center">수업 입장 준비</b><p style="text-align:center">AP1012 · 해부생리학<br><b>제19장 심장</b></p>'
                '<div class="mk-up" style="border-style:solid" data-cam>' + ic('user', 30) + '<span>카메라 미리보기</span></div><p class="mk-demo" data-camoff hidden>카메라를 껐어요. 내 화면이 다른 사람에게 보이지 않아요.</p>'
                '<div class="mk-two"><button type="button" class="mk-tile on" data-tg="cam">' + ic('send', 18) + '<b>카메라</b><small data-camt>ON</small></button><button type="button" class="mk-tile" data-tg="mic">' + ic('bell', 18) + '<b>마이크</b><small data-mict>OFF</small></button></div>'
                '<button type="button" class="mk-btn wide" data-show="[data-in]" data-goal>수업 입장</button>' + toast('data-in', '수업에 입장했어요. 교수님이 입장 설정을 해 두면 그에 따라 카메라·마이크가 켜져요.') + '</div>')
        return frame(TH, sd('cls'), ('HAI-Forum', '실시간 화상수업'), main)
    def socratic():
        main = ('<div class="mk-row"><div class="mk-h"><h3>소크라틱 토론</h3><span class="mk-st ing">LIVE</span></div><span class="mk-eg">체험용 예시 주제</span></div>'
                '<div class="mk-box tint"><span class="mk-lbl">토론 주제 (교수님 질문)</span><b>인공지능이 만든 글의 책임은 누구에게 있을까요?</b></div>'
                '<div class="mk-log" id="mklog">' + me('', 'data-qa hidden') + dots('교수') + ai('<p><b>후속 질문</b><br>그렇게 생각한 근거는 무엇인가요? 반대 입장이라면 어떤 점을 문제 삼을까요?</p><span class="mk-eg">체험용 예시 질문</span>', 'data-a hidden', '교수') + '</div>'
                + inbar('글을 쓰도록 지시하고 결과를 확인한 사람에게 책임이 있다고 생각합니다.', '내 생각을 작성해 주세요…', True, hide='[data-none]', more='체험판에서는 후속 질문이 한 번만 나와요. 실제 수업에서는 교수님의 후속 질문에 이어서 답하며 토론을 이어 가요.'))
        return frame(TH, sd('cls'), ('HAI-Forum', '소크라틱 토론'), main)
    I = 'media/walk/hai-forum/'
    return [
        dict(title='대시보드에서 오늘 할 일을 봐요', text='오늘의 수업, 마감 임박 과제, 내 강좌, 평점을 한눈에 봐요. 진행 중인 수업은 「참여하기」로 바로 들어가요.', do='「내 강좌」에서 「고급시스템프로그래밍」을 눌러 강좌로 들어가 보세요.', ui=dash(), img=I + '1.jpg'),
        dict(title='과제를 확인하고 제출해요', text='과제 설명과 마감 시간을 확인하고, 내용을 쓰거나 파일을 올려 「제출」을 눌러요.', do='제출 내용을 직접 쓰고 「제출」을 눌러 보세요.', ui=hw(), img=I + '2.jpg'),
        dict(title='코딩 과제는 바로 실행해요', text='언어를 고르고 코드를 작성한 뒤 「제출 + 실행」을 누르면 자동으로 채점돼요. 테스트 결과와 오류 메시지도 볼 수 있어요.', do='코드를 확인하거나 고쳐 본 뒤 「제출 + 실행」을 눌러 보세요.', ui=code(), img=I + '3.jpg'),
        dict(title='실시간 화상수업에 들어가요', text='대시보드나 강좌에서 「참여하기」를 누르고, 입장 전에 카메라·마이크를 확인해요.', do='카메라와 마이크를 눌러 켜고 끈 뒤 「수업 입장」을 눌러 보세요.', ui=live(), img=I + '4.jpg'),
        dict(title='소크라틱 토론에 참여해요', text='교수님이 던진 질문에 내 생각을 쓰고, 이어지는 후속 질문에 답하며 생각을 깊게 다듬어요.', do='교수님의 질문에 내 생각을 써서 보내 보세요. 비워 둔 채 보내면 예시 답이 입력돼요.', ui=socratic(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Fist (운영자/사용자 매뉴얼)
def _fist():
    TH = '--mk:#1f3a8a;--mk-side:#0f1b3d'
    def sd(active):
        return side('FIST AI 코스웨어', '융합과학수사학과', [('', [('dash', 'home', '강의 대시보드'), ('plan', 'doc', '강의계획서 생성'), ('make', 'edit', '수업 자료 생성'), ('edit', 'doc', '수업 자료 편집'), ('ana', 'chart', '학습 분석')])], active,
                    user=('교수자', '범죄수사절차법1'), light=True, go={'dash': 0, 'plan': 1, 'make': 2, 'edit': 3, 'ana': 4})
    WK = ['범죄수사절차법 개요', '수사의 기본원칙', '수사기관의 종류와 권한', '수사절차']
    def dash():
        rows = ''.join(f'<div class="mk-rowbtn" style="cursor:default"><span>{k + 1}주차　<b>{w}</b></span><span class="mk-pills"><span>예정</span><span>시험 설정</span></span></div>' for k, w in enumerate(WK))
        main = ('<div class="mk-h"><h3>범죄수사절차법1</h3></div><b>강의 진행 현황 요약</b><div class="mk-two"><div class="mk-box"><span class="mk-lbl">CURRENT WEEK</span><b>1주차 범죄수사절차법 개요</b><span class="mk-st ok" style="align-self:flex-start">진행 중</span></div>'
                '<div class="mk-box"><span class="mk-lbl">UPCOMING</span><b>예정된 수업 없음</b><span class="mk-ref">다음 차시 수업이 없습니다.</span></div></div><b>전체 강의 일정</b>'
                '<div class="mk-box tint"><div class="mk-row"><span><b>강의계획서를 생성해주세요</b><br><span class="mk-ref">강의계획서 생성이 진행 중입니다. 이어서 작성하세요.</span></span><button type="button" class="mk-btn sm dark" data-show="[data-go1]" data-goal>이어서 작성</button></div></div>'
                + toast('data-go1', '강의계획서 작성 화면으로 이어져요. 「다음」을 눌러 주차별 구성을 확인해 보세요.') + rows)
        return frame(TH, sd('dash'), ('FIST', '강의 대시보드'), main)
    def plan():
        rows = ''.join(f'<div class="mk-rowbtn" style="cursor:default"><span><b>{k + 1}주차</b>　{w}<small>교재 제{k + 1}장 · 2차시</small></span><span class="mk-pills"><span>차시 조정</span></span></div>' for k, w in enumerate(WK))
        main = ('<div class="mk-h"><h3>강의계획서 생성</h3><span class="mk-badge">주차별 수업 배정</span></div><p class="mk-ref">교재를 분석해 만든 주차·차시별 수업 구성이에요. 학사 일정에 맞게 순서와 교재 범위를 조정할 수 있어요.</p>' + rows
                + '<div class="mk-row"><button type="button" class="mk-btn line">이전</button><button type="button" class="mk-btn dark mk-grow" style="justify-content:center" data-show="[data-nx]" data-goal>다음: 학습 목표 생성</button></div>' + toast('data-nx', '주차 구성을 확정하고 학습 목표 생성 단계로 넘어갔어요.'))
        return frame(TH, sd('plan'), ('FIST', '강의계획서'), main)
    def make():
        ty = ''.join(f'<button type="button" class="mk-tile{" on" if k < 2 else ""}" data-tg><b>{t}</b><small>{"ON" if k < 2 else "OFF"}</small></button>' for k, t in enumerate(['강의록', '강의장표', '팟캐스트', '마인드맵', '퀴즈', '사례(TBL)']))
        main = ('<div class="mk-h"><h3>수업 자료 생성</h3><span class="mk-badge">1주차 1차시</span></div><div class="mk-box"><b>파일 업로드</b><div class="mk-pills"><span class="on">주교재</span><span>부가자료</span></div>'
                f'<span class="mk-filechip">{ic("doc", 13)}제1주차_형사절차의 이해_교재.pdf</span><span class="mk-filechip">{ic("doc", 13)}제1주차_형사절차기초_20260212.pdf</span></div>'
                f'<div class="mk-box"><b>만들 자료 유형 <small>(눌러서 켜고 끄기)</small></b><div class="mk-tiles" style="grid-template-columns:repeat(3,minmax(0,1fr))">{ty}</div></div>'
                '<div class="mk-row"><span class="mk-ref">선택된 자료 2개</span><button type="button" class="mk-btn dark" data-wait="[data-mk]" data-show="[data-made]" data-goal>자료 생성 시작</button></div>'
                '<p class="mk-note" data-mk hidden><span>AI가 교재를 분석해 자료를 만들고 있어요…</span></p><div class="mk-box tint" data-made hidden><b>자료 생성이 끝났어요</b><span>켜 둔 유형의 자료가 차시별로 만들어졌어요. 「수업 자료 편집」에서 검토하고 고칠 수 있어요.</span><span class="mk-eg">체험용 예시 · 실제로는 몇 분 정도 걸려요</span></div>')
        return frame(TH, sd('make'), ('FIST', '수업 자료 생성'), main)
    def edit():
        th = ''.join(f'<button type="button" class="mk-rowbtn{" on" if k == 0 else ""}" data-on data-set="[data-sn]|{k + 1}"><span>{k + 1}　{t}</span></button>' for k, t in enumerate(['표지', '학습 목표', '형사절차의 흐름', '수사기관 비교']))
        main = ('<div class="mk-h"><h3>수업 자료 편집</h3><span class="mk-badge">강의장표</span></div><div class="mk-two" style="grid-template-columns:150px 1fr"><div class="mk-opts">' + th + '</div>'
                '<div class="mk-box" style="background:linear-gradient(135deg,#1e3a8a,#0ea5e9);color:#fff;border:0;min-height:170px;justify-content:center;align-items:center;text-align:center"><b style="font-size:18px">범죄수사절차법 개요(상)</b><span>수사기관의 권한과 형사사법 체계의 이해</span><small>1주차 강의 · 장표 <span data-sn>1</span> / 30</small></div></div>'
                '<div class="mk-row"><button type="button" class="mk-btn dark" data-show="[data-ai]" data-goal>콘텐츠 편집</button><button type="button" class="mk-btn line">배포 설정</button></div>'
                '<div class="mk-box" data-ai hidden><b>AI 수정 요청</b><textarea id="mkfx" placeholder="예: 3번 장표에 실제 사례를 하나 추가해 줘"></textarea><p class="mk-demo" data-need hidden>수정 방향을 먼저 써 주세요.</p><div class="mk-row end"><button type="button" class="mk-btn sm" data-req="#mkfx" data-show="[data-fxd]">AI에게 수정 요청</button></div>'
                + toast('data-fxd', '수정 방향을 AI에게 전달했어요. 고친 장표를 다시 검토할 수 있어요. (체험판에서는 장표가 바뀌지 않아요)') + '</div>')
        return frame(TH, sd('edit'), ('FIST', '수업 자료 편집'), main)
    def ana():
        bars = ''.join(f'<div class="mk-bar2"><span>{l}</span><i style="--v:{v}%"></i><b>{v}%</b></div>' for l, v in [('학생 참여도', 50), ('사전문항 평균', 67), ('사후문항 평균', 40), ('Q&A 활동', 30)])
        main = ('<div class="mk-row"><div class="mk-h"><h3>주차별 학생 성과 분석 대시보드</h3></div><span class="mk-row"><select aria-label="주차"><option>1주차: 범죄수사절차법 개요(상)</option></select><button type="button" class="mk-btn sm dark" data-show="[data-dl]" data-goal>' + ic('down', 14) + '리포트 다운로드</button></span></div>'
                '<div class="mk-stats"><div class="mk-stat"><small>팟캐스트 시청 인원</small><b>13명</b></div><div class="mk-stat"><small>시청 완료율</small><b>50%</b></div><div class="mk-stat"><small>사전문항 평균</small><b>66.7</b></div><div class="mk-stat"><small>사후문항 평균</small><b>40</b></div></div>'
                f'<div class="mk-box"><div class="mk-row"><b>학습성과 요약</b><span class="mk-eg">체험용 예시 수치</span></div><div class="mk-bars">{bars}</div></div>' + toast('data-dl', '분석 보고서를 내려받았어요. (체험판에서는 파일이 만들어지지 않아요)'))
        return frame(TH, sd('ana'), ('FIST', '학습 분석'), main)
    I = 'media/walk/hai-fist/'
    return [
        dict(title='강의 대시보드에서 시작해요', text='담당 강의를 고르면 진행 중인 주차, 예정 수업, 공지를 한 화면에서 보고 강의계획서·자료 생성·시험 설정으로 이동해요.', do='「강의계획서를 생성해주세요」 알림의 「이어서 작성」을 눌러 보세요.', ui=dash(), img=I + '1.jpg'),
        dict(title='AI가 교재로 강의계획서를 만들어요', text='교재를 올리면 AI가 분석해 강의계획서 초안을 만들어요. 주차·차시별 수업 구성과 교재 범위를 학사 일정에 맞게 조정해요.', do='주차 구성을 확인했다면 「다음: 학습 목표 생성」을 눌러 보세요.', ui=plan(), img=I + '2.jpg'),
        dict(title='수업 자료를 생성해요', text='차시마다 강의록, 강의장표, 팟캐스트, 마인드맵, 퀴즈 등 필요한 자료 유형을 골라 AI로 만들어요.', do='만들 자료 유형을 눌러 고른 뒤 「자료 생성 시작」을 눌러 보세요.', ui=make(), img=I + '3.jpg'),
        dict(title='만든 자료를 AI와 함께 다듬어요', text='강의장표를 미리 보며 고칠 장표를 고르고, 수정 방향을 AI에게 요청해 내용을 보완해요.', do='「콘텐츠 편집」을 눌러 AI 수정 요청 칸을 열어 보세요.', ui=edit(), img=I + '4.jpg'),
        dict(title='학습성과를 분석해요', text='학생 참여도, 평가 결과, Q&A 활동, AI 활용 이력으로 학습성과를 확인하고 분석 보고서를 내려받아요.', do='「리포트 다운로드」를 눌러 분석 보고서를 받아 보세요.', ui=ana(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Lens (사용자 매뉴얼)
def _lens():
    TH = '--mk:#ea580c;--mk-side:#431407'
    SUBJ = [('HAI-LENS 시연', 'DEMO-LIVE-101 · 2026-2학기'), ('파이썬 프로그래밍', 'PY-101-DEMO · 2026-1학기'), ('CUDA Programming', 'CUDA-101-DEMO · 2026-1'), ('운영체제', 'os-DEMO · 2026-1')]
    def sd(active=0):
        return side('HAILENS', '', [('과목', [(f's{k}', 'doc', n) for k, (n, c) in enumerate(SUBJ)])], f's{active}', user=('데모 교수1', '교수'), light=True, go={'s0': 2})
    def pick():
        rows = ''.join(f'<button type="button" class="mk-rowbtn" data-on data-show="[data-in]"{" data-goal" if k == 0 else ""}><span><small>0{k + 1}</small><b>{n}</b><small>{c}</small></span><span>→</span></button>' for k, (n, c) in enumerate(SUBJ))
        return frame(TH, sd(-1), ('HAILENS', '홈'), '<div class="mk-center" style="margin:6px auto"><h3 style="margin:0;font-size:18px">과목을 선택하세요</h3><span class="mk-ref">선택하면 강의 시작, 자료 관리와 지난 리포트를 확인할 수 있습니다.</span></div>' + rows + toast('data-in', '과목 홈으로 들어왔어요. 강의 시작, 강의 자료, 지난 강의를 볼 수 있어요.'))
    def upload():
        main = ('<div class="mk-h"><h3>강의 자료</h3><span class="mk-badge">HAI-LENS 시연</span></div><div class="mk-two"><div class="mk-box" style="min-height:190px"><span class="mk-lbl">미리보기</span><span class="mk-center mk-ref" data-pv0>파일을 선택하면 미리보기가 표시됩니다</span>'
                '<div class="mk-sheet" data-pv hidden><p class="c" style="letter-spacing:0">인공지능 시대를 위한 운영체제</p><p style="text-align:center">1 / 24</p></div></div>'
                '<div class="mk-box"><button type="button" class="mk-up" data-hide="[data-pv0],[data-none]" data-show="[data-pv],[data-fl]" data-goal>' + ic('down', 20) + '<b>클릭하거나 드래그</b><small>여러 PDF 파일을 한 번에 업로드 가능</small></button><span class="mk-lbl">업로드된 파일</span>'
                '<span class="mk-ref" data-none>업로드된 파일이 없습니다</span><span class="mk-filechip" data-fl hidden>' + ic('doc', 13) + '운영체제_파일시스템.pdf (체험용)</span><span class="mk-ref">PDF만 지원됩니다. PPT는 PDF로 저장해서 올려 주세요.</span></div></div>')
        return frame(TH, sd(0), ('HAILENS', '강의 자료'), main)
    def start():
        main = ('<div class="mk-box"><div class="mk-row"><span><b style="font-size:17px">HAI-LENS 시연</b><br><small>시연용</small></span><span class="mk-row"><button type="button" class="mk-btn" data-hide="[data-idle]" data-show="[data-rec]" data-goal>▶ 강의 시작</button><span class="mk-btn line" style="cursor:default">강의 자료 업로드</span></span></div>'
                '<div class="mk-stats"><div class="mk-stat"><b>0회</b><small>총 강의 횟수</small></div><div class="mk-stat"><b>—</b><small>총 강의 시간</small></div><div class="mk-stat"><b>0건</b><small>분석 완료</small></div></div></div>'
                '<div class="mk-box" data-idle><b>지난 강의</b><span class="mk-ref">아직 진행한 강의가 없습니다.</span></div>'
                '<div class="mk-box" data-rec hidden style="background:#0b1020;color:#fff;border:0"><div class="mk-row"><b>발표 화면</b><span class="mk-st ing">● 녹화 중</span></div><div class="mk-center" style="padding:18px 0"><b style="font-size:16px">인공지능 시대를 위한 운영체제</b><small>슬라이드 <span data-pg>1</span> / 24</small></div>'
                '<div class="mk-row"><span class="mk-pills"><button type="button" data-set="[data-pg]|1">이전</button><button type="button" data-set="[data-pg]|2">다음</button></span><button type="button" class="mk-btn sm" data-show="[data-end]">강의 종료</button></div>'
                + toast('data-end', '강의를 마치고 분석을 시작했어요. 화면을 닫아도 분석은 계속돼요.').replace('mk-ok"', 'mk-ok" style="color:#86efac"') + '</div>')
        return frame(TH, sd(0), ('HAILENS', '과목 홈'), main)
    def report():
        bars = ''.join(f'<div class="mk-bar2"><span>{l}</span><i style="--v:{v * 20}%"></i><b>{v}</b></div>' for l, v in [('도입', 3.8), ('전개', 3.4), ('마무리', 2.6), ('전체', 3.3)])
        main = ('<div class="mk-box" style="background:#fff7ed;border-color:#fed7aa"><div class="mk-row"><b style="font-size:16px">강의 분석 결과</b><b style="font-size:26px;color:var(--mk)">3.3<small> / 5</small></b></div>'
                '<span>본 강의는 운영체제의 핵심 요소인 파일 시스템의 개념과 구조를 체계적으로 다루고 있습니다. 도입부에서 이전 수업과의 연계성을 확보하고 학습 목표를 명확히 제시한 점이 우수하며, 본론에서는 복잡한 기술적 개념을 반복 설명과 요약을 통해 효과적으로 전달합니다. 다만, 학습자의 참여를 유도하는 질문이나 상호작용이 부족하고, 마무리 단계에서 학습 내용을 정리하는 요약 과정이 미흡하여 보완이 필요합니다.</span>'
                '<div class="mk-row"><span class="mk-pills"><span>개선 우선 6개</span><span>강점 11개</span></span><span class="mk-row"><button type="button" class="mk-btn sm line" data-show="[data-dl]">리포트 다운로드</button><button type="button" class="mk-btn sm" data-show="[data-tl]" data-goal>강의 흐름 탐색 →</button></span></div></div>'
                + toast('data-dl', '리포트를 내려받았어요. (체험판에서는 파일이 만들어지지 않아요)') + toast('data-tl', '타임라인 화면으로 이동해요. 「다음」을 눌러 구간별로 돌아보세요.')
                + f'<div class="mk-box"><div class="mk-row"><b>강의 한눈에 보기 · 구간 점수 형상</b><span class="mk-eg">체험용 예시 점수</span></div><div class="mk-bars">{bars}</div></div>')
        return frame(TH, sd(0), ('HAILENS', '리포트 요약'), main)
    def timeline():
        SEG = [('구간 1 · 도입', '00:00 – 00:11', "강의 제목 '인공지능 시대를 위한 운영체제'와 강의교안 이용 안내를 담은 표지 슬라이드를 제시하고 있습니다."), ('구간 2 · 전개', '00:11 – 12:40', '파일 시스템의 개념과 구조를 슬라이드 순서에 따라 설명하고, 핵심 용어를 반복해 정리합니다.'), ('구간 3 · 마무리', '12:40 – 27:34', '학습 내용을 정리하는 요약이 짧아, 다음 차시 예고와 함께 핵심 정리를 보완하면 좋습니다.')]
        segs = ''.join(f'<button type="button" class="mk-rowbtn{" on" if k == 0 else ""}" data-on data-hide="[data-ob]" data-show="[data-ob={chr(39)}{k}{chr(39)}]"><span><b>{n}</b><small>{t}</small></span></button>' for k, (n, t, o) in enumerate(SEG))
        obs = ''.join(f'<div class="mk-box" data-ob="{k}"{"" if k == 0 else " hidden"}><span class="mk-lbl">관찰 내용</span><span>{o}</span>{"" if k == 0 else chr(60) + "span class=mk-eg" + chr(62) + "체험용 예시" + chr(60) + "/span" + chr(62)}</div>' for k, (n, t, o) in enumerate(SEG))
        main = ('<div class="mk-h"><h3>강의 흐름</h3><span class="mk-badge">00:00 – 27:34</span></div><div class="mk-two"><div class="mk-box" style="background:#0b1020;color:#fff;border:0;min-height:170px;align-items:center;justify-content:center;text-align:center"><b>인공지능 시대를 위한 운영체제</b>'
                '<button type="button" class="mk-btn" style="border-radius:999px" data-hide="[data-pl0]" data-show="[data-pl]" data-goal>▶ 재생</button><small data-pl0>슬라이드 · 영상 · 음성을 함께 볼 수 있어요</small><small data-pl hidden>재생 중 · 구간 1 (체험판에는 영상이 들어 있지 않아요)</small></div>'
                f'<div class="mk-opts">{segs}</div></div>{obs}')
        return frame(TH, sd(0), ('HAILENS', '타임라인'), main)
    I = 'media/walk/hai-lens/'
    return [
        dict(title='과목을 골라요', text='로그인하면 담당 과목이 보여요. 과목을 누르면 강의 시작, 강의 자료, 지난 강의로 들어가요.', do='과목 목록에서 「HAI-LENS 시연」을 눌러 보세요.', ui=pick(), img=I + '1.jpg'),
        dict(title='강의 자료(PDF)를 올려요', text='수업에 쓸 PDF 슬라이드를 올려요. 리포트에서 어느 슬라이드에서 무슨 말을 했는지 함께 보여 줘요.', do='「클릭하거나 드래그」 영역을 눌러 PDF 슬라이드를 올려 보세요.', ui=upload(), img=I + '2.jpg'),
        dict(title='강의를 진행해요', text='강의를 시작하면 발표 화면으로 바뀌어요. 슬라이드를 넘긴 시점이 기록되고, 필기 도구도 쓸 수 있어요. 마치면 「강의 종료」로 분석을 시작해요.', do='「강의 시작」을 눌러 발표 화면으로 들어가 보세요.', ui=start(), img=I + '3.jpg'),
        dict(title='리포트 요약을 확인해요', text='종합 점수와 강의 총평, 8개 영역별 점수와 진단, 먼저 고칠 점과 잘하고 있는 점을 한눈에 봐요.', do='「강의 흐름 탐색」을 눌러 타임라인으로 가 보세요.', ui=report(), img=I + '4.jpg'),
        dict(title='강의 흐름을 구간별로 돌아봐요', text='타임라인에서 구간별 점수 흐름을 보고, 원하는 구간의 슬라이드·영상·음성과 관찰 내용을 함께 확인해요.', do='「재생」을 눌러 이 구간의 강의를 다시 봐요. 오른쪽 구간도 눌러 보세요.', ui=timeline(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Way (학생용 매뉴얼)
def _way():
    TH = '--mk:#6d4fe0;--mk-side:#3b2a8f'
    def sd(active, goal=''):
        h = side('HAI-Way', '', [('', [('dash', 'home', '대시보드'), ('cur', 'doc', '커리큘럼 추천'), ('job', 'user', '직무 매칭'), ('dbl', 'edit', '복수전공 추천'), ('pf', 'mark', '포트폴리오'), ('rec', 'search', '채용공고 추천')])], active,
                 go={'dash': 1, 'cur': 2, 'job': 3}, top='<div class="mk-course" style="background:rgba(255,255,255,.12);border:0;color:#fff"><b>학생</b><small>데이터사이언스학부 데이터테크전공<br>선택 직무: 시스템소프트웨어개발자<br>진로 설계 진행률 20%</small></div>')
        return h.replace('data-go="2">', 'data-on data-goal data-hide="[data-c0]" data-show="[data-c1]">') if goal == 'cur' else h
    def dash():
        sk = ''.join(f'<span>{x}</span>' for x in ['자료구조', '알고리즘', '데이터베이스', '운영체제', '통계', '파이썬'])
        bars = ''.join(f'<div class="mk-bar2"><span>{l}</span><i style="--v:{v * 3}%"></i><b>{v}%</b></div>' for l, v in [('응용 능력', 28), ('개발적 사고력', 25), ('이론 설명 능력', 22), ('논리적 분석력', 18), ('기초이론 이해', 6)])
        main = ('<div class="mk-h"><h3>대시보드</h3></div><div class="mk-box"><b>전공 기반 추천</b><span class="mk-ref">전공 설명과 연계 직무를 먼저 확인하세요.</span><div class="mk-two"><span><span class="mk-lbl">전공</span><br><b>데이터테크전공</b></span>'
                '<span><span class="mk-lbl">추천 직무</span><br><span class="mk-pills"><span>시스템소프트웨어개발자</span><span>응용소프트웨어개발자</span><span>데이터분석가</span></span></span></div></div>'
                f'<button type="button" class="mk-card" data-on data-show="[data-sk]" data-goal><strong>핵심 역량</strong><span class="mk-ref">현재까지 학습한 과목 기반으로 분석한 대표 스킬</span><span class="mk-pills">{sk}</span><span class="mk-bars">{bars}</span></button>'
                '<div class="mk-box tint" data-sk hidden><b>과목 기반 스킬 통계</b><span>지금까지 들은 과목의 스킬셋을 분석한 결과예요. 가장 높은 「응용 능력」을 살릴 수 있는 직무를 추천해 줘요.</span></div>'
                '<div class="mk-box"><div class="mk-row"><b>나의 질문 기록</b><span class="mk-eg">체험용 예시 수치</span></div><div class="mk-bars"><div class="mk-bar2"><span>3월</span><i style="--v:85%"></i><b>34</b></div><div class="mk-bar2"><span>4월</span><i style="--v:55%"></i><b>22</b></div><div class="mk-bar2"><span>5월</span><i style="--v:8%"></i><b>3</b></div></div></div>')
        return frame(TH, sd('dash'), ('HAI-Way', '대시보드'), main)
    def cur():
        C = [('511644', 'C프로그래밍', '3학년', '3', '90%'), ('506203', '컴퓨터프로그래밍', '4학년', '3', '85%'), ('511702', '자료구조', '2학년', '3', '82%')]
        tb = '<table class="mk-tbl"><tr><th>과목번호</th><th>과목명</th><th>학년(수준)</th><th>학점</th><th>매칭도</th></tr>' + ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td><td><span class="mk-st ok">{e}</span></td></tr>' for a, b, c, d, e in C) + '</table>'
        main = ('<div class="mk-h"><h3>커리큘럼 추천</h3></div><div class="mk-box" data-c0><span class="mk-ref">왼쪽 메뉴에서 「커리큘럼 추천」을 누르면 희망 직무에 맞는 과목 로드맵을 만들어 줘요.</span></div>'
                '<div data-c1 hidden style="display:flex;flex-direction:column;gap:12px"><div class="mk-box"><b>시스템소프트웨어개발자 학습 로드맵</b><div class="mk-pills"><span class="on">기초</span><span>C프로그래밍</span><span>자료구조</span><span class="on">응용</span><span>운영체제</span><span>시스템프로그래밍</span><span class="on">심화</span><span>임베디드시스템</span></div></div>'
                f'<div class="mk-box"><div class="mk-row"><b>2026-1학기 추천 커리큘럼</b><span class="mk-eg">체험용 예시 과목</span></div><span class="mk-ref">시스템소프트웨어개발자를 위한 맞춤 추천이에요. 기초부터 차근차근 들을 수 있게 순서를 잡아 줘요.</span>{tb}</div></div>')
        return frame(TH, sd('dash', 'cur'), ('HAI-Way', '커리큘럼 추천'), main)
    def job(tab):
        tabs = ''.join(f'<button type="button" class="{"on" if k == 2 else ""}" data-on data-hide="[data-jt]" data-show="[data-jt={chr(39)}{k}{chr(39)}]"{" data-goal" if k == tab else ""}>{t}</button>' for k, t in enumerate(['커리큘럼 기반 매칭', '성향검사 기반 매칭', '선택한 희망 직무']))
        bars = ''.join(f'<div class="mk-bar2"><span>{l}</span><i style="--v:{v}%"></i><b>{v}%</b></div>' for l, v in [('기초 단계', 65), ('응용 단계', 60)])
        p0 = ('<div data-jt="0" hidden style="display:flex;flex-direction:column;gap:12px"><div class="mk-box tint"><b>직무 학습 로드맵</b><span>내가 들은 과목의 스킬셋을 기준으로 나와 가장 가까운 직무와, 그 직무에 필요한 과목 로드맵을 추천해요.</span></div>'
              f'<div class="mk-box"><b>학습 단계별 적합도</b><div class="mk-bars">{bars}</div></div><div class="mk-grid"><div class="mk-card"><strong>VFX아티스트(일반)</strong><span class="mk-ref">영상 특수효과 제작</span></div><div class="mk-card"><strong>VFX디자이너</strong><span class="mk-ref">시각효과 디자인</span></div><div class="mk-card on"><strong>시스템소프트웨어개발자</strong><span class="mk-ref">운영체제·시스템 개발</span></div></div></div>')
        p1 = ('<div data-jt="1" hidden style="display:flex;flex-direction:column;gap:12px"><div class="mk-box tint"><b>직업성향검사 기반 직무 매칭</b><span>STRONG 직무 성향검사 결과를 바탕으로 나에게 맞는 직무를 추천하고, 왜 맞는지 설명해 줘요.</span></div>'
              '<div class="mk-box"><div class="mk-row"><b>STRONG 검사 결과</b><span class="mk-eg">체험용 예시 결과</span></div><div class="mk-bars">' + ''.join(f'<div class="mk-bar2"><span>{l}</span><i style="--v:{v}%"></i><b>{v}</b></div>' for l, v in [('탐구형(I)', 82), ('현실형(R)', 64), ('관습형(C)', 51), ('예술형(A)', 38)]) + '</div><span>탐구형이 가장 높아요. 분석하고 문제를 푸는 일을 좋아하는 성향이라 개발·데이터 분석 직무와 잘 맞아요.</span></div></div>')
        p2 = '<div class="mk-box" data-jt="2"><b>선택한 희망 직무</b><span>시스템소프트웨어개발자</span><span class="mk-ref">위 탭을 눌러 다른 기준으로 나에게 맞는 직무를 찾아볼 수 있어요.</span></div>'
        return frame(TH, sd('job'), ('HAI-Way', '직무 매칭'), '<div class="mk-h"><h3>직무 매칭</h3></div><div class="mk-tabs">' + tabs + '</div>' + p0 + p1 + p2)
    I = 'media/walk/hai-way/'
    return [
        dict(title='통합 SSO로 로그인해요', text='○○대학교 계정(SSO)으로 바로 로그인해요.', do='「로그인」을 눌러 통합 SSO로 들어가 보세요.', img=I + '1.jpg',
             ui=login(TH, ('○○ UNIVERSITY', 'Think Beyond,<br>Together Grow', '○○대학교 통합 로그인'), ('한국어 · English', '로그인'), [('ID', 'ID', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', True, True)], foot='비밀번호 초기화 · 도움말')),
        dict(title='나의 대시보드를 봐요', text='전공 로드맵과 지금까지 들은 과목의 스킬셋 분석, 추천 직무를 대시보드로 확인해요.', do='「핵심 역량」 영역을 눌러 나의 스킬셋 분석을 확인해 보세요.', ui=dash(), img=I + '2.jpg'),
        dict(title='희망 직무에 맞는 커리큘럼을 받아요', text='희망 직무를 고르면 그 직무에 필요한 스킬셋을 기준으로 들어야 할 과목 로드맵을 만들어 줘요.', do='왼쪽 메뉴에서 「커리큘럼 추천」을 눌러 보세요.', ui=cur(), img=I + '3.jpg'),
        dict(title='나와 가까운 직무를 찾아요', text='내가 들은 과목의 스킬셋을 바탕으로 나와 가장 가까운 직무와 그 직무를 위한 로드맵을 추천해요.', do='「커리큘럼 기반 매칭」 탭을 눌러 나와 가까운 직무를 확인해 보세요.', ui=job(0), img=I + '4.jpg'),
        dict(title='성향검사로 직무를 매칭해요', text='STRONG 직무 성향검사 결과를 바탕으로 나에게 맞는 직무를 추천하고 설명해 줘요.', do='「성향검사 기반 매칭」 탭을 눌러 보세요.', ui=job(1), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Research (일반 사용자 매뉴얼)
def _research():
    TH = '--mk:#0d9488;--mk-side:#0f2f4a'
    TOP = '<div class="mk-box" style="background:var(--mk-side);color:#fff;border:0;flex-direction:row;justify-content:space-between;align-items:center"><b>○○대학교 · 연구자 탐색</b><span class="mk-pills"><span>매뉴얼 보기</span><span>연구자 로그인</span></span></div>'
    CARDS = [('연구자 A', '의학과', '줄기세포·조직 재생'), ('연구자 B', '바이오메디컬학과', '재생의학 소재'), ('연구자 C', '의학과', '임상 적용 연구')]
    def cards(goal=False):
        return ('<div class="mk-box" data-a{H}><b>매칭된 연구자의 상세 정보를 제공합니다</b><div class="mk-srcs">' + ''.join(f'<button type="button" class="mk-src" data-on data-hide="[data-pf]" data-show="[data-pf={chr(39)}{k}{chr(39)}]"{" data-goal" if goal and k == 0 else ""}><strong>{n}</strong><span>소속 {d}</span><span>연구분야 {f}</span></button>' for k, (n, d, f) in enumerate(CARDS)) + '</div>'
                + ''.join(f'<div class="mk-box tint" data-pf="{k}" hidden><div class="mk-row"><b>{n} 교수님</b><span class="mk-btn sm" style="cursor:default">프로필</span></div><span>소속: {d} · 연구분야: {f}</span><span class="mk-ref">주요 논문·과제·특허 목록과 연락처를 볼 수 있어요. (체험판에서는 실제 연구자 정보를 가렸어요)</span></div>' for k, (n, d, f) in enumerate(CARDS)) + '</div>')
    def chat(sample, ans, goal, answered=False, extra='', pre='', hide='[data-hello]'):
        hid = '' if answered else ' hidden'
        left = ('<div class="mk-log" id="mklog">' + ai('연구자를 찾으세요? 협업 내용 또는 RFP를 입력해보세요.', '', 'AI') + me(sample if answered else '', 'data-qa' + hid) + dots() + ai(demo(sample) + ans, 'data-a' + hid) + extra + '</div>'
                + inbar(sample, '찾고 싶은 기술을 입력해보세요 (예: 의료분야 AI 데이터…)', goal, pre=pre, hide=hide, more='체험판에서는 예시 요청 하나에만 답해 드려요. 실제 서비스에서는 연구자 데이터에서 맞는 분을 찾아 줘요.'))
        return left
    Q1 = '줄기세포 기반 재생의학 연구를 함께할 공동 연구자를 찾고 있어'
    A1 = '<p>줄기세포 기반 재생의학 분야에서 임상 적용 경험과 다양한 조직 재생 연구 실적을 보유한 교수님들이 추천됩니다. 오른쪽(아래)에서 연구자별 상세 정보를 확인해 보세요.</p>'
    def s1(): return frame(TH, '', ('HAI-Research', '연구자 탐색'), TOP + chat(Q1, A1, True) + cards().replace('{H}', ' hidden'))
    def s2(): return frame(TH, '', ('HAI-Research', '연구자 프로필'), TOP + '<div class="mk-log">' + me(Q1).replace(' data-q', '') + ai(A1) + '</div>' + cards(True).replace('{H}', ''))
    def s3():
        main = (TOP + '<div class="mk-row"><b>검색 결과</b><button type="button" class="mk-btn sm line" data-show="[data-w]">검색 가중치</button></div>' + cards().replace('{H}', '')
                + '<div class="mk-modal" data-w><b>검색 가중치</b><div class="mk-two"><label class="mk-f">주저자 (1~3)<input type="text" value="1" inputmode="numeric"><small style="font-weight:400">주저자 논문이 많은 교수님이 더 많이 검색됩니다.</small></label>'
                '<label class="mk-f">최근 연구 (년도 1~5 / 배수 1~3)<input type="text" value="2 · 1"><small style="font-weight:400">최근에 발간한 논문에 가중치를 더 줍니다.</small></label></div>'
                '<div class="mk-row end"><button type="button" class="mk-btn sm line" data-hide="[data-w]">취소</button><button type="button" class="mk-btn sm" data-hide="[data-w]" data-show="[data-rs]" data-goal>재검색</button></div></div>' + toast('data-rs', '가중치를 반영해 연구자를 다시 찾았어요.'))
        return frame(TH, '', ('HAI-Research', '검색 가중치'), main)
    Q4 = '의료분야 AI 팀 빌딩해줘'
    A4 = ('<p>의료 분야 AI 주제를 세부 연구로 나누고, 주제마다 맞는 교수님을 묶어 팀을 구성했어요.</p><p><b>#1</b> 의료 영상 진단을 위한 인공지능 모델 개발<br><b>#2</b> 환자 데이터 기반 질병 예측 인공지능 알고리즘 연구<br><b>#3</b> 의료 기록 자동 분석을 위한 자연어처리 기술 적용<br><b>#4</b> 웨어러블 헬스케어 데이터의 AI 기반 건강 모니터링</p>'
          '<p class="mk-ref">세부 주제별 추천 연구자는 「프로필 전체보기」에서 확인할 수 있어요.</p>')
    def s4(): return frame(TH, '', ('HAI-Research', '팀 빌딩'), TOP + chat(Q4, A4, True))
    def s5():
        clip = f'<button type="button" class="mk-ghost" style="border:0;background:none" data-show="[data-rfp]" data-goal aria-label="파일 첨부">{ic("clip", 18)}</button>'
        ans = '<p>RFP 내용을 분석해 과제에 맞는 연구자를 찾았어요. 요구 기술과 연구 실적이 가까운 순서로 보여 줘요.</p><span class="mk-eg">체험용 예시 답변</span>'
        return frame(TH, '', ('HAI-Research', 'RFP로 찾기'), TOP + chat('첨부한 RFP에 맞는 연구자를 찾아줘', ans, False, extra='<span class="mk-filechip" data-rfp hidden>' + ic('doc', 13) + 'RFP_예시.hwp 첨부됨 (체험용)</span>', pre=clip, hide='[data-none]'))
    I = 'media/walk/hai-research/'
    return [
        dict(title='협업 내용을 채팅으로 입력해요', text='찾고 싶은 기술이나 협업 내용을 채팅으로 입력하면, 연구 실적을 바탕으로 맞는 연구자를 추천해 줘요.', do='입력창에 찾고 싶은 협업 내용을 써서 보내 보세요. 비워 둔 채 보내면 예시가 입력돼요.', ui=s1(), img=I + '1.jpg'),
        dict(title='연구자 프로필을 자세히 봐요', text='추천된 연구자 카드를 누르면 소속, 연구 분야, 주요 논문·과제·특허를 자세히 볼 수 있어요.', do='매칭된 연구자 카드 가운데 첫 번째 카드를 눌러 상세 정보를 열어 보세요.', ui=s2(), img=I + '2.jpg'),
        dict(title='검색 가중치로 다시 찾아요', text='주저자 논문 수나 최근 연구에 가중치를 주어, 원하는 기준에 더 맞는 연구자를 다시 찾아요.', do='가중치를 고쳐 본 뒤 「재검색」을 눌러 다시 찾아보세요.', ui=s3(), img=I + '3.jpg'),
        dict(title='팀 빌딩을 요청해요', text='주제를 말하면 세부 연구로 나누고, 주제별로 맞는 연구자를 묶어 팀 구성을 제안해요.', do='입력창에 팀 빌딩을 요청해 보세요. 비워 둔 채 보내면 예시가 입력돼요.', ui=s4(), img=I + '4.jpg'),
        dict(title='RFP 파일로 연구자를 찾아요', text='과제 제안요청서(RFP) 파일을 첨부하면 그 내용에 맞는 연구자를 찾아 줘요.', do='입력창 왼쪽 클립 단추를 눌러 RFP 파일을 첨부해 보세요.', ui=s5(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-BDPI (응시자 매뉴얼)
def _bdpi():
    TH = '--mk:#0d9488;--mk-side:#134e4a'
    BAR = '<div class="mk-box" style="background:var(--mk);color:#fff;border:0;flex-direction:row;justify-content:space-between"><b>BDPI 성격검사</b><span>로그아웃</span></div>'
    def intro():
        main = (BAR + '<div class="mk-box"><b>BDPI 성격검사</b><span>안녕하세요. 응시하실 검사는 \'한국형 다차원 성격검사\'인 BDPI(Bright and Dark Personality Inventory)입니다.</span>'
                '<span>정답이 있는 검사가 아니니 평소 자신의 모습에 가깝게 솔직하게 응답해 주세요.</span>'
                '<span class="mk-ref">검사를 시작하려면 [시작]을, 이미 응시했다면 [결과 확인]을 눌러 주세요.</span></div>'
                '<div class="mk-row end"><button type="button" class="mk-btn" data-show="[data-st]" data-goal>시작</button><button type="button" class="mk-btn soft" data-go="3">결과 확인</button></div>' + toast('data-st', '검사를 시작했어요. 「다음」을 눌러 문항에 응답해 보세요.'))
        return frame(TH, '', ('BDPI', '검사 안내문'), main)
    def items():
        IT = ['나는 새로운 사람을 만나는 것이 즐겁다.', '나는 계획을 세워 일을 처리하는 편이다.', '나는 사소한 일에도 쉽게 걱정한다.', '나는 다른 사람의 감정을 잘 알아차린다.']
        sc = ''.join(f'<div class="mk-box"><b>{k + 1}　{t}</b><div class="mk-scale" data-sc>' + ''.join(f'<button type="button" data-on>{o}</button>' for o in ['전혀 그렇지 않다', '그렇지 않다', '그렇다', '매우 그렇다']) + '</div></div>' for k, t in enumerate(IT))
        main = (BAR + '<div class="mk-row"><b>다음의 문항을 보고 가장 자신의 모습과 가깝다고 생각하는 것에 응답해주세요.</b><span class="mk-eg">체험용 예시 문항</span></div>' + sc
                + '<p class="mk-demo" data-need hidden>모든 문항에 응답해야 다음 페이지로 넘어갈 수 있어요.</p><div class="mk-row end"><button type="button" class="mk-btn" data-allon="[data-sc]" data-show="[data-nx]" data-goal>다음으로</button></div>' + toast('data-nx', '응답을 저장하고 다음 페이지로 넘어갔어요.'))
        return frame(TH, '', ('BDPI', '성격검사 응시'), main)
    def result(goal):
        R = ['2026_08_12_홍길동_6회차', '2026_08_12_홍길동_5회차', '2026_08_11_홍길동_4회차']
        rows = ''.join(f'<div class="mk-rowbtn" style="cursor:default"><span>{r}</span><span class="mk-row"><button type="button" class="mk-btn sm line" data-show="[data-rp]"{" data-goal" if goal == "view" and k == 0 else ""}>보고서 보기</button>'
                       f'<button type="button" class="mk-btn sm" data-show="[data-dl]"{" data-goal" if goal == "pdf" and k == 0 else ""}>PDF 다운로드</button></span></div>' for k, r in enumerate(R))
        main = (BAR + '<div class="mk-two"><div class="mk-box"><b>본인확인</b><span>성명　홍길동</span><span>학번　H1234</span></div><div class="mk-box"><b>결과안내</b><span><b>홍길동</b>님의 BDPI 성격검사가 종료되었습니다.</span></div></div>'
                '<div class="mk-box"><b>결과 보고서</b>' + rows + '</div>'
                '<div class="mk-box" data-rp hidden style="background:linear-gradient(160deg,#bbf7d0,#86efac);border:0;align-items:center;text-align:center;padding:26px 14px"><b style="font-size:19px">5요인 성격 모델 기반<br>한국형 다차원 성격 검사</b><span>Bright Dark Personality Inventory</span><small>결과 보고서가 새 창에서 열려요. 요인별 프로파일과 해석을 볼 수 있어요.</small></div>'
                + toast('data-dl', 'PDF로 내려받았어요. (체험판에서는 파일이 만들어지지 않아요)'))
        return frame(TH, '', ('BDPI', '결과 확인'), main)
    I = 'media/walk/hai-bdpi/'
    return [
        dict(title='학번으로 로그인해요', text='○○대학교 통합 로그인 화면에서 학번과 비밀번호로 로그인해요.', do='학번과 비밀번호 칸을 확인하고 「로그인」을 눌러 보세요.', img=I + '1.jpg',
             ui=login(TH, ('○○ UNIVERSITY', 'The New University,<br>K-University of the Future', '○○대학교 통합 로그인'), ('한국어 · English', '로그인'), [('ID', 'ID', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', True, True)], foot='비밀번호 초기화 · 도움말')),
        dict(title='검사를 시작해요', text='검사 안내문을 읽고 「시작」을 누르면 성격검사가 시작돼요. 이미 응시했다면 「결과 확인」으로 바로 갈 수 있어요.', do='안내문을 읽었다면 「시작」을 눌러 검사를 시작해 보세요.', ui=intro(), img=I + '2.jpg'),
        dict(title='문항에 응답해요', text='각 문항에 솔직하게 응답하고 「다음으로」를 눌러요. 모든 문항에 답해야 다음 페이지로 넘어가요.', do='네 문항에 모두 응답한 뒤 「다음으로」를 눌러 보세요.', ui=items(), img=I + '3.jpg'),
        dict(title='결과 보고서를 확인해요', text='검사가 끝나면 결과 보고서가 만들어져요. 「보고서 보기」를 누르면 새 창에서 결과를 확인할 수 있어요.', do='첫 번째 보고서의 「보고서 보기」를 눌러 보세요.', ui=result('view'), img=I + '4.jpg'),
        dict(title='결과를 모아 보고 내려받아요', text='지금까지 응시한 회차별 보고서를 모아 보고, PDF 파일로 내려받을 수 있어요.', do='첫 번째 보고서의 「PDF 다운로드」를 눌러 보세요.', ui=result('pdf'), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Check (LIVECAT 관리자 매뉴얼)
def _check():
    TH = '--mk:#1e40af;--mk-side:#1e3a6e'
    def sd(active):
        return side('LIVECAT', '', [('', [('test', 'edit', 'TEST 등록'), ('pool', 'doc', '문항 pool'), ('res', 'chart', '결과 관리'), ('bank', 'mark', '문항은행'), ('org', 'user', '조직 권한 관리')])], active, go={'bank': 1, 'pool': 2, 'test': 3, 'res': 4})
    def flow():
        F = [('문항 등록', '문항의 분류·등급 등 기본 정보를 정하고 문항은행에 문항을 등록해요.'), ('문항Pool 생성', '이번 시험에 쓸 문항을 골라 시험지(문항Pool)를 만들어요.'), ('시험 생성', '문항Pool을 골라 시험(Test)을 만들고 응시자와 안내 문구를 설정해요.'), ('URL 배포', '시험마다 만들어지는 URL을 응시자에게 알려요.'), ('응시', '응시자는 URL로 접속해 웹에서 시험을 봐요.'), ('결과 확인', '응시 결과를 확인하고 엑셀 결과표로 내려받아요.')]
        fl = '<i>→</i>'.join(f'<button type="button" data-on data-hide="[data-fd]" data-show="[data-fd={chr(39)}{k}{chr(39)}]"{" data-goal" if k == 0 else ""}>{t}</button>' for k, (t, d) in enumerate(F))
        ds = ''.join(f'<div class="mk-box tint" data-fd="{k}" hidden><b>{k + 1}. {t}</b><span>{d}</span></div>' for k, (t, d) in enumerate(F))
        return frame(TH, sd(''), ('LIVECAT', '소개'), '<div class="mk-h"><h3>LIVECAT 소개</h3></div><p>LIVECAT의 기능 및 사용 상세 흐름은 아래와 같습니다. 단계를 눌러 보세요.</p><div class="mk-flow">' + fl + '</div>' + ds + '<p class="mk-ref">CBT(컴퓨터 기반 시험)와 맞춤형 CAT(적응형 시험)를 모두 웹에서 운영해요.</p>')
    def item():
        def row(l, opts, on=0, goal=False): return f'<div class="mk-f">{l}<div class="mk-pills">' + ''.join(f'<button type="button" class="{"on" if k == on else ""}" data-on{" data-goal data-show=[data-ar]" if goal and k == 0 else ""}>{o}</button>' for k, o in enumerate(opts)) + '</div></div>'
        main = ('<div class="mk-h"><h3>문항 등록</h3><span class="mk-badge">기본정보</span></div><div class="mk-box">' + row('① 교수명', ['홍길동'], 0) + row('② 영역', ['인지검사', '성격검사'], -1, True) + row('③ 문항구성유형', ['단일문항', '세트문항'], 0)
                + row('④ 분류', ['선택 안 함', '대분류', '중분류'], 0) + row('⑤ 문항등급', ['본문항', '예비문항'], 0) + row('⑥ 문항응답유형', ['선택형', '서술형'], 0) + '</div>' + toast('data-ar', '영역을 「인지검사」로 정했어요. 나머지 기본 정보도 눌러서 바꿔 볼 수 있어요.'))
        return frame(TH, sd('bank'), ('LIVECAT', '문항 등록'), main)
    def table(title, heads, rows, btn, form, done):
        tb = '<table class="mk-tbl"><tr>' + ''.join(f'<th>{h}</th>' for h in heads) + '</tr>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '<tr data-new hidden class="on">' + ''.join(f'<td>{c}</td>' for c in rows[0][:-1]) + '<td><span class="mk-st ing">방금 등록</span></td></tr></table>'
        return (f'<div class="mk-row"><div class="mk-h"><h3>{title}</h3></div><button type="button" class="mk-btn sm" style="background:#dc2626" data-show="[data-fm]" data-goal>{btn}</button></div>{tb}'
                f'<div class="mk-modal" data-fm hidden><b>{btn}</b>{form}<p class="mk-demo" data-need hidden>이름을 먼저 써 주세요.</p><div class="mk-row end"><button type="button" class="mk-btn sm line" data-hide="[data-fm]">취소</button><button type="button" class="mk-btn sm" data-req="#mknm" data-hide="[data-fm]" data-show="[data-new],[data-dn]">등록</button></div></div>' + toast('data-dn', done))
    def pool():
        main = table('구성중인 문항 Pool 목록', ['문항Pool명', '영역', 'Model', '확정여부', '사용여부'], [['CBT 2', '인지검사', 'CBT-시험지형', '확정', '<span class="mk-st ok">사용</span>'], ['CAT 2', '인지검사', 'CAT-Rasch', '확정', '<span class="mk-st ok">사용</span>']], '새 문항Pool 등록',
                     '<label class="mk-f">문항Pool명<input type="text" id="mknm" placeholder="예: 중간고사 시험지"></label><div class="mk-f">담을 문항 (눌러서 고르기)<div class="mk-pills"><button type="button" data-tg>문항 1</button><button type="button" data-tg>문항 2</button><button type="button" data-tg>문항 3</button></div></div>', '새 문항Pool을 등록했어요. 문항Pool은 이번 시험의 시험지예요.')
        return frame(TH, sd('pool'), ('LIVECAT', '문항 pool'), main)
    def test():
        main = table('등록중인 TEST 목록', ['조직명', '시험명', '진행', '등록자', '상태'], [['○○대학교', '중간고사', 'step3단계', '홍길동', '<span class="mk-st ok">완료</span>'], ['○○대학교', 'CAT 테스트', 'step3단계', '홍길동', '<span class="mk-st ok">완료</span>']], '새 TEST 등록',
                     '<label class="mk-f">TEST 명<input type="text" id="mknm" placeholder="예: 기말고사"></label><label class="mk-f">문항Pool<select><option>CBT 2</option><option>CAT 2</option></select></label><label class="mk-f">응시자 안내 문구<textarea placeholder="응시자에게 보일 안내 문구"></textarea></label>', '새 시험을 만들었어요. 시험마다 응시용 URL이 만들어져요.')
        return frame(TH, sd('test'), ('LIVECAT', 'TEST 등록'), main)
    def res():
        main = ('<div class="mk-h"><h3>결과관리</h3></div><table class="mk-tbl"><tr><th>조직명</th><th>테스트명</th><th>응시인원</th><th>진행일</th></tr><tr class="on"><td>○○대학교</td><td><button type="button" data-show="[data-pv]">중간고사</button></td><td>0/22</td><td>2026-08-18 ~ 2026-08-18</td></tr><tr><td>○○대학교</td><td>CAT 테스트</td><td>0/22</td><td>2026-08-18 ~ 2026-08-18</td></tr></table>'
                '<div class="mk-modal" data-pv><b>미리보기</b><span class="mk-lbl">TEST 기본정보</span><span>TEST 명　중간고사<br>대상자 정보　지속관리형 · 22명<br>TEST url　https://…/takerlogin (응시용 주소)</span><span class="mk-lbl">결과관리</span>'
                '<div class="mk-row"><span>결과표</span><button type="button" class="mk-btn sm" style="background:#15803d" data-show="[data-dl]" data-goal>' + ic('down', 14) + '다운로드</button></div>' + toast('data-dl', '응시 결과를 엑셀 결과표로 내려받았어요. (체험판에서는 파일이 만들어지지 않아요)') + '</div>')
        return frame(TH, sd('res'), ('LIVECAT', '결과 관리'), main)
    I = 'media/walk/hai-check/'
    return [
        dict(title='전체 흐름을 먼저 봐요', text='문항 등록 → 문항Pool 생성 → 시험 생성 → URL 배포 → 응시 → 결과 확인 순서로 진행해요. CBT와 맞춤형 CAT 모두 웹에서 운영해요.', do='흐름의 첫 단계 「문항 등록」을 눌러 설명을 확인해 보세요.', ui=flow(), img=I + '1.jpg'),
        dict(title='문항을 등록해요', text='문항의 분류와 등급 등 기본 정보를 정하고 문항을 등록해요.', do='기본 정보에서 「② 영역」을 「인지검사」로 골라 보세요.', ui=item(), img=I + '2.jpg'),
        dict(title='문항Pool(시험지)을 구성해요', text='문항Pool은 시험지와 같아요. 「문항Pool구성」 → 「새 문항Pool 등록」에서 이번 시험에 쓸 문항을 골라 담아요.', do='「새 문항Pool 등록」을 눌러 등록 창을 열어 보세요.', ui=pool(), img=I + '3.jpg'),
        dict(title='시험(Test)을 만들어요', text='「Test 등록」에서 「새 Test 등록」을 눌러 시험을 만들고 응시자와 안내 문구를 설정해요.', do='「새 TEST 등록」을 눌러 등록 창을 열어 보세요.', ui=test(), img=I + '4.jpg'),
        dict(title='결과를 확인하고 내려받아요', text='「결과 관리」에서 검사를 고르고 「다운로드」를 누르면 응시 결과를 엑셀 결과표로 받을 수 있어요.', do='미리보기 아래 결과표의 「다운로드」를 눌러 보세요.', ui=res(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-LRS (학생 대시보드 안내)
def _lrs():
    TH = '--mk:#0d9488;--mk-side:#134e4a'
    HEAD = '<div class="mk-row"><div class="mk-h"><h3>HAI-LRS 학습분석</h3></div><div class="mk-pills"><span class="on">학생</span><span>교수</span><span>운영자</span></div></div><p class="mk-ref">학생　사회학과 4학년 (이름과 학번은 가렸어요)</p>'
    def bar(l, v, pct, goal=False, key=''): return f'<button type="button" class="mk-bar2" data-on data-hide="[data-bd]" data-show="[data-bd={chr(39)}{key}{chr(39)}]"{" data-goal" if goal else ""}><span>{l}</span><i style="--v:{pct}%"></i><b>{v}</b></button>'
    def home():
        C = [('진로 경험 레이더', '상위 1%', '비교과 · 가장 높은 축', True), ('나의 역량 프로필', '탐구 36%', '가장 두터운 이수 역량', False), ('마이크로디그리 진행', '8/13과목', '가장 가까운 과정 · 일반사회학전공트랙', False), ('선배 수강 경험', '1,639과목', '부담 × 진로 도움 사분면', False)]
        cards = ''.join(f'<button type="button" class="mk-card" data-on data-show="[data-cd]"{" data-goal" if g else ""}><span class="mk-ref">{t}</span><strong style="font-size:18px;color:var(--mk)">{v}</strong><span class="mk-chip">{d}</span></button>' for t, v, d, g in C)
        return frame(TH, '', ('HAI-LRS', '학습분석'), HEAD + f'<div class="mk-grid two">{cards}</div><div class="mk-box tint" data-cd hidden><b>카드를 누르면 자세한 분석으로 들어가요</b><span>동기 대비 나의 경험 위치, 이수 과목이 쌓아 준 역량, 마이크로디그리까지 남은 과목, 선배들의 수강 경험을 차례로 볼 수 있어요.</span></div>')
    def radar():
        B = [('수강·이수(전공)', 54), ('성취', 98), ('비교과', 100), ('상담', 41), ('어학·수상', 100)]
        return frame(TH, '', ('HAI-LRS', '진로 경험 레이더'), HEAD + '<div class="mk-box"><div class="mk-row"><b>진로 경험 레이더 <small>동기 대비 나의 경험 위치 확인</small></b></div><b style="font-size:20px;color:var(--mk)">상위 1% <span class="mk-chip">비교과 · 가장 높은 축</span></b>'
                     '<span class="mk-ref">동기 속 내 위치(백분위)</span><div class="mk-bars">' + ''.join(bar(l, v, v, l == '비교과', str(k)) for k, (l, v) in enumerate(B)) + '</div>'
                     + ''.join(f'<p class="mk-note" data-bd="{k}" hidden><span><b>{l}</b> 영역에서 나는 동기 가운데 백분위 {v}에 있어요.</span></p>' for k, (l, v) in enumerate(B)) + '<span class="mk-ref">사회과학대학 동기 116명 기준 · 8학기차 시점 · 백분위 33 미만 축은 없음</span></div>')
    def comp():
        B = [('탐구', 36), ('기술', 33), ('도전', 16), ('직무', 15)]
        return frame(TH, '', ('HAI-LRS', '나의 역량 프로필'), HEAD + '<div class="mk-box"><b>나의 역량 프로필 <small>이수 과목 기반 나의 역량 구성 분석</small></b><b style="font-size:20px;color:var(--mk)">탐구 36% <span class="mk-chip">가장 두터운 이수 역량</span></b>'
                     '<span class="mk-ref">들은 과목이 쌓아 준 역량 (Hi FIVE 누적 · 2026-2 · 커버리지 61.9%)</span><div class="mk-bars">' + ''.join(bar(l, f'{v}%', v * 2.5, l == '탐구', str(k)) for k, (l, v) in enumerate(B)) + '</div>'
                     + ''.join(f'<p class="mk-note" data-bd="{k}" hidden><span>이수한 과목 가운데 <b>{l}</b> 역량에 기여한 비중이 {v}%예요.</span></p>' for k, (l, v) in enumerate(B)) + '</div>')
    def micro():
        B = [('일반사회학전공트랙', '8/13', 62), ('문화기획 전공트랙', '4/7', 57), ('글로벌 지속가능발전트랙', '8/20', 40), ('기후변화정책트랙', '8/20', 40)]
        return frame(TH, '', ('HAI-LRS', '마이크로디그리 진행'), HEAD + '<div class="mk-box"><b>마이크로디그리 진행 <small>이수 과목과 트랙 요건의 겹침 확인</small></b><b style="font-size:20px;color:var(--mk)">8/13과목 <span class="mk-chip">가장 가까운 과정 · 일반사회학전공트랙</span></b>'
                     '<span class="mk-ref">이미 들은 과목으로 채워진 트랙</span><div class="mk-bars" style="--w:150px">' + ''.join(bar(l, v, p, k == 0, str(k)).replace('class="mk-bar2"', 'class="mk-bar2" style="grid-template-columns:150px 1fr 44px"') for k, (l, v, p) in enumerate(B)) + '</div>'
                     + ''.join(f'<p class="mk-note" data-bd="{k}" hidden><span><b>{l}</b>: 요건 과목 가운데 {v}를 이미 들었어요. 상세에서 남은 과목을 볼 수 있어요.</span></p>' for k, (l, v, p) in enumerate(B)) + '<span class="mk-ref">겹침 상위 4개 트랙 · 상세에서 과정을 눌러 남은 과목을 보세요</span></div>')
    def senior():
        Q = [('쉽고 남는 수업', 364), ('힘들지만 남는 수업', 456), ('쉽고 가벼운 수업', 455), ('힘들고 가벼운 수업', 364)]
        return frame(TH, '', ('HAI-LRS', '선배 수강 경험'), HEAD + '<div class="mk-box"><b>선배 수강 경험 <small>과목별 학습 부담과 진로 도움 비교</small></b><span class="mk-ref">선배 후기 1,639과목 · 부담 × 진로 도움 사분면</span><div class="mk-quad">'
                     + ''.join(f'<button type="button" data-on data-hide="[data-bd]" data-show="[data-bd={chr(39)}{k}{chr(39)}]"{" data-goal" if k == 1 else ""}><span>{l}</span><b>{v}</b></button>' for k, (l, v) in enumerate(Q)) + '</div>'
                     + ''.join(f'<p class="mk-note" data-bd="{k}" hidden><span>선배들이 <b>{l}</b>으로 평가한 과목이 {v}개예요. 상세에서 과목별 한 줄 평가를 볼 수 있어요.</span></p>' for k, (l, v) in enumerate(Q)) + '<span class="mk-ref">내가 들은 42과목의 부담 중앙값 68.1 (전체 72.2)</span></div>')
    I = 'media/walk/hai-lrs/'
    return [
        dict(title='나의 학습 대시보드를 열어요', text='학생 대시보드에서는 진로 경험, 역량 프로필, 마이크로디그리 진행, 선배 수강 경험을 카드로 한눈에 봐요.', do='대시보드에서 「진로 경험 레이더」 카드를 눌러 보세요.', ui=home(), img=I + '1.jpg'),
        dict(title='진로 경험 레이더를 봐요', text='수강·성취·비교과·상담·어학·수상 다섯 축에서 동기들과 비교한 나의 위치(백분위)를 확인해요.', do='다섯 축 가운데 값이 가장 높은 「비교과」 막대를 눌러 보세요.', ui=radar(), img=I + '2.jpg'),
        dict(title='나의 역량 프로필을 확인해요', text='지금까지 들은 과목이 어떤 역량을 얼마나 쌓아 주었는지 비율로 보여 줘요.', do='가장 두터운 역량인 「탐구」 막대를 눌러 보세요.', ui=comp(), img=I + '3.jpg'),
        dict(title='마이크로디그리에 얼마나 가까운지 봐요', text='이미 들은 과목이 어느 마이크로디그리 트랙 요건과 겹치는지, 몇 과목이 남았는지 확인해요.', do='가장 가까운 과정 「일반사회학전공트랙」을 눌러 보세요.', ui=micro(), img=I + '4.jpg'),
        dict(title='선배들의 수강 경험을 참고해요', text='선배 후기를 바탕으로 과목의 학습 부담과 진로 도움 정도를 네 영역으로 나눠 보여 줘요.', do='「힘들지만 남는 수업」 칸을 눌러 보세요.', ui=senior(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Sync (소개자료)
def _sync():
    TH = '--mk:#7c3aed;--mk-side:#1e1b4b'
    NAV = '<div class="mk-topbar"><div class="mk-h"><h3>3주차 1차시 - 아들의 지능은 엄마가 결정한다</h3></div><span class="mk-chip">생명과학의 세계</span></div>'
    def tabs(on, goal=''):
        return '<div class="mk-tabs">' + ''.join(f'<button type="button" class="{"on" if k == on else ""}" data-on data-hide="[data-tb]" data-show="[data-tb={chr(39)}{k}{chr(39)}]"{" data-goal" if t == goal else ""}>{t}</button>' for k, t in enumerate(['요약', '퀴즈', '게임'])) + '</div>'
    SUM = ('<div class="mk-box" data-tb="0"{H0}><b>요약</b><span>본 강의는 유전적 변이의 기본 개념인 드노보 변이(De novo variant)부터 최신 유전학의 핵심인 다인자 유전(Polygenic) 모델까지 폭넓게 다룹니다.</span>'
           '<b>드노보 변이(De novo variant)의 정의와 발생 과정 <span class="mk-chip">수업 녹음</span> <span class="mk-chip">강의자료</span></b><span>드노보(De novo)는 \'새롭게 발생한\'이라는 의미로, 부모에게는 없지만 자녀에게 처음 나타나는 유전 변이를 뜻해요.</span>'
           '<div class="mk-row"><button type="button" class="mk-btn sm soft" data-show="[data-src]"{G0}>' + ic('doc', 14) + '강의자료 보기</button><button type="button" class="mk-btn sm" data-go="4">AI에게 질문하기</button></div>'
           '<div class="mk-box tint" data-src hidden><b>원문 출처</b><span>요약 문단마다 근거가 된 강의자료 쪽과 수업 녹음 구간이 연결돼 있어 원문을 바로 확인할 수 있어요.</span><span class="mk-filechip">' + ic('doc', 13) + '[학습자료] 생명과학의 세계 · 3주차 강의자료</span></div></div>')
    OPT = ['염색체(Chromosome)', '유전자(Gene)', '아미노산(Amino acid)', '표현형(Phenotype)', '대립유전자(Allele)']
    QUIZ = ('<div class="mk-box" data-tb="1"{H1}><span class="mk-chip">Q1 · 용어 퀴즈</span><b>다음 설명에 알맞은 용어를 고르시오.</b><span>설명: 단백질을 생성하는 유전 정보의 기본 단위로, 모든 사람이 공통적으로 보유하고 있는 생물학적 설계도를 의미한다.</span>'
            '<div class="mk-opts" id="mko">' + ''.join(f'<button type="button" class="mk-opt" data-on>{o}</button>' for o in OPT) + '</div><p class="mk-demo" data-need hidden>먼저 답을 하나 골라 주세요.</p>'
            '<div class="mk-box tint" data-right hidden><b>정답이에요! 유전자(Gene)</b></div><div class="mk-box tint" data-wrong hidden><b>아쉬워요. 정답은 유전자(Gene)예요.</b></div><div class="mk-row end"><button type="button" class="mk-btn sm" data-check="#mko|1">정답 확인</button></div></div>')
    GAME = '<div class="mk-box" data-tb="2" hidden><b>학습 게임</b><span class="mk-ref">회차 내용으로 만든 학습 게임이에요. 체험판에는 들어 있지 않아요.</span></div>'
    def setup(goal):
        def lst(items, kind): return ''.join(f'<button type="button" class="mk-rowbtn" data-tg><span>[{kind}] {t}</span><small>OFF</small></button>' for t in items)
        main = ('<div class="mk-modal"><div class="mk-row"><b>회차 설정</b><span class="mk-ref">3주차 1차시</span></div><div class="mk-two"><div class="mk-box" id="mkdoc"><div class="mk-row"><b>강의자료 저장소 <small>(53개)</small></b><button type="button" class="mk-btn sm" style="background:#b91c1c" data-show="[data-nf]"' + (' data-goal' if goal == 'add' else '') + '>강의자료 추가하기</button></div>'
                + '<button type="button" class="mk-rowbtn" data-tg data-nf hidden><span>[학습자료] 새로 올린 강의자료.pdf (체험용)</span><small>OFF</small></button>' + lst(['생명과학의 세계_150202_헤이크로바이올…', '생명과학의 세계_150201_마이크로바이옴…'], '학습자료') + '</div>'
                '<div class="mk-box"><div class="mk-row"><b>녹음본 저장소 <small>(57개)</small></b><span class="mk-btn sm" style="background:#b91c1c;cursor:default">녹음본 추가하기</span></div>' + lst(['생명과학의 세계_140202_식물의 저대사산물과…', '생명과학의 세계_140201_식물의 저대사산물과…'], '녹음본') + '</div></div>'
                '<p class="mk-demo" data-need hidden>회차에 쓸 강의자료를 하나 이상 눌러 골라 주세요.</p><div class="mk-row end"><span class="mk-btn sm line" style="cursor:default">닫기</span><button type="button" class="mk-btn sm" data-allon="#mkdoc" data-wait="[data-mk]" data-show="[data-made]"' + (' data-goal' if goal == 'make' else '') + '>적용하고 콘텐츠 생성</button></div>'
                '<p class="mk-note" data-mk hidden><span>AI가 강의자료와 녹음을 학습하고 있어요…</span></p><div class="mk-box tint" data-made hidden><b>회차별 학습 콘텐츠가 만들어졌어요</b><span>요약 노트, 연습 퀴즈, 학습 게임, AI 튜터가 이 회차에 준비됐어요.</span><span class="mk-eg">체험용 예시</span></div></div>')
        return frame(TH, '', ('HAI-Sync', '회차 설정'), main)
    Q = '유전자와 대립유전자의 차이가 무엇인가요?'
    def tutor():
        body = (demo(Q) + '<p>제공된 강의자료에 따르면, <b>유전자(Gene)</b>는 단백질을 만들어내는 정보의 단위로 모든 사람이 가지고 있는 반면, <b>대립유전자(Allele)</b>는 유전자 DNA 상의 변화, 즉 유전 변이에 해당해 사람마다 다르게 나타나요.</p>'
                '<p class="mk-ref">근거 ' + f'<span class="mk-filechip">{ic("doc", 13)}수업 녹음본 · 녹음 구간 #3 (6:01 – 9:33)</span></p>')
        return frame(TH, '', ('HAI-Sync', 'AI 튜터'), NAV + '<div class="mk-log" id="mklog"><div class="mk-hello" data-hello><b>대화형 AI 튜터</b><span>무엇이든 질문하면 강의 내용에 근거해 답하고, 근거 페이지까지 짚어 줘요.</span><div class="mk-chips"><button type="button" data-fill="' + Q + '">' + Q + '</button></div></div>'
                     + me('', 'data-qa hidden') + dots() + ai(body, 'data-a hidden') + '</div>' + inbar(Q, '무엇이든 물어보세요…', True, more='체험판에서는 예시 질문 하나에만 답해 드려요. 실제 서비스에서는 올린 강의자료와 녹음을 근거로 답합니다.'))
    I = 'media/walk/hai-sync/'
    return [
        dict(title='강의자료와 녹음을 올려요', text='교수님은 강의자료와 수업 녹음을 올리기만 하면 되고, 학생은 언제든 질문하며 복습해요.', do='「강의자료 추가하기」를 눌러 강의자료를 올려 보세요.', ui=setup('add'), img=I + '2.jpg'),
        dict(title='강의자료·녹음을 자동으로 학습해요', text='자료와 녹음을 올리면 AI가 회차별 학습 콘텐츠를 자동으로 만들어요.', do='쓸 강의자료를 눌러 고른 뒤 「적용하고 콘텐츠 생성」을 눌러 보세요.', ui=setup('make'), img=I + '2.jpg'),
        dict(title='AI 요약 노트로 복습해요', text='회차 전체를 구조화한 요약 노트에 문단마다 강의자료·녹음 출처가 붙어 있어 원문을 바로 확인해요.', do='요약 노트에서 「강의자료 보기」를 눌러 원문 출처를 확인해 보세요.', ui=frame(TH, '', ('HAI-Sync', '요약 노트'), NAV + tabs(0) + SUM.replace('{H0}', '').replace('{G0}', ' data-goal') + QUIZ.replace('{H1}', ' hidden') + GAME), img=I + '3.jpg'),
        dict(title='퀴즈와 게임으로 반복해요', text='회차마다 연습 퀴즈와 학습 게임으로 재미있게 반복 학습해요.', do='「퀴즈」 탭을 눌러 연습 퀴즈를 열고 풀어 보세요.', ui=frame(TH, '', ('HAI-Sync', '퀴즈'), NAV + tabs(0, '퀴즈') + SUM.replace('{H0}', '').replace('{G0}', '') + QUIZ.replace('{H1}', ' hidden') + GAME), img=I + '4.jpg'),
        dict(title='AI 튜터에게 언제든 물어봐요', text='궁금한 건 대화형 AI 튜터에게 물어보면 강의 내용을 근거로 답하고 근거 페이지까지 짚어 줘요.', do='AI 튜터에게 궁금한 것을 써서 보내 보세요. 비워 둔 채 보내면 예시 질문이 입력돼요.', ui=tutor(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Security (소개자료)
def _security():
    TH = '--mk:#2563eb;--mk-side:#0f172a'
    def sd(active, prof=False):
        items = [('ov', 'chart', '과목 관리'), ('pr', 'user', '진도 관리'), ('qz', 'edit', '퀴즈 관리')] if prof else [('dash', 'home', '대시보드'), ('crs', 'doc', '과목'), ('my', 'chart', '내 진도'), ('qna', 'chat', '문의사항'), ('ntc', 'bell', '공지사항')]
        return side('HAI-Security', '', [('', items)], active, user=(('교수자', '관리자') if prof else ('학생', '수강생')), light=True, go=({} if prof else {'dash': 0, 'crs': 1}))
    def dash():
        main = ('<div class="mk-h"><h3>대시보드</h3></div><p class="mk-ref">수강 중인 과목과 학습 진행 상황을 한눈에 확인하세요.</p>'
                '<button type="button" class="mk-box tint" style="text-align:left" data-show="[data-st]" data-goal><b>오늘의 학습을 시작할 준비가 되었습니다</b><span>과목에 등록하면 이곳에서 실습 시나리오·퀴즈와 나의 진도를 확인할 수 있습니다.</span></button>'
                '<div class="mk-stats"><div class="mk-stat"><small>수강 과목</small><b>1</b></div><div class="mk-stat"><small>평균 학습 완료율</small><b>25%</b></div><div class="mk-stat"><small>해결 시나리오</small><b>0</b></div></div>'
                '<div class="mk-two"><div class="mk-box"><b>공지사항</b><span class="mk-ref">등록된 공지사항이 없습니다.</span></div><div class="mk-box"><b>오늘의 학습 포커스</b><span>네트워크 보안</span></div></div>' + toast('data-st', '오늘의 학습을 시작했어요. 「다음」을 눌러 실습으로 들어가 보세요.'))
        return frame(TH, sd('dash'), ('HAI-Security', '대시보드'), main)
    Q = '학습 목표를 알려줄 수 있어?'
    def lab():
        body = demo(Q) + '<p>학습 목표는 다음과 같습니다.</p><p>1. Wireshark의 패킷 목록, 패킷 상세 정보, 원시 바이트 영역을 구분할 수 있습니다.<br>2. 캡처 필터와 디스플레이 필터의 차이를 설명할 수 있습니다.<br>3. ARP, ICMP, DNS, TCP, HTTP 패킷의 주요 필드를 찾을 수 있습니다.<br>4. TCP 3-way handshake와 하나의 TCP 스트림을 추적할 수 있습니다.</p>'
        aside = ('<aside class="mk-aside mk-keep" style="width:260px"><b>' + ic('chat', 14) + ' AI 튜터</b><div class="mk-log" id="mklog" style="min-height:150px"><div class="mk-chips" data-hello><button type="button" data-fill="' + Q + '">' + Q + '</button></div>' + me('', 'data-qa hidden') + dots('T') + ai(body, 'data-a hidden', 'T') + '</div>' + inbar(Q, '질문을 입력하세요…', True) + '</aside>')
        main = ('<div class="mk-h"><h3>Wireshark로 시작하는 네트워크 패킷 분석</h3><span class="mk-badge">실습</span></div><div class="mk-box"><b>실습 개요</b><table class="mk-tbl"><tr><th>항목</th><th>내용</th></tr><tr><td>난이도</td><td>초급</td></tr><tr><td>권장 시간</td><td>150분</td></tr><tr><td>실습 도구</td><td>Wireshark 4.x 권장</td></tr><tr><td>제출물</td><td>문항 답안, 필터식, 캡처 화면, 사고분석 보고서</td></tr></table></div>'
                '<div class="mk-box"><b>학습 목표</b><span class="mk-ref">실습을 마치면 Wireshark 화면 구성과 필터, 주요 프로토콜 패킷을 읽을 수 있어요. 막히면 AI 튜터에게 물어보세요.</span></div>')
        return frame(TH, sd('crs'), ('HAI-Security', 'AI Tutor'), main, aside)
    def ctf(goal):
        L = ['Aug 21, 2025 @ 02:00:01.894　Microsoft-Windows-Sysmon/Operational　process_create', 'Aug 21, 2025 @ 02:00:00.917　Microsoft-Windows-Sysmon/Operational　network_connect', 'Aug 21, 2025 @ 01:59:58.004　Microsoft-Windows-Security-Auditing　logon']
        rows = ''.join(f'<button type="button" class="mk-rowbtn" style="font:11.5px ui-monospace,monospace" data-on data-show="[data-ld]"{" data-goal" if goal == "log" and k == 0 else ""}><span>{l}</span></button>' for k, l in enumerate(L))
        main = ('<div class="mk-h"><h3>실전형 CTF 플랫폼</h3><span class="mk-badge">2,847 hits</span></div><p class="mk-ref">실제 공격 데이터를 분석해 위협 행위를 찾아내는 문제예요. 로그를 눌러 자세히 살펴보세요.</p><div class="mk-opts">' + rows + '</div>'
                '<div class="mk-box tint" data-ld hidden><b>로그 상세</b><span style="font:11.5px ui-monospace,monospace">event_data.Image: C:\\Windows\\System32\\cmd.exe<br>event_data.ParentImage: (상위 프로세스)<br>computer_name: DESKTOP-…</span><span class="mk-eg">체험용 예시 로그</span></div>'
                '<div class="mk-box"><b>정답(플래그) 제출</b><div class="mk-row"><input type="text" id="mkflag" class="mk-grow" placeholder="찾아낸 답을 입력하세요" aria-label="정답 입력"><button type="button" class="mk-btn sm" data-req="#mkflag" data-show="[data-sb]"' + (' data-goal' if goal == 'flag' else '') + '>제출</button></div>'
                '<p class="mk-demo" data-need hidden>답을 먼저 입력해 주세요.</p>' + toast('data-sb', '답을 제출했어요. 자동 채점 결과가 바로 나와요. (체험판에서는 채점되지 않아요)') + '</div>')
        return frame(TH, sd('crs'), ('HAI-Security', 'CTF'), main)
    def prof():
        main = ('<div class="mk-row"><div class="mk-h"><h3>강좌 종합 현황</h3></div><span class="mk-row"><span class="mk-btn sm line" style="cursor:default">퀴즈 운영</span><button type="button" class="mk-btn sm" data-show="[data-pg]" data-goal>상세 진도 보기</button></span></div>'
                '<div class="mk-stats"><div class="mk-stat"><small>수강생</small><b>7명</b></div><div class="mk-stat"><small>평균 진도</small><b>6.4%</b></div><div class="mk-stat"><small>진행 중 과제</small><b>1</b></div><div class="mk-stat"><small>퀴즈</small><b>7</b></div></div>'
                '<div class="mk-box" data-pg hidden><div class="mk-row"><b>학생별 진도</b><span class="mk-eg">체험용 예시</span></div><div class="mk-bars">' + ''.join(f'<div class="mk-bar2"><span>학생 {k + 1}</span><i style="--v:{v}%"></i><b>{v}%</b></div>' for k, v in enumerate([25, 10, 5, 0])) + '</div></div>'
                '<div class="mk-box"><b>확인이 필요한 학습자</b><span class="mk-ref">진도가 낮거나 오래 접속하지 않은 학생을 먼저 보여 줘요.</span></div>')
        return frame(TH, sd('ov', True), ('HAI-Security', '교수(관리자) 화면'), main)
    I = 'media/walk/hai-security/'
    return [
        dict(title='학습자 대시보드에서 시작해요', text='오늘의 학습, 진행 중인 과제와 문제 풀이 현황을 대시보드에서 확인해요.', do='「오늘의 학습을 시작할 준비가 되었습니다」 알림을 눌러 학습을 시작해 보세요.', ui=dash(), img=I + '2.jpg'),
        dict(title='AI 튜터와 함께 공부해요', text='실습하다 막히면 AI 튜터에게 질문하며 스스로 답을 찾아가요.', do='AI 튜터에게 궁금한 것을 써서 보내 보세요. 비워 둔 채 보내면 예시 질문이 입력돼요.', ui=lab(), img=I + '3.jpg'),
        dict(title='실전형 CTF 문제를 풀어요', text='실제 공격 데이터를 분석해 위협 행위를 찾아내는 문제를 풀어요.', do='로그 목록에서 맨 위 기록을 눌러 자세히 살펴보세요.', ui=ctf('log'), img=I + '4.jpg'),
        dict(title='답을 제출하고 자동 채점을 받아요', text='찾아낸 답을 제출하면 자동 채점 시스템이 바로 결과를 알려 줘요.', do='정답 칸에 답을 쓰고 「제출」을 눌러 보세요.', ui=ctf('flag'), img=I + '4.jpg'),
        dict(title='교수님은 학습 현황을 관리해요', text='교수(관리자) 화면에서 문제와 시나리오를 관리하고 학생들의 학습 현황을 확인해요.', do='「상세 진도 보기」를 눌러 학생별 진도를 확인해 보세요.', ui=prof(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-PBL (소개자료 — 화면이 작게만 실려 있어 기능 소개에 맞춰 체험용으로 구성)
def _pbl():
    TH = '--mk:#0d9488;--mk-side:#134e4a'
    EGP = '<span class="mk-eg">체험용 예시 화면</span>'
    def sd(active):
        return side('HAI-PBL', '와우 아이디어스', [('', [('prj', 'doc', '프로젝트'), ('board', 'edit', '아이디어 보드'), ('dash', 'chart', '작업장 대시보드'), ('port', 'mark', '포트폴리오'), ('eval', 'check', '평가')])], active, user=('학생', '3모둠'), go={'prj': 1, 'board': 2, 'port': 3, 'eval': 4})
    def device():
        def box(k, w, t, hid): return f'<div class="mk-box" data-dv="{k}"{hid} style="width:{w};max-width:100%;margin:0 auto;border:3px solid #0f172a;border-radius:14px"><b>{t} 화면</b><div class="mk-pills"><span class="on">프로젝트</span><span>아이디어 보드</span><span>포트폴리오</span></div><span class="mk-ref">같은 주소로 접속해도 화면 크기에 맞게 배치가 바뀌어요.</span></div>'
        pick = ''.join(f'<button type="button" class="{"on" if k == 0 else ""}" data-on data-hide="[data-dv]" data-show="[data-dv={chr(39)}{k}{chr(39)}]"{" data-goal" if k == 2 else ""}>{t}</button>' for k, t in enumerate(['PC', '태블릿', '스마트폰']))
        return frame(TH, sd('prj'), ('HAI-PBL', '어디서나 접속'), '<div class="mk-row"><div class="mk-h"><h3>웹 기반 반응형 플랫폼</h3></div>' + EGP + '</div><div class="mk-tabs">' + pick + '</div>' + box(0, '100%', 'PC', '') + box(1, '70%', '태블릿', ' hidden') + box(2, '230px', '스마트폰', ' hidden'))
    def project():
        ST = ['문제 정의', '자료 조사', '아이디어 발상', '해결안 설계', '발표·성찰']
        fl = '<i>→</i>'.join(f'<button type="button" class="{"on" if k == 0 else ""}" data-on>{t}</button>' for k, t in enumerate(ST))
        main = ('<div class="mk-row"><div class="mk-h"><h3>프로젝트 구성</h3></div>' + EGP + '</div><p class="mk-ref">수업 설계를 프로젝트 단위로 재구성해요. 단계를 눌러 지금 진행 중인 단계를 바꿔 보세요.</p><div class="mk-flow">' + fl + '</div>'
                '<div class="mk-row"><b>작업장 대시보드</b><button type="button" class="mk-btn sm" data-show="[data-ds]" data-goal>학생 활동 통계 보기</button></div>'
                '<div class="mk-box" data-ds hidden><div class="mk-bars">' + ''.join(f'<div class="mk-bar2"><span>{l}</span><i style="--v:{v}%"></i><b>{v}%</b></div>' for l, v in [('1모둠', 80), ('2모둠', 65), ('3모둠', 90)]) + '</div><span class="mk-ref">모둠별 활동량을 보고 맞춤형 피드백을 줄 수 있어요.</span></div>')
        return frame(TH, sd('prj'), ('HAI-PBL', '프로젝트'), main)
    def board():
        main = ('<div class="mk-row"><div class="mk-h"><h3>IDEA BOARD</h3><span class="mk-st ing">실시간</span></div>' + EGP + '</div><div class="mk-box tint"><span class="mk-lbl">토의 주제</span><b>우리 학교 급식 잔반을 줄이려면?</b></div>'
                '<div class="mk-grid" id="mklog"><div class="mk-card" style="background:#fef9c3">먹을 만큼만 담는 자율 배식</div><div class="mk-card" style="background:#dcfce7">잔반 없는 날 스티커 모으기</div><div class="mk-card" style="background:#dbeafe" data-qa hidden><span data-q></span></div></div>'
                + inbar('메뉴를 미리 투표로 정하기', '아이디어를 적어 붙여 보세요…', True, show='[data-posted]', hide='[data-none]', more='아이디어를 더 붙였어요.') + toast('data-posted', '내 아이디어 카드가 보드에 붙었어요. 모둠 친구들이 실시간으로 볼 수 있어요.'))
        return frame(TH, sd('board'), ('HAI-PBL', '아이디어 보드'), main)
    def port():
        S = ['김하늘', '이도윤', '박서연']
        lst = ''.join(f'<button type="button" class="mk-rowbtn" data-on data-set="[data-pn]|{n}" data-show="[data-pf]"{" data-goal" if k == 0 else ""}><span><b>{n}</b><small>활동 기록 {12 - k * 3}건</small></span><span>›</span></button>' for k, n in enumerate(S))
        main = ('<div class="mk-row"><div class="mk-h"><h3>학생별 포트폴리오</h3></div>' + EGP + f'</div><div class="mk-two"><div class="mk-opts">{lst}</div><div class="mk-box" data-pf hidden><b><span data-pn>김하늘</span> 학생의 포트폴리오</b>'
                '<span>1주차　문제 정의 활동지 제출</span><span>2주차　자료 조사 발표</span><span>3주차　아이디어 보드 참여 8회</span><span class="mk-ref">활동 기록이 쌓여 성장 과정을 관찰할 수 있어요.</span></div></div>')
        return frame(TH, sd('port'), ('HAI-PBL', '포트폴리오'), main)
    def evalu():
        C = ['문제 해결에 기여했나요?', '모둠 활동에 협력했나요?', '자기 생각을 잘 표현했나요?']
        rows = ''.join(f'<div class="mk-box"><b>{c}</b><div class="mk-scale" data-sc>' + ''.join(f'<button type="button" data-on>{o}</button>' for o in ['노력 필요', '보통', '잘함', '매우 잘함']) + '</div></div>' for c in C)
        main = ('<div class="mk-row"><div class="mk-h"><h3>동료 평가 (루브릭 상호평가)</h3></div>' + EGP + '</div><p class="mk-ref">교사 평가(포트폴리오)와 동료 평가(루브릭 상호평가)로 과정중심 종합 평가를 해요. 모둠 친구 「이도윤」을 평가해 보세요.</p>' + rows
                + '<p class="mk-demo" data-need hidden>모든 항목을 평가해 주세요.</p><div class="mk-row end"><button type="button" class="mk-btn" data-allon="[data-sc]" data-show="[data-ev]" data-goal>평가 제출</button></div>' + toast('data-ev', '동료 평가를 제출했어요. 결과는 과정중심 종합 평가에 반영돼요.'))
        return frame(TH, sd('eval'), ('HAI-PBL', '평가'), main)
    I = 'media/walk/hai-pbl/'
    return [
        dict(title='어디서나 접속하는 웹 플랫폼', text='PC, 태블릿, 스마트폰 어디서나 웹으로 바로 접속하는 반응형 PBL 협업 플랫폼이에요.', do='화면 종류에서 「스마트폰」을 눌러 화면이 어떻게 바뀌는지 보세요.', ui=device(), img=I + '1.jpg'),
        dict(title='프로젝트를 체계적으로 구성해요', text='수업 설계를 프로젝트 단위로 재구성하고, 작업장 대시보드에서 학생 활동 통계와 맞춤형 피드백을 확인해요.', do='「학생 활동 통계 보기」를 눌러 작업장 대시보드를 확인해 보세요.', ui=project(), img=I + '2.jpg'),
        dict(title='실시간으로 아이디어를 모아요', text='아이디어 보드와 화상 연결로 실시간 토의·토론 수업을 해요.', do='아이디어를 적어 보드에 붙여 보세요. 비워 둔 채 보내면 예시가 입력돼요.', ui=board(), img=I + '3.jpg'),
        dict(title='학생별 포트폴리오가 쌓여요', text='활동 기록이 학생별 포트폴리오로 쌓여 성장 과정을 관찰할 수 있어요.', do='학생 목록에서 첫 번째 학생을 눌러 포트폴리오를 열어 보세요.', ui=port(), img=I + '4.jpg'),
        dict(title='과정중심으로 평가해요', text='교사 평가(포트폴리오)와 동료 평가(루브릭 상호평가)로 과정중심 종합 평가를 해요.', do='세 항목을 모두 평가한 뒤 「평가 제출」을 눌러 보세요.', ui=evalu(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-EpiLearn · HAI-MedLearnX (의과대학 코스웨어 매뉴얼 — 화면 구성이 같아 한 틀로 만든다)
def _studio(slug, brand, course, los, book, extras, pod, T):
    TH = '--mk:#4f46e5;--mk-side:#1e1b4b'
    TILES = [('edit', '수업 자료 생성', 'AI를 활용한 자동 콘텐츠 생성 및 편집'), ('doc', '수업 자료 편집', '기존 수업 자료 수정 및 관리'), ('user', '수업 진행', '실시간 수업 진행 및 학생 모니터링'), ('chart', '학습 분석', '학생 성과 분석 및 통계 확인')]
    BAR = lambda t: f'<div class="mk-topbar"><div class="mk-h"><h3>{t}</h3></div><span class="mk-chip">{course}</span></div>'
    def dash():
        tiles = ''.join(f'<button type="button" class="mk-tile" data-on data-show="[data-tl]"{" data-goal" if k == 0 else ""}>{ic(i, 22)}<b>{t}</b><small>{d}</small></button>' for k, (i, t, d) in enumerate(TILES))
        return frame(TH, '', (brand, '교수자 대시보드'), BAR('교수자 대시보드') + f'<p class="mk-center" style="margin:4px auto"><b>{course}</b><span class="mk-ref">원하는 기능을 선택해주세요</span></p><div class="mk-tiles">{tiles}</div>' + toast('data-tl', '기능 화면으로 이동해요. 상단 툴바의 수업 목록을 누르면 코스 목록으로 돌아가요.'))
    def make():
        lo = ''.join(f'<span>{k + 1}. {t}</span>' for k, t in enumerate(los))
        ex = ''.join(f'<button type="button" class="mk-rowbtn" data-tg><span>{t}</span><small>OFF</small></button>' for t in extras) or '<span class="mk-ref">자료가 없습니다</span>'
        main = (BAR('1단계 - 자료 선택') + f'<div class="mk-box"><div class="mk-row"><b>학습 목표</b><span class="mk-pills"><button type="button" data-tg>Bloom\'s Taxonomy <small>OFF</small></button></span></div>{lo}</div>'
                f'<div class="mk-two"><div class="mk-box" id="mkbk"><b>교재 목록</b><button type="button" class="mk-rowbtn" data-tg><span>{book}</span><small>OFF</small></button></div><div class="mk-box"><b>부가자료 목록</b>{ex}</div></div>'
                '<p class="mk-demo" data-need hidden>교재 목록에서 교재를 1개 이상 선택해 주세요.</p><button type="button" class="mk-btn wide" data-allon="#mkbk" data-wait="[data-mk]" data-show="[data-made]" data-goal>AI 콘텐츠 생성 시작</button>'
                '<p class="mk-note" data-mk hidden><span>AI가 팟캐스트, 강의노트, 퀴즈, 사례를 만들고 있어요…</span></p><div class="mk-box tint" data-made hidden><b>콘텐츠 생성이 끝났어요</b><span>2단계 「콘텐츠 확인」에서 탭별로 검토하고 고칠 수 있어요.</span><span class="mk-eg">체험용 예시 · 실제로는 몇 분 정도 걸려요</span></div>')
        return frame(TH, '', (brand, '수업 자료 생성'), main)
    def review():
        tabs = ''.join(f'<button type="button" class="{"on" if k == 0 else ""}" data-on data-hide="[data-rv]" data-show="[data-rv={chr(39)}{0 if k == 0 else (2 if "사전퀴즈" in t else 9)}{chr(39)}]"{" data-goal" if "사전퀴즈" in t else ""}>{t}</button>' for k, t in enumerate(T))
        main = (BAR('2단계 - 생성된 콘텐츠 확인') + f'<div class="mk-tabs">{tabs}</div><div class="mk-box" data-rv="0"><div class="mk-row"><b>팟캐스트 관리</b><span class="mk-eg">매뉴얼 화면을 옮긴 예시</span></div><b>{pod[0]}</b><span class="mk-ref">{pod[1]}</span>'
                f'<div class="mk-stats"><div class="mk-stat"><small>재생 시간</small><b>{pod[2]}</b></div><div class="mk-stat"><small>스크립트 길이</small><b>{pod[3]}</b></div></div><div class="mk-pills">' + ''.join(f'<span>{x}</span>' for x in pod[4]) + '</div></div>'
                f'<div class="mk-box" data-rv="2" hidden><b>사전퀴즈 검토</b><span>학습 목표에 맞춰 만든 사전퀴즈 문항이 목록으로 보여요.</span><span class="mk-ref">문항과 보기, 정답, 해설을 검토하고 고칠 수 있어요. (체험판에는 문항 내용이 들어 있지 않아요)</span></div>'
                '<p class="mk-demo" data-rv="9" hidden>체험판에는 팟캐스트와 사전퀴즈 탭만 들어 있어요.</p>')
        return frame(TH, '', (brand, '콘텐츠 확인'), main)
    return TH, BAR, dash, make, review

def _epilearn():
    los = ['역학의 개념을 설명할 수 있다.', '역학의 쓰임새를 열거할 수 있다.', '역학이 거둔 역사적 성과를 설명할 수 있다.']
    TH, BAR, dash, make, review = _studio('hai-epilearn', 'EpiLearn Studio', '1주차', los, 'Basic epidemiology_1주차', [], ('예방의학 핵심 정리 90초 세션', '예방 단계, 선별검사, 민감도와 특이도를 요약한 음성 콘텐츠', '02:00', '733자', ['1차예방', '선별검사', '2차예방', '민감도', '공중보건']), ['팟캐스트', '강의록', '사전퀴즈', '케이스', '사후퀴즈'])
    def ana():
        L = [('LO1', los[0], 74), ('LO2', los[1], 56), ('LO3', los[2], 64)]
        cards = ''.join(f'<button type="button" class="mk-card" data-on data-hide="[data-ld]" data-show="[data-ld={chr(39)}{k}{chr(39)}]"{" data-goal" if k == 0 else ""}><span class="mk-row"><span class="mk-chip">{c}</span><b style="color:var(--mk);font-size:17px">{v}%</b></span><strong>{t}</strong><span class="mk-bar2" style="grid-template-columns:1fr"><i style="--v:{v}%"></i></span></button>' for k, (c, t, v) in enumerate(L))
        det = ''.join(f'<p class="mk-note" data-ld="{k}" hidden><span><b>{c}</b> 달성률 {v}% · 이 목표와 연결된 문항의 정답·오답 분포를 보고 다음 수업에서 보완할 내용을 정해요.</span></p>' for k, (c, t, v) in enumerate(L))
        main = (BAR('학습성과') + '<p class="mk-ref">학습목표(LO) 달성 현황과 퀴즈 오답 분포를 확인합니다.</p><div class="mk-stats"><div class="mk-stat"><small>수강생</small><b>30명</b></div><div class="mk-stat"><small>문항 수</small><b>12개</b></div><div class="mk-stat"><small>전체 정답률</small><b>65%</b></div></div>'
                f'<b>학습목표(LO) 달성 현황</b><div class="mk-grid">{cards}</div>{det}')
        return frame(TH, '', ('EpiLearn Studio', '학습 분석'), main)
    I = 'media/walk/hai-epilearn/'
    return [
        dict(title='EPI-Learn Studio에 로그인해요', text='브라우저에서 EPI-Learn Studio에 접속해 로그인해요. 수업 전·중·후 전 과정을 한 곳에서 지원해요.', do='아이디와 비밀번호 칸을 확인하고 「로그인」을 눌러 보세요.', img=I + '1.jpg',
             ui=login(TH, ('COLLEGE OF MEDICINE', 'EpiLearn Studio', '사회의학 수업을 위한 AI 코스웨어'), ('EpiLearn', 'Studio'), [('아이디', '아이디를 입력하세요', 'text'), ('비밀번호', '비밀번호를 입력하세요', 'password')], [('로그인', True, True)], foot='교수자 또는 학생 계정으로 로그인하세요')),
        dict(title='교수자 대시보드에서 기능을 골라요', text='코스를 선택하면 수업 자료 생성, 수업 자료 편집, 수업 진행, 학습 분석 네 가지 기능 타일이 보여요.', do='네 가지 기능 가운데 「수업 자료 생성」을 눌러 보세요.', ui=dash(), img=I + '2.jpg'),
        dict(title='자료를 고르고 AI 생성을 시작해요', text='학습 목표와 교재를 고르면 AI가 팟캐스트, 강의노트, 퀴즈, 사례를 한 번에 만들어요.', do='교재를 눌러 고른 뒤 「AI 콘텐츠 생성 시작」을 눌러 보세요.', ui=make(), img=I + '3.jpg'),
        dict(title='생성된 콘텐츠를 검토해요', text='팟캐스트, 강의록, 사전퀴즈, 케이스, 사후퀴즈를 탭별로 검토하고 필요한 부분을 고쳐요.', do='「사전퀴즈」 탭을 눌러 생성된 퀴즈를 검토해 보세요.', ui=review(), img=I + '4.jpg'),
        dict(title='학습 성과를 분석해요', text='수업이 끝나면 학습목표(LO) 달성 현황과 퀴즈 오답 분포를 확인해 다음 수업 설계에 반영해요.', do='첫 번째 학습목표(LO1) 카드를 눌러 달성 현황을 살펴보세요.', ui=ana(), img=I + '5.jpg'),
    ]

def _medlearn():
    los = ['떨림 및 이상운동 증상을 보이는 환자에 대한 전반적인 진료 접근법을 이해한다.', '떨림이 있는 사람에게서 진단에 필요한 검사를 선택할 수 있다.', '병적 떨림이 있는 사람에게서 원인에 따른 치료 계획을 세울 수 있다.']
    TH, BAR, dash, make, review = _studio('hai-medlearn-x', 'MedLearn-X Studio', '떨림 운동이상(CP2)', los, '신경학(8) + Neurology', ['떨림 운동이상(CP2)', 'Consensus Statement on the Classification of Tremors', 'Systematic clinical approach for diagnosing upper…'],
                                          ('자율신경계와 연령·질환의 관계', '교감·부교감 균형을 다룬 음성 콘텐츠', '01:26', '702자', ['연령에 따른 교감 우세', '신경-내분비 상호작용', '파킨슨 감별']), ['팟캐스트 검토', '사전퀴즈 검토', '케이스 검토', '사후퀴즈 검토', '기타 데이터 선택'])
    def flow():
        F = [('콘텐츠 생성', '교수자가 학습 목표와 교재를 골라 AI로 수업 자료를 만들어요.'), ('검수', '만든 콘텐츠를 탭별로 검토하고 고쳐요.'), ('배포', '학생에게 팟캐스트와 사전퀴즈를 배포해요.'), ('학습', '수업 전 예습, 수업 중 임상 증례 기반 토론, 수업 후 사후퀴즈로 학습해요.'), ('분석', '사전·사후 평가 결과와 학습 데이터를 분석해요.'), ('재생성', '분석 결과를 반영해 다음 차시 자료를 다시 만들어요.')]
        fl = '<i>→</i>'.join(f'<button type="button" data-on data-hide="[data-fd]" data-show="[data-fd={chr(39)}{k}{chr(39)}]"{" data-goal" if k == 0 else ""}>{t}</button>' for k, (t, d) in enumerate(F))
        return frame(TH, '', ('MedLearn-X', '수업 흐름'), BAR('수업 흐름 개요') + '<p>MedLearn-X는 수업 전, 수업 중, 수업 후의 전 과정을 통합적으로 지원해요. 단계를 눌러 보세요.</p><div class="mk-flow">' + fl + '</div>' + ''.join(f'<div class="mk-box tint" data-fd="{k}" hidden><b>{k + 1}. {t}</b><span>{d}</span></div>' for k, (t, d) in enumerate(F)))
    def qr():
        main = (BAR('학생 접속') + '<div class="mk-two"><div class="mk-box" style="align-items:center;text-align:center"><b>수업 QR</b><div style="width:110px;height:110px;border-radius:8px;background:repeating-conic-gradient(#0f172a 0 25%,#fff 0 50%) 0 0/22px 22px"></div><span class="mk-ref">교수님이 화면에 띄운 QR을 스마트폰으로 스캔해요.</span></div>'
                '<div class="mk-box"><b>MedLearn-X Studio</b><label class="mk-f">아이디<input type="text" id="mkid" placeholder="아이디를 입력하세요" autocomplete="off" name="mk-qr-id" data-lpignore="true" data-1p-ignore readonly data-ro></label><p class="mk-demo" data-need hidden>아이디를 먼저 입력해 주세요.</p>'
                '<button type="button" class="mk-btn wide" data-req="#mkid" data-show="[data-in]" data-goal>로그인</button>' + toast('data-in', '수업에 접속했어요. 학생은 아이디만 입력하면 들어올 수 있어요.') + '</div></div>')
        return frame(TH, '', ('MedLearn-X', '학생 접속'), main)
    I = 'media/walk/hai-medlearn-x/'
    return [
        dict(title='수업 전·중·후를 하나로', text='콘텐츠 생성 → 검수 → 배포 → 학습 → 분석 → 재생성의 흐름으로 의학교육 수업 전 과정을 지원해요.', do='흐름의 첫 단계 「콘텐츠 생성」을 눌러 설명을 확인해 보세요.', ui=flow(), img=I + '1.jpg'),
        dict(title='학생은 QR로 바로 들어와요', text='교수님이 수업 QR을 띄우면 학생은 스마트폰으로 스캔해 아이디만 입력하고 접속해요.', do='아이디 칸에 아무 아이디나 쓰고 「로그인」을 눌러 보세요.', ui=qr(), img=I + '2.jpg'),
        dict(title='교수자 대시보드에서 시작해요', text='수업 자료 생성, 자료 편집, 수업 진행, 학습 분석 네 가지 기능을 타일로 골라요.', do='네 가지 기능 가운데 「수업 자료 생성」을 눌러 보세요.', ui=dash(), img=I + '3.jpg'),
        dict(title='AI로 수업 자료를 만들어요', text='학습 목표와 교재(PDF)를 고르면 AI가 팟캐스트, 강의노트, 퀴즈, 임상 증례를 자동으로 만들어요.', do='교재를 눌러 고른 뒤 「AI 콘텐츠 생성 시작」을 눌러 보세요.', ui=make(), img=I + '4.jpg'),
        dict(title='만든 콘텐츠를 확인해요', text='팟캐스트, 사전퀴즈, 케이스, 사후퀴즈를 탭별로 검토·수정하고 수업용 영상도 추가해요.', do='「사전퀴즈 검토」 탭을 눌러 생성된 퀴즈를 검토해 보세요.', ui=review(), img=I + '5.jpg'),
    ]

MOCKS = {'hai-docs': _docs(), 'hai-tutor': _tutor(), 'hai-mate': _mate(), 'hai-gpt': _gpt(), 'hai-mathtutor': _math(), 'lxp': _lxp(), 'hai-forum': _forum(), 'hai-fist': _fist(), 'hai-lens': _lens(), 'hai-way': _way(), 'hai-research': _research(),
         'hai-bdpi': _bdpi(), 'hai-check': _check(), 'hai-lrs': _lrs(), 'hai-sync': _sync(), 'hai-security': _security(), 'hai-pbl': _pbl(), 'hai-epilearn': _epilearn(), 'hai-medlearn-x': _medlearn()}

MK_CSS = r"""
/* 매뉴얼 기반 재구성용 보조 */
.mk-opt b { white-space: nowrap; }
.mk-tgl { display: inline-block; width: 30px; height: 17px; border-radius: 999px; background: #cbd5e1; position: relative; } .mk-tgl::after { content: ""; position: absolute; top: 2px; left: 2px; width: 13px; height: 13px; border-radius: 50%; background: #fff; } .mk-tgl.on { background: var(--mk); } .mk-tgl.on::after { left: 15px; }
.mk-cb { display: inline-block; width: 15px; height: 15px; border: 2px solid #cbd5e1; border-radius: 4px; vertical-align: -3px; background: #fff; } .mk-cb.on, .on > span > .mk-cb, .on > .mk-cb, tr.on .mk-cb { border-color: var(--mk); background: var(--mk) url("data:image/svg+xml,%3Csvg xmlns=%27http://www.w3.org/2000/svg%27 viewBox=%270 0 24 24%27 fill=%27none%27 stroke=%27white%27 stroke-width=%273.5%27%3E%3Cpath d=%27M5 12l5 5 9-10%27/%3E%3C/svg%3E") center/11px no-repeat; }
.mk-ox { display: inline-grid; grid-auto-flow: column; gap: 6px; padding: 4px 8px; border: 1px solid #e5e9f2; border-radius: 8px; font-weight: 700; } .mk-ox i { display: flex; flex-direction: column; align-items: center; font-style: normal; } .mk-ox small { font-size: 9px; color: #94a3b8; font-weight: 400; }
.mk-quad3 { display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.2fr) minmax(0, 1fr); gap: 10px; } @container (max-width: 760px) { .mk-quad3 { grid-template-columns: 1fr; } }
.mk-in { width: 100%; min-width: 0; height: 34px; padding: 0 10px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; } .mk select { height: 34px; padding: 0 8px; border: 1px solid #e2e8f0; border-radius: 8px; background: #fff; }
.mk-tbl tr[data-on] { cursor: pointer; } .mk-tbl tr[data-on]:hover td { background: #f8fafc; }
/* 체험용 화면(목업) 공통 */
.walk-ui { display: none; flex: 1; min-width: 0; container-type: inline-size; } .walk-shot.ui > img { display: none; } .walk-shot.ui .walk-ui { display: flex; } .walk-shot.ui { padding: 12px; }
.mk { --mk: #1d4ed8; --mk-side: #0b2a5b; flex: 1; min-width: 0; display: flex; align-items: stretch; min-height: min(600px, calc(100vh - 170px)); background: #f4f6fb; color: #1f2937; font-size: 13px; line-height: 1.5; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 18px rgba(0,0,0,.12); text-align: left; }
.mk [hidden] { display: none !important; } .mk button, .mk input, .mk select { font: inherit; color: inherit; } .mk button { cursor: pointer; } .mk p { margin: 0; } .mk-ic { flex: none; }
.mk-side { flex: none; width: 172px; display: flex; flex-direction: column; gap: 2px; padding: 16px 10px 12px; background: var(--mk-side); color: #c9d6ee; }
.mk-brand { padding: 0 8px 12px; color: #fff; } .mk-brand strong { display: block; font-size: 16px; } .mk-brand i { font-style: normal; font-size: 10px; padding: 1px 5px; border-radius: 5px; background: var(--mk); vertical-align: 2px; } .mk-brand small { font-size: 9px; letter-spacing: .08em; opacity: .7; }
.mk-grp { margin: 10px 8px 4px; font-size: 10px; letter-spacing: .06em; opacity: .6; } .mk-nav { display: flex; align-items: center; gap: 8px; padding: 7px 10px; border-radius: 8px; } .mk-nav.on { background: var(--mk); color: #fff; font-weight: 700; } button.mk-nav { border: 0; background: none; color: #fff; text-align: left; width: 100%; } button.mk-nav:hover { background: rgba(255,255,255,.12); } button.mk-nav.on:hover { background: var(--mk); } span.mk-nav { opacity: .55; } .mk-sp { flex: 1; min-height: 10px; }
.mk-user { display: flex; align-items: center; gap: 8px; margin-top: 8px; padding: 10px 8px 0; border-top: 1px solid rgba(255,255,255,.14); color: #fff; } .mk-user small { display: block; font-size: 10px; opacity: .7; } .mk-uav { display: inline-flex; width: 28px; height: 28px; align-items: center; justify-content: center; border-radius: 50%; background: rgba(255,255,255,.18); }
.mk-main { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 12px; padding: 16px 18px; overflow-y: auto; max-height: calc(100vh - 170px); } .mk-top { display: none; }
.mk-h { display: flex; align-items: center; gap: 10px; } .mk-h h3 { margin: 0; font-size: 18px; } .mk-badge { padding: 2px 9px; border-radius: 999px; background: #e3ecff; color: var(--mk); font-size: 11px; font-weight: 700; }
.mk-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; } .mk-row.end { justify-content: flex-end; } .mk-row small, .mk-h small { color: #6b7280; font-weight: 400; }
.mk-bar { display: flex; flex-wrap: wrap; gap: 10px; align-items: center; } .mk-tabs { display: flex; flex-wrap: wrap; gap: 2px; padding: 3px; border: 1px solid #e2e8f0; border-radius: 10px; background: #fff; } .mk-tabs button { padding: 5px 13px; border: 0; border-radius: 7px; background: none; color: #6b7280; } .mk-tabs button.on { background: #eef2f8; color: #111827; font-weight: 700; }
.mk-tabs.mk-pill { border: 0; background: none; padding: 0; gap: 6px; } .mk-tabs.mk-pill button { border: 1px solid #e2e8f0; border-radius: 999px; background: #fff; } .mk-tabs.mk-pill button.on { background: var(--mk); border-color: var(--mk); color: #fff; }
.mk-search { flex: 1; min-width: 150px; display: flex; align-items: center; gap: 8px; padding: 0 12px; height: 36px; border: 1px solid #e2e8f0; border-radius: 10px; background: #fff; color: #9ca3af; } .mk-search input { flex: 1; min-width: 0; border: 0; outline: 0; background: none; color: #111827; } .mk-search:focus-within { border-color: var(--mk); box-shadow: 0 0 0 3px rgba(29,78,216,.12); }
.mk-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; } .mk-grid.two { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.mk-card { display: flex; flex-direction: column; gap: 8px; padding: 14px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: left; } .mk-card strong { font-size: 13.5px; word-break: keep-all; } .mk-card.on { border-color: var(--mk); box-shadow: 0 0 0 2px rgba(29,78,216,.15); }
.mk-file { display: inline-flex; width: 34px; height: 34px; align-items: center; justify-content: center; border-radius: 9px; background: #e8f0ff; color: #2563eb; } .mk-file.pdf { background: #ffe9e9; color: #dc2626; } .mk-file.docx { background: #ece9ff; color: #4f46e5; }
.mk-st { padding: 1px 8px; border-radius: 999px; font-size: 11px; font-weight: 700; background: #e6f6ec; color: #15803d; } .mk-st.ing { background: #fff3e0; color: #d97706; }
.mk-chip { align-self: flex-start; padding: 1px 8px; border-radius: 6px; background: #eef2f8; color: #64748b; font-size: 11px; } .mk-meta { color: #94a3b8; font-size: 11.5px; } .mk-empty { padding: 26px 0; text-align: center; color: #6b7280; }
.mk-log { flex: 1; display: flex; flex-direction: column; gap: 12px; min-height: 120px; } .mk-hello { margin: auto; display: flex; flex-direction: column; align-items: center; gap: 8px; text-align: center; color: #6b7280; } .mk-hello b { font-size: 17px; color: #111827; }
.mk-msg { display: flex; gap: 8px; align-items: flex-start; } .mk-msg.me { justify-content: flex-end; } .mk-bub { max-width: 88%; padding: 10px 14px; border-radius: 12px; background: #fff; border: 1px solid #e5e9f2; display: flex; flex-direction: column; gap: 6px; } .mk-msg.me .mk-bub { background: #e3ecff; border-color: #d3e0ff; }
.mk-av { flex: none; display: inline-flex; width: 26px; height: 26px; align-items: center; justify-content: center; border-radius: 7px; background: var(--mk); color: #fff; font-size: 11px; font-weight: 800; }
.mk-ck { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 4px; } .mk-ck li { padding-left: 20px; position: relative; } .mk-ck li::before { content: '✓'; position: absolute; left: 0; top: 1px; width: 14px; height: 14px; border-radius: 50%; background: var(--mk); color: #fff; font-size: 9px; font-weight: 800; display: flex; align-items: center; justify-content: center; }
.mk-ref { color: #6b7280; font-size: 12px; } .mk-demo { padding: 6px 10px; border-radius: 8px; background: #fff7e6; color: #92400e; font-size: 12px; }
.mk-dots { flex-direction: row; gap: 4px; padding: 14px; } .mk-dots i { width: 6px; height: 6px; border-radius: 50%; background: #94a3b8; animation: mkDot 1s infinite; } .mk-dots i:nth-child(2) { animation-delay: .15s; } .mk-dots i:nth-child(3) { animation-delay: .3s; } @keyframes mkDot { 0%, 60%, 100% { opacity: .3; transform: none; } 30% { opacity: 1; transform: translateY(-3px); } }
.mk-block { display: flex; flex-direction: column; gap: 8px; margin-left: 34px; } .mk-link { color: var(--mk); font-size: 12px; } .mk-sub { color: #6b7280; font-size: 12px; margin-top: 2px; }
.mk-srcs { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; } .mk-src { display: flex; flex-direction: column; gap: 3px; padding: 10px; border: 1px solid #e5e9f2; border-radius: 10px; background: #fff; text-align: left; } .mk-src b { color: var(--mk); } .mk-src strong { font-size: 12.5px; word-break: keep-all; } .mk-src > span { color: #6b7280; font-size: 11.5px; } .mk-src.on { border-color: var(--mk); background: #f3f7ff; box-shadow: 0 0 0 2px rgba(29,78,216,.15); }
.mk-cite { display: flex; gap: 8px; align-items: flex-start; padding: 9px 12px; border-radius: 10px; background: #f3f7ff; border: 1px solid #d3e0ff; color: #1e3a8a; } .mk-note { display: flex; gap: 8px; align-items: flex-start; padding: 9px 12px; border-radius: 10px; background: #f1f5fb; color: #475569; font-size: 12px; }
.mk-chips { display: flex; flex-wrap: wrap; gap: 6px; } .mk-chips button { padding: 5px 11px; border: 1px solid #dbe3f0; border-radius: 999px; background: #fff; color: #1e3a8a; font-size: 12px; text-align: left; } .mk-chips button.on { background: #e3ecff; border-color: var(--mk); }
.mk-inbar { position: sticky; bottom: 0; display: flex; align-items: center; gap: 8px; padding: 6px 6px 6px 14px; border: 1px solid #dbe3f0; border-radius: 12px; background: #fff; box-shadow: 0 -6px 14px #f4f6fb; } .mk-inbar input { flex: 1; min-width: 0; height: 32px; border: 0; outline: 0; background: none; } .mk-inbar:focus-within { border-color: var(--mk); box-shadow: 0 0 0 3px rgba(29,78,216,.12); }
.mk-ghost { color: #94a3b8; display: inline-flex; } .mk-send { display: inline-flex; width: 34px; height: 34px; align-items: center; justify-content: center; border: 0; border-radius: 9px; background: var(--mk); color: #fff !important; }
.mk-aside { flex: none; width: 190px; display: flex; flex-direction: column; gap: 8px; padding: 16px 12px; border-left: 1px solid #e5e9f2; background: #fff; } .mk-res { display: flex; gap: 8px; align-items: flex-start; padding: 6px 0; border-bottom: 1px solid #f1f4f9; } .mk-res strong { display: block; font-size: 12px; word-break: keep-all; } .mk-res small { color: #94a3b8; font-size: 11px; } .mk-res .mk-file { width: 28px; height: 28px; border-radius: 7px; }
.mk-stepper { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; } .mk-stepper span { display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 8px 4px; border-top: 3px solid #dbe3f0; color: #94a3b8; text-align: center; } .mk-stepper i { font-style: normal; display: inline-flex; width: 24px; height: 24px; align-items: center; justify-content: center; border-radius: 50%; border: 1px solid #cbd5e1; font-weight: 700; background: #fff; } .mk-stepper small { font-size: 11px; }
.mk-stepper span.on { border-color: var(--mk); color: #111827; } .mk-stepper span.on i { background: var(--mk); border-color: var(--mk); color: #fff; }
.mk-fields { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; } .mk-fields label, .mk-fields > div { display: flex; flex-direction: column; gap: 5px; font-weight: 700; } .mk-fields select { height: 36px; padding: 0 10px; border: 1px solid #dbe3f0; border-radius: 9px; background: #fff; font-weight: 400; }
.mk-seg { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; } .mk-seg button { height: 36px; border: 1px solid #dbe3f0; border-radius: 9px; background: #fff; font-weight: 400; color: #64748b; } .mk-seg button.on { border-color: var(--mk); color: var(--mk); font-weight: 700; box-shadow: 0 0 0 1px var(--mk) inset; }
.mk-guide { display: flex; flex-direction: column; gap: 6px; padding: 12px 14px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; } .mk-guide b { color: var(--mk); } .mk-guide > span { color: #475569; }
.mk-tpl > span:last-child { color: #6b7280; font-size: 12px; } .mk-tpl .mk-ic { color: #94a3b8; }
.mk-paper { display: flex; flex-direction: column; gap: 10px; padding: 14px; border: 2px solid var(--mk); border-radius: 12px; background: #fff; } .mk-sheet { padding: 16px 18px; border: 1px solid #e5e9f2; border-radius: 6px; background: #fff; display: flex; flex-direction: column; gap: 6px; box-shadow: 0 2px 8px rgba(0,0,0,.06); } .mk-sheet .c { text-align: center; font-weight: 800; font-size: 16px; letter-spacing: .2em; } .mk-sheet .in { padding-left: 18px; } .mk-sheet hr { width: 100%; border: 0; border-top: 2px solid #111827; margin: 2px 0; }
.mk-btn { display: inline-flex; align-items: center; gap: 6px; height: 36px; padding: 0 14px; border: 0; border-radius: 9px; background: var(--mk); color: #fff !important; font-weight: 700; } .mk-ok { display: flex; align-items: center; gap: 6px; color: #15803d; font-weight: 700; }
.mk .mk-hint { outline: 3px solid var(--accent, #0b5cff); outline-offset: 3px; border-radius: 10px; animation: mkHint 1.1s ease-in-out infinite; } @keyframes mkHint { 0%, 100% { box-shadow: 0 0 0 4px rgba(11,92,255,.35); } 50% { box-shadow: 0 0 0 14px rgba(11,92,255,0); } }
.mk-side.light { background: #fff; color: #334155; border-right: 1px solid #e5e9f2; } .mk-side.light .mk-brand { color: #0f172a; } .mk-side.light button.mk-nav { color: #0f172a; } .mk-side.light button.mk-nav:hover { background: #eef2f8; } .mk-side.light .mk-nav.on, .mk-side.light button.mk-nav.on:hover { background: #e3ecff; color: var(--mk); } .mk-side.light .mk-user { color: #0f172a; border-color: #e5e9f2; } .mk-side.light .mk-uav { background: #eef2f8; }
.mk-hist { padding: 5px 10px; font-size: 12px; color: #475569; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; } .mk-course { margin: 0 4px 8px; padding: 8px 10px; border: 1px solid #e5e9f2; border-radius: 9px; font-size: 12px; } .mk-course b { display: block; }
.mk-login { align-items: stretch; background: #fff; } .mk-hero { flex: 1.2; min-width: 0; display: flex; flex-direction: column; justify-content: center; gap: 8px; padding: 28px; background: linear-gradient(135deg, var(--mk-side), var(--mk)); color: #fff; } .mk-hero small { font-size: 10px; letter-spacing: .1em; opacity: .8; } .mk-hero b { font-size: 24px; line-height: 1.3; } .mk-hero span { opacity: .9; } .mk-hchips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; } .mk-hchips i { font-style: normal; padding: 3px 10px; border-radius: 999px; background: rgba(255,255,255,.18); font-size: 11px; }
.mk-lg { flex: 1; min-width: 0; align-self: center; display: flex; flex-direction: column; gap: 10px; padding: 24px 28px; } .mk-lg small { color: var(--mk); font-size: 10px; font-weight: 700; letter-spacing: .1em; } .mk-lg h3 { margin: 0 0 4px; font-size: 20px; } .mk-lg label, .mk-f { display: flex; flex-direction: column; gap: 4px; font-size: 12px; font-weight: 700; color: #475569; }
.mk input[type=text], .mk input[type=password], .mk textarea, .mk-f select { height: 38px; padding: 0 12px; border: 1px solid #dbe3f0; border-radius: 9px; background: #fff; font-weight: 400; color: #111827; outline: 0; } .mk textarea, .mk input, .mk select { font-weight: 400; } .mk textarea { height: auto; min-height: 64px; padding: 9px 12px; resize: vertical; font: inherit; } .mk input:focus, .mk textarea:focus { border-color: var(--mk); box-shadow: 0 0 0 3px rgba(29,78,216,.12); } .mk-inbar input[type=text], .mk-search input { height: 32px; padding: 0; border: 0; box-shadow: none !important; }
.mk-btn.wide { justify-content: center; width: 100%; height: 40px; } .mk-btn.soft { background: #e3ecff; color: var(--mk) !important; } .mk-btn.line { background: #fff; border: 1px solid #dbe3f0; color: #334155 !important; } .mk-btn.sm { height: 30px; padding: 0 11px; font-size: 12px; } .mk-btn.dark { background: #0f172a; }
.mk-modal { display: flex; flex-direction: column; gap: 12px; padding: 16px 18px; border-radius: 14px; background: #fff; border: 1px solid #e5e9f2; box-shadow: 0 10px 30px rgba(15,23,42,.12); } .mk-dim { background: #e9edf5; }
.mk-box { display: flex; flex-direction: column; gap: 8px; padding: 12px 14px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; } .mk-box.tint { background: #f3f7ff; border-color: #d3e0ff; } .mk-lbl { font-size: 12px; font-weight: 700; color: #64748b; }
.mk-pills { display: flex; flex-wrap: wrap; gap: 6px; } .mk .mk-pills > * { padding: 3px 10px; border: 1px solid #dbe3f0; border-radius: 999px; background: #fff; font-size: 12px; color: #475569; } .mk .mk-pills > .on { background: var(--mk); border-color: var(--mk); color: #fff; font-weight: 700; }
.mk-opts { display: flex; flex-direction: column; gap: 6px; } .mk-opt { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border: 1px solid #e5e9f2; border-radius: 10px; background: #fff; text-align: left; } .mk-opt::before { content: ''; flex: none; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #cbd5e1; } .mk-opt.on { border-color: var(--mk); background: #f3f7ff; } .mk-opt.on::before { border-color: var(--mk); background: radial-gradient(var(--mk) 45%, #fff 50%); }
.mk-tbl { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e5e9f2; border-radius: 10px; overflow: hidden; font-size: 12.5px; } .mk-tbl th { padding: 8px 10px; background: #f1f5fb; color: #64748b; font-weight: 700; text-align: left; white-space: nowrap; } .mk-tbl td { padding: 9px 10px; border-top: 1px solid #f1f4f9; } .mk-tbl tr.on td { background: #f3f7ff; } .mk-tbl button { border: 0; background: none; padding: 0; color: inherit; text-align: left; font-weight: 700; }
.mk-rowbtn { display: flex; align-items: center; justify-content: space-between; gap: 10px; width: 100%; padding: 12px 14px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: left; } .mk-rowbtn:hover, .mk-card[type=button]:hover, .mk-opt:hover { border-color: var(--mk); } .mk-rowbtn small { display: block; color: #6b7280; font-weight: 400; }
.mk-bars { display: flex; flex-direction: column; gap: 8px; } .mk-bar2 { display: grid; grid-template-columns: 96px 1fr 44px; align-items: center; gap: 8px; width: 100%; padding: 4px 6px; border: 0; border-radius: 8px; background: none; text-align: right; font-size: 12.5px; } .mk-bar2 i { display: block; height: 16px; border-radius: 5px; background: #e8edf5; overflow: hidden; } .mk-bar2 i::after { content: ''; display: block; height: 100%; width: var(--v); background: var(--mk); border-radius: 5px; } .mk-bar2 b { text-align: left; } .mk-bar2.on, button.mk-bar2:hover { background: #eef4ff; }
.mk-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; } .mk-stat { display: flex; flex-direction: column; gap: 2px; padding: 12px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: left; } .mk-stat small { color: #6b7280; } .mk-stat b { font-size: 20px; }
.mk-tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; } .mk-tile { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 16px 8px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: center; } .mk-tile small { color: #6b7280; font-size: 11px; } .mk-tile .mk-ic { color: var(--mk); } .mk-tile.on { border-color: var(--mk); background: #f3f7ff; }
.mk textarea.mk-code { background: #0b1020; color: #d6e2ff; border: 0; }
.mk-code { padding: 12px 14px; border-radius: 10px; background: #0b1020; color: #d6e2ff; font: 12.5px/1.6 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre-wrap; min-height: 90px; } textarea.mk-code { width: 100%; border: 0; }
.mk-center { margin: auto; display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center; } .mk-up { display: flex; flex-direction: column; align-items: center; gap: 6px; width: 100%; padding: 22px 12px; border: 2px dashed #cbd5e1; border-radius: 12px; background: #fff; color: #64748b; } .mk-up:hover { border-color: var(--mk); color: var(--mk); }
.mk canvas[data-draw] { display: block; width: 100%; height: 150px; border: 1px dashed #b8c4d9; border-radius: 10px; background: #fff; touch-action: none; cursor: crosshair; } .mk-drawwrap { position: relative; } .mk-drawwrap > span { position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%); text-align: center; color: #94a3b8; pointer-events: none; }
.mk-scale { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; } .mk-scale button { padding: 7px 4px; border: 1px solid #dbe3f0; border-radius: 9px; background: #fff; font-size: 11.5px; color: #475569; } .mk-scale button.on { background: var(--mk); border-color: var(--mk); color: #fff; font-weight: 700; }
.mk-flow { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; } .mk-flow button { padding: 8px 12px; border: 1px solid #dbe3f0; border-radius: 10px; background: #fff; font-weight: 700; } .mk-flow button.on { background: var(--mk); border-color: var(--mk); color: #fff; } .mk-flow i { font-style: normal; color: #94a3b8; }
.mk-quad { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; } .mk-quad button { display: flex; flex-direction: column; gap: 6px; padding: 14px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: left; } .mk-quad button b { font-size: 20px; } .mk-quad button.on { background: var(--mk); border-color: var(--mk); color: #fff; }
.mk-eg { align-self: flex-start; padding: 1px 8px; border-radius: 6px; background: #fff7e6; color: #92400e; font-size: 11px; } .mk-topbar { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.mk-filechip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border-radius: 8px; background: #eef2f8; font-size: 12px; } .mk-two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; } .mk-grow { flex: 1; }
@container (max-width: 700px) { .mk-aside { display: none; } .mk { flex-wrap: wrap; } .mk-aside.mk-keep { display: flex; width: 100% !important; border-left: 0; border-top: 1px solid #e5e9f2; } }
@container (max-width: 560px) { .mk-hero { display: none; } .mk-tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } .mk-two { grid-template-columns: 1fr; } .mk-bar2 { grid-template-columns: 72px 1fr 40px; } .mk-side { display: none; } .mk-top { display: flex; align-items: center; gap: 8px; margin: -16px -14px 0; padding: 9px 14px; background: var(--mk-side); color: #fff; } .mk-top span { opacity: .8; font-size: 12px; } .mk-main { padding: 16px 14px; } .mk-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .mk-grid.two, .mk-srcs, .mk-fields { grid-template-columns: 1fr; } .mk-block { margin-left: 0; } }
@media (max-width: 860px) { .walk-main.uimode { grid-template-rows: minmax(0, 56%) minmax(0, 1fr); } .walk-shot.ui { padding: 0; } .mk { min-height: 100%; border-radius: 0; } .mk-main { max-height: none; } }
"""
