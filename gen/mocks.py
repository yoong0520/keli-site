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
    f = ''.join(f'<label>{n}<input type="{t}" placeholder="{ph}" autocomplete="off"></label>' for n, ph, t in fields)
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
        return side('HAI-Docs <i>AI</i>', 'HALLYM UNIVERSITY', [
            ('WORKSPACE', [('home', 'home', '홈'), ('chat', 'chat', 'AI 대화'), ('lib', 'doc', '문서 라이브러리'), ('gen', 'edit', '문서 생성'), ('mark', 'mark', '북마크'), ('rem', 'bell', '리마인드')]),
            ('ADMIN', [('dash', 'chart', '대시보드'), ('sys', 'gear', '시스템 관리')])], active, user=('박직원', '교무팀 · 직원'), foot=[('gear', '설정'), ('help', '도움말')], go={'lib': 0, 'chat': 2, 'gen': 4})
    DOCS = [('한림대학교_학사운영규정', 'PDF', '2.4 MB', '2026.03.15', '완료', '규정'), ('교원인사규정', 'HWP', '1.8 MB', '2026.03.12', '진행중', '규정'), ('자체평가계획서', 'PDF', '3.1 MB', '2026.03.10', '완료', '보고서'),
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
               f'<p>한림대학교 교원 연구년 제도는 다음과 같이 운영됩니다.</p><ul class="mk-ck"><li><b>대상:</b> 전임교원(조교수 이상)으로 재직기간 3년 이상인 자</li><li><b>기간:</b> 1년 또는 2년(단, 연속 2회 초과 불가)</li></ul>'
               f'<p class="mk-ref">(근거: 한림대학교 교원인사규정 제27조(연구년))</p></div></div>'
               f'<div class="mk-block" data-a{hid}><div class="mk-row"><b>참고 문서 <small>(원문 근거)</small></b><span class="mk-link">모두 보기</span></div><div class="mk-srcs">{src}</div>{cites}'
               f'<p class="mk-note">{ic("shield", 15)}<span>AI 응답은 등록된 한림대학교 공식 문서를 기반으로 생성되었습니다. 부정확한 정보 발견 시 피드백을 통해 개선에 참여해주세요.</span></p>'
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
    TPL = [('공문서 기본 템플릿', '제목과 주요 내용을 바탕으로 한림대학교 행정 공문서 초안을 생성합니다.'), ('공지사항 기본 템플릿', '공지 대상, 기간, 안내사항을 중심으로 게시용 공지 초안을 생성합니다.'), ('회의록 기본 템플릿', '회의명, 참석자, 안건, 결정사항을 중심으로 회의록 초안을 생성합니다.'),
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
    TH = '--mk:#2f6fed;--mk-side:#0b2a66'
    HIST = ['이번 학기 수업계획서를 생성해 주세요.', '창의적인 프론트엔드 기술에 대해 쉬운…', '메모리 관리에 관해 쉬운 단답식 1문제…', '메모리 관리에 관해 어려운 객관식 3문…']
    def sd(active):
        return side('AI 조교 <i>v1.1.4</i>', '', [('', [('new', 'chat', '새로운 대화'), ('src', 'doc', '소스 문서 관리'), ('con', 'edit', '콘텐츠 관리'), ('stu', 'user', '수강생 관리'), ('bank', 'chart', '문제출제 및 시험관리')])], active,
                    user=('Test003 교수님', '교수'), go={'new': 1, 'bank': 3}, light=True, top='<div class="mk-course"><small>2025학년도 2학기</small><b>창의코딩-모두의웹</b></div>',
                    mid='<span class="mk-grp">대화내역</span>' + ''.join(f'<span class="mk-hist">{h}</span>' for h in HIST))
    Q = '올린 자료로 쉬운 단답식 3개와 어려운 객관식 2개를 만들어 줘'
    def chat(answered, goal):
        hid = '' if answered else ' hidden'
        hello = '' if answered else ('<div class="mk-hello" data-hello><b>강의 준비에 필요한 <span style="color:var(--mk)">자료를 생성해 보세요</span></b><span>업로드한 강의 자료를 바탕으로 AI가 시험 문제, 수업 자료 등을 만들어 드립니다.</span>'
                                    '<div class="mk-chips"><button type="button" data-show="[data-guide]">' + ic('help', 14) + ' 더 똑똑한 문제 생성 가이드</button><button type="button" data-fill="' + Q + '">예시 요청 넣기</button></div>'
                                    '<p class="mk-note" data-guide hidden><span>문제의 난이도, 개수, 유형을 함께 알려 주면 더 좋은 문항을 만들 수 있어요. 강의 자료를 먼저 올리면 그 자료를 근거로 만들어요.</span></p></div>')
        body = (demo(Q) + '<p><b>[객관식 · 어려움]</b> 다음 설명 중 \'과제별 특성 반영\' 기준에 해당하는 것을 고르세요.</p><p>A. 반복 없이 다양한 표현을 사용했다.<br>B. 서론-본론-결론이 명확하고 연결이 자연스럽다.<br>C. 문법적 오류가 적고 문장이 명확하다.<br>D. 논설문은 설득력, 설명문은 정보의 정확성과 다양성을 평가한다.</p><p><b>정답: D</b></p>'
                '<p class="mk-ref">안내(요청 사항 확인) 위에 정리해 드린 문항들은 요청하신 쉬운 단답형 3개 + 어려운 객관식 2개 조건을 충족합니다. 원하시면 같은 기준으로 추가 문제도 더 만들어 드리겠습니다.</p>')
        src = (f'<div class="mk-block" data-a{hid}><div class="mk-row"><span class="mk-lbl">원본 출처</span><span class="mk-pills"><button type="button" data-show="[data-saved]">파일로 저장</button></span></div>'
               f'<div class="mk-rowbtn" style="cursor:default"><span><span class="mk-filechip">{ic("doc", 14)}pro16_영작 평가 기준 안내.pdf</span></span><button type="button" class="mk-btn sm line" data-show="[data-open]"{" data-goal" if goal == "src" else ""}>열기</button></div>'
               + toast('data-open', '출처 문서가 열렸어요. 답변의 근거가 된 원본 자료를 확인할 수 있어요. (체험판에서는 문서 창이 뜨지 않아요)') + toast('data-saved', '답변을 파일로 저장했어요. (체험판에서는 파일이 만들어지지 않아요)') + '</div>')
        main = (f'<div class="mk-log" id="mklog">{hello}{me(Q if answered else "", "data-qa" + hid)}{dots()}{ai(body, "data-a" + hid)}{src}</div>'
                + inbar(Q, '메시지를 입력하세요…', goal == 'ask', pre=f'<span class="mk-ghost" title="강의 자료 올리기">{ic("clip", 16)}</span>', post='<span class="mk-chip" style="align-self:center">MODEL GPT 5.2</span>'))
        return frame(TH, sd('new'), ('AI 조교', '새로운 대화'), main)
    QS = [('단답형', '보통', '웹페이지 개발 시 불필요한 리소스가 과도하게 로드되어 메모리가 낭비되는 상황을 줄이기 위해 꼭 수행해야 할 작업 한 가지를 간단히 쓰시오.', '불필요한 리소스 제거',
           '웹페이지에는 실제로 사용되지 않는 스크립트나 이미지 파일이 포함될 수 있는데, 이를 그대로 두면 메모리가 불필요하게 점유되고 로드 속도가 저하됩니다. 따라서 필요하지 않은 리소스를 적극적으로 제거하거나 최적화하여 메모리 사용을 효율화해야 합니다.'),
          ('객관식', '보통', '다음 중 창의적인 프론트엔드 디자인에서 색상, 글꼴, 배치를 담당하는 기술은 무엇입니까?', '② CSS', 'CSS는 웹페이지의 시각적 요소를 꾸미고 배치하는 데 사용됩니다. HTML은 구조, JavaScript는 동적 기능, 데이터베이스는 백엔드와 관련됩니다.')]
    def qcard(k, t, lv, q, a, ex):
        return (f'<div class="mk-box" data-qc="{k}"{"" if k == 0 else " hidden"}><div class="mk-row"><span class="mk-pills"><span class="on">{t}</span><span>난이도 {lv}</span></span>'
                f'<span class="mk-row"><button type="button" class="mk-btn sm" data-show="[data-add{k}]"{" data-goal" if k == 0 else ""}>이 문항만 추가</button><button type="button" class="mk-btn sm line" data-go="4">수정</button></span></div>'
                f'<span class="mk-lbl">질문</span><p>{q}</p><span class="mk-lbl">정답</span><p><b>{a}</b></p><span class="mk-lbl">해설</span><p>{ex}</p>' + toast(f'data-add{k}', '문제은행에 추가했어요.') + '</div>')
    def bank():
        pager = ('<div class="mk-row"><span class="mk-pills"><button type="button" class="on" data-on data-hide="[data-qc]" data-show="[data-qc=\'0\']">1</button><button type="button" data-on data-hide="[data-qc]" data-show="[data-qc=\'1\']">2</button></span>'
                 '<button type="button" class="mk-btn sm dark" data-show="[data-all]">미등록 2건 일괄 등록</button></div>')
        main = ('<div class="mk-modal"><div class="mk-h"><h3>생성 문제</h3><span class="mk-badge">2건</span></div><p class="mk-ref">생성된 문제를 확인 및 수정하고 바로 문제은행에 추가할 수 있습니다.</p>' + pager
                + ''.join(qcard(k, *x) for k, x in enumerate(QS)) + toast('data-all', '남은 문항을 모두 문제은행에 등록했어요.') + '</div>')
        return frame(TH, sd('bank'), ('AI 조교', '생성 문제'), main)
    def edit():
        opts = ''.join(f'<button type="button" class="mk-opt{" on" if k == 1 else ""}" data-on>{k + 1}　{t}</button>' for k, t in enumerate(['HTML', 'CSS', 'JavaScript', '데이터베이스']))
        main = ('<div class="mk-modal"><div class="mk-row"><div class="mk-h"><h3>생성 문제</h3><span class="mk-badge">문항 편집</span></div><span class="mk-row"><button type="button" class="mk-btn sm line">원래대로</button><button type="button" class="mk-btn sm dark" data-show="[data-saved]" data-goal>저장</button></span></div>'
                '<div class="mk-two"><div class="mk-f">문제 유형<div class="mk-pills"><button type="button" class="on" data-on>객관식</button><button type="button" data-on>단답형</button><button type="button" data-on>빈칸 채우기</button><button type="button" data-on>서술형</button></div></div>'
                '<label class="mk-f">난이도<select><option>쉬움</option><option selected>보통</option><option>어려움</option></select></label></div>'
                '<label class="mk-f">질문<textarea>다음 중 창의적인 프론트엔드 디자인에서 색상, 글꼴, 배치를 담당하는 기술은 무엇입니까?</textarea></label>'
                f'<div class="mk-f">선택지 (정답을 눌러 고르세요)<div class="mk-opts">{opts}</div></div>'
                '<label class="mk-f">해설<textarea>CSS는 웹페이지의 시각적 요소를 꾸미고 배치하는 데 사용됩니다. HTML은 구조, JavaScript는 동적 기능, 데이터베이스는 백엔드와 관련됩니다.</textarea></label>'
                + toast('data-saved', '수정한 내용을 저장했어요. 해설은 나중에 AI가 시험지를 채점할 때 쓰여요.') + '</div>')
        return frame(TH, sd('bank'), ('AI 조교', '문항 편집'), main)
    I = 'media/walk/hai-tutor/'
    return [
        dict(title='사번으로 로그인해요', text='별도 회원가입 없이 한림대학교 사번 ID와 비밀번호로 로그인해요. 아이디 저장 기능도 있어요.', do='「한림대 통합 로그인」 단추를 눌러 로그인해 보세요.', img=I + '1.jpg',
             ui=login(TH, ('HALLYM UNIVERSITY AI TEACHING ASSISTANT', '교수 활동 지원 시스템', '검색부터 자료 생성까지 모두 가능한 AI 조교와의 대화를 시작해 보세요.', ['AI Chat', 'Lecture Prep', 'Smart Assist']),
                      ('SECURE ACCESS', 'Sign in'), [('아이디', '아이디', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', False, False), ('한림대 통합 로그인', True, True)])),
        dict(title='강의 자료를 올리고 대화를 시작해요', text='입력창 왼쪽 클립 단추로 강의 자료를 올리면, 그 자료를 근거로 더 믿을 수 있는 답을 만들어 줘요. 「더 똑똑한 문제 생성 가이드」로 요청 요령도 볼 수 있어요.',
             do='입력창에 요청을 쓰고 보내 보세요. 비워 둔 채 보내면 예시 요청이 입력돼요.', ui=chat(False, 'ask'), img=I + '2.jpg'),
        dict(title='답변의 출처를 확인해요', text='답변 아래에 근거가 된 원본 자료가 표시돼요. 「열기」를 누르면 출처 문서를 바로 열어 볼 수 있고, 답변은 복사하거나 파일로 저장할 수 있어요.',
             do='답변 아래 원본 출처의 「열기」를 눌러 보세요.', ui=chat(True, 'src'), img=I + '3.jpg'),
        dict(title='시험 문항을 만들어요', text='대화로 문제 생성을 요청하면 문항이 만들어져요. 문항을 넘겨 보며 검토하고, 마음에 드는 문항을 문제은행에 추가해요.',
             do='첫 번째 문항에서 「이 문항만 추가」를 눌러 문제은행에 담아 보세요.', ui=bank(), img=I + '4.jpg'),
        dict(title='문항을 다듬고 저장해요', text='난이도·정답·보기·해설을 직접 고칠 수 있어요. 해설은 나중에 AI가 시험지를 채점할 때 쓰이니 꼼꼼히 확인하고 저장해요.',
             do='내용을 고쳐 본 뒤 「저장」을 눌러 보세요.', ui=edit(), img=I + '5.jpg'),
    ]

# ------------------------------------------------------------------ HAI-Mate (학생용 매뉴얼)
def _mate():
    TH = '--mk:#1e4fd8;--mk-side:#0b2a66'
    def sd(active, entered=True):
        return side('HAI-Mate', '', [('', [('chat', 'chat', '챗봇 튜터'), ('mat', 'doc', '학습 자료'), ('pre', 'edit', '예복습 문제'), ('quiz', 'check', '퀴즈')])], active, user=('학생', 'AIED 학생'), light=True,
                    go=({'chat': 1, 'pre': 2} if entered else {}), top='<div class="mk-course"><small>2026학년도 2학기</small><b>' + ('창의코딩파이썬-1' if entered else '강좌를 선택해주세요') + '</b></div>')
    def home():
        main = ('<div class="mk-h"><h3>나의 강좌</h3></div><div class="mk-box"><div class="mk-row"><span><span class="mk-lbl">강좌 조회</span><br><b>2026학년도 2학기</b></span>'
                '<span class="mk-row"><label class="mk-f">년도<select><option>2026</option><option>2025</option></select></label><label class="mk-f">학기<select><option>2</option><option>1</option></select></label></span></div></div>'
                '<button type="button" class="mk-rowbtn" data-on data-show="[data-in]" data-goal><span><b>창의코딩파이썬-1</b> <small style="display:inline">AIED 2수 1</small></span><span>›</span></button>'
                + toast('data-in', '강좌에 들어왔어요. 챗봇 튜터, 학습 자료, 예복습 문제, 퀴즈 메뉴가 열려요.'))
        return frame(TH, sd('', False), ('HAI-Mate', '나의 강좌'), main)
    Q = '파이썬에서 주석은 어떻게 작성해?'
    def chat():
        hello = '<div class="mk-hello" data-hello><b>무엇을 도와드릴까요?</b><span>창의코딩파이썬-1에 대해 궁금한 것을 튜터에게 자유롭게 물어보세요!</span><div class="mk-chips"><button type="button" data-fill="' + Q + '">예시 질문: ' + Q + '</button></div></div>'
        body = (demo(Q) + '<p>파이썬에서 주석은 <b># 문자 뒤에</b> 작성해요.</p><p>주석은 주로 소스 코드를 읽는 사람을 위해 남기는 설명이에요. 코드가 무엇을 하는지보다 <b>왜 그렇게 작성했는지</b>를 적어 두면 좋아요.</p>'
                f'<p class="mk-ref">참고 자료 <span class="mk-filechip">{ic("doc", 13)}byte_of_python_5장.pdf · p.1</span></p>')
        aside = ('<aside class="mk-aside"><button type="button" class="mk-btn sm soft wide" data-go="1">새로운 대화 시작하기 +</button><b>전체 대화</b><small style="color:#94a3b8">오늘</small><span class="mk-hist">파이썬에서 주석은 어떻게 작성해?</span><small style="color:#94a3b8">지난 30일</small><span class="mk-hist">학습 자료 목록 요청</span></aside>')
        main = '<div class="mk-h"><h3>챗봇 튜터</h3></div><div class="mk-log" id="mklog">' + hello + me('', 'data-qa hidden') + dots('튜터') + ai(body, 'data-a hidden', '튜터') + '</div>' + inbar(Q, '창의코딩파이썬-1에 대해 궁금한 것을 튜터에게 자유롭게 물어보세요!', True)
        return frame(TH, sd('chat'), ('HAI-Mate', '챗봇 튜터'), main, aside)
    def plist():
        main = ('<div class="mk-h"><h3>문제 풀기</h3></div><table class="mk-tbl"><tr><th>번호</th><th>퀴즈명</th><th>시작 일시</th><th>종료 일시</th><th>상태</th><th>응시</th></tr>'
                '<tr><td>1</td><td><button type="button" data-show="[data-open]" data-goal>11주차 예습</button></td><td>2026-09-02 10:23</td><td>-</td><td><span class="mk-st ok">응시 가능</span></td><td>›</td></tr></table>'
                + toast('data-open', '11주차 예습 문제를 열었어요. 「다음」을 눌러 풀어 보세요.'))
        return frame(TH, sd('pre'), ('HAI-Mate', '예복습 문제'), main)
    OPT = ['주석을 작성하려면 세 개의 따옴표로 문자열 블록을 만들어야 한다.', '주석 내용은 실행 시 화면에 출력되므로 배포 전 반드시 삭제해야 한다.', "주석의 주된 목적은 코드가 '무엇'을 하는지를 상세히 기술하는 것이다.", "# 문자 뒤에 작성되며 '왜' 그 코드를 작성했는지를 설명한다."]
    EXP = "주석은 # 문자 뒤에 오는 문장으로 작성해요. 코드는 '어떻게'를 말해 주고, 주석은 '왜' 그렇게 작성했는지를 설명하는 데 써요."
    def solve():
        opts = ''.join(f'<button type="button" class="mk-opt" data-on>{k + 1}. {t}</button>' for k, t in enumerate(OPT))
        main = ('<div class="mk-row"><div class="mk-h"><h3>← 11주차 예습</h3></div><span class="mk-row"><small>정답 확인 0/5</small><span class="mk-btn sm soft" style="cursor:default">제출 (0/5)</span></span></div>'
                '<div class="mk-pills"><span class="on">1</span><span>2</span><span>3</span><span>4</span><span>5</span></div>'
                f'<div class="mk-two"><div class="mk-box"><span class="mk-chip">문제 1</span><p><b>Q. 다음 중 파이썬 주석(comment)에 대한 설명으로 옳은 것은?</b></p><div class="mk-opts" id="mko">{opts}</div>'
                '<p class="mk-demo" data-need hidden>먼저 답을 하나 골라 주세요.</p><div class="mk-box tint" data-right hidden><b>정답이에요! (정답 4번)</b><span>' + EXP + '</span></div><div class="mk-box tint" data-wrong hidden><b>아쉬워요. 정답은 4번이에요.</b><span>' + EXP + '</span></div>'
                '<div class="mk-row end"><button type="button" class="mk-btn" data-check="#mko|3" data-goal>정답확인</button></div></div>'
                f'<div class="mk-box"><div class="mk-row"><span class="mk-lbl">출처</span><span class="mk-link">byte_of_python_5장.pdf p.1</span></div><div class="mk-sheet"><p><b>5장. 기초</b></p><p><b>5.1 주석</b></p><p>주석은 # 문자 뒤에 따라오는 문장입니다. 주로 소스 코드를 읽는 사람들을 위해 주석을 남기는 용도로 빈번하게 사용됩니다.</p><p class="mk-code" style="min-height:0">print(\'hello world\')  # print는 함수입니다</p></div></div></div>')
        return frame(TH, sd('pre'), ('HAI-Mate', '문제 풀기'), main)
    def result():
        QL = [('다음 중 파이썬 주석(comment)에…', 1), ("다음 중 파이썬에서 '변수(variable)…", 1), ('format() 메소드를 사용한 다음 코…', 1), ("파이썬에서 '물리적 명령행(physica…", 0), ('PyCharm에서 예제 파이썬 프로그…', 1)]
        lst = ''.join(f'<button type="button" class="mk-rowbtn{" on" if k == 0 else ""}" data-on data-hide="[data-d]" data-show="[data-d={chr(39)}{0 if k == 0 else 9}{chr(39)}]"{" data-goal" if k == 0 else ""}><span>{k + 1}　{t}</span><span class="mk-st {"ok" if ok else "ing"}">{"정답" if ok else "오답"}</span></button>' for k, (t, ok) in enumerate(QL))
        det = ('<div class="mk-box" data-d="0" hidden><div class="mk-row"><span class="mk-chip">문제 1</span><span class="mk-st ok">정답</span></div><p><b>Q. 다음 중 파이썬 주석(comment)에 대한 설명으로 옳은 것은?</b></p>'
               + ''.join(f'<span class="mk-opt{" on" if k == 3 else ""}" style="cursor:default">{k + 1}. {t}</span>' for k, t in enumerate(OPT)) + '<div class="mk-box tint"><b>A. 4</b><span>' + EXP + '</span><span class="mk-ref">출처: byte_of_python_5장.pdf p.1</span></div></div>'
               '<div class="mk-box" data-d="9" hidden><p class="mk-demo">체험판에는 1번 문항의 정답과 해설만 들어 있어요. 실제 서비스에서는 모든 문항의 정답·오답과 해설을 다시 볼 수 있어요.</p></div>'
               '<div class="mk-box" data-d="x"><p class="mk-ref">왼쪽 목록에서 문항을 누르면 내 답안과 정답, 해설이 여기에 보여요.</p></div>')
        main = ('<div class="mk-row"><div class="mk-h"><h3>← 11주차 예습</h3></div><span class="mk-row"><span class="mk-st ok">제출 완료</span><small>정답 4 / 오답 1</small></span></div>'
                f'<div class="mk-two"><div class="mk-opts">{lst}</div><div>{det}</div></div>')
        return frame(TH, sd('pre'), ('HAI-Mate', '결과 확인'), main)
    I = 'media/walk/hai-mate/'
    return [
        dict(title='강좌를 골라요', text='로그인한 뒤 학년도·학기를 확인하고 「나의 강좌」에서 학습할 강좌를 선택해요. 챗봇 튜터, 학습 자료, 예복습 문제, 퀴즈 메뉴가 열려요.', do='「나의 강좌」에서 「창의코딩파이썬-1」 강좌를 눌러 보세요.', ui=home(), img=I + '1.jpg'),
        dict(title='챗봇 튜터에게 물어봐요', text='「챗봇 튜터」에서 새 대화를 시작하고 궁금한 점을 입력해요. 강좌 자료를 근거로 답하고 참고 자료도 보여 줘요.', do='입력창에 궁금한 점을 쓰고 보내 보세요. 비워 둔 채 보내면 예시 질문이 입력돼요.', ui=chat(), img=I + '2.jpg'),
        dict(title='예습·복습 문제를 골라요', text='「예복습 문제」에서 주차와 예습·복습 구분을 확인하고, 공개 기간 안에 있는 문제를 선택해요.', do='목록에서 「11주차 예습」을 눌러 문제를 열어 보세요.', ui=plist(), img=I + '3.jpg'),
        dict(title='문제를 풀고 정답을 확인해요', text='답을 고른 뒤 「정답확인」을 누르면 정오와 해설, 출처를 바로 볼 수 있어요. 모든 문항을 확인하면 제출해요.', do='보기 가운데 답을 하나 고르고 「정답확인」을 눌러 보세요.', ui=solve(), img=I + '4.jpg'),
        dict(title='결과를 다시 살펴봐요', text='제출 후에도 문항별 정답·오답과 해설을 다시 볼 수 있어요. 결과는 교수님 화면에도 반영돼요.', do='왼쪽 목록에서 1번 문항을 눌러 정답과 해설을 다시 확인해 보세요.', ui=result(), img=I + '5.jpg'),
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
                '<button type="button" class="' + ('on' if agent else '') + '" data-on data-hide="[data-nm]" data-show="[data-sa]"' + (' data-goal' if goal else '') + '>Super Agent</button></div><span class="mk-chip">한림대학교 구성원</span></div>')
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
        dict(title='한림 계정으로 로그인해요', text='기존 한림 계정(SSO) 그대로 로그인하면 HAI-GPT 메인 채팅 화면으로 들어가요.', do='「로그인」을 눌러 한림 계정으로 들어가 보세요.', img=I + '1.jpg',
             ui=login(TH, ('HALLYM UNIVERSITY', 'The New Hallym,<br>K-University of the Future', '한림대학교 통합 로그인'), ('한국어 · English', '로그인'), [('ID', 'ID', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', True, True)], foot='비밀번호 초기화 · 도움말')),
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
        dict(title='학번/사번으로 로그인해요', text='한림대학교 LXP 접속 페이지에서 개인 계정으로 로그인하면 강의실에 들어갈 수 있어요.', do='학번(사번)과 비밀번호 칸을 확인하고 「로그인」을 눌러 보세요.', img=I + '1.jpg',
             ui=login(TH, ('HALLYM UNIVERSITY', '한림대학교 LXP', '인공지능(AI) 기반 학습 경험 플랫폼'), ('LXP', '로그인'), [('학번/사번', '학번 또는 사번', 'text'), ('비밀번호', '비밀번호', 'password')], [('로그인', True, True)], foot='한림대학교 LXP에 오신 것을 환영합니다.')),
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

MOCKS = {'hai-docs': _docs(), 'hai-tutor': _tutor(), 'hai-mate': _mate(), 'hai-gpt': _gpt(), 'hai-mathtutor': _math(), 'lxp': _lxp(), 'hai-forum': _forum()}

MK_CSS = r"""
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
.mk-pills { display: flex; flex-wrap: wrap; gap: 6px; } .mk-pills > * { padding: 3px 10px; border: 1px solid #dbe3f0; border-radius: 999px; background: #fff; font-size: 12px; color: #475569; } .mk-pills > .on { background: var(--mk); border-color: var(--mk); color: #fff; font-weight: 700; }
.mk-opts { display: flex; flex-direction: column; gap: 6px; } .mk-opt { display: flex; align-items: center; gap: 10px; padding: 9px 12px; border: 1px solid #e5e9f2; border-radius: 10px; background: #fff; text-align: left; } .mk-opt::before { content: ''; flex: none; width: 14px; height: 14px; border-radius: 50%; border: 2px solid #cbd5e1; } .mk-opt.on { border-color: var(--mk); background: #f3f7ff; } .mk-opt.on::before { border-color: var(--mk); background: radial-gradient(var(--mk) 45%, #fff 50%); }
.mk-tbl { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #e5e9f2; border-radius: 10px; overflow: hidden; font-size: 12.5px; } .mk-tbl th { padding: 8px 10px; background: #f1f5fb; color: #64748b; font-weight: 700; text-align: left; white-space: nowrap; } .mk-tbl td { padding: 9px 10px; border-top: 1px solid #f1f4f9; } .mk-tbl tr.on td { background: #f3f7ff; } .mk-tbl button { border: 0; background: none; padding: 0; color: inherit; text-align: left; font-weight: 700; }
.mk-rowbtn { display: flex; align-items: center; justify-content: space-between; gap: 10px; width: 100%; padding: 12px 14px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: left; } .mk-rowbtn:hover, .mk-card[type=button]:hover, .mk-opt:hover { border-color: var(--mk); } .mk-rowbtn small { display: block; color: #6b7280; font-weight: 400; }
.mk-bars { display: flex; flex-direction: column; gap: 8px; } .mk-bar2 { display: grid; grid-template-columns: 96px 1fr 44px; align-items: center; gap: 8px; width: 100%; padding: 4px 6px; border: 0; border-radius: 8px; background: none; text-align: right; font-size: 12.5px; } .mk-bar2 i { display: block; height: 16px; border-radius: 5px; background: #e8edf5; overflow: hidden; } .mk-bar2 i::after { content: ''; display: block; height: 100%; width: var(--v); background: var(--mk); border-radius: 5px; } .mk-bar2 b { text-align: left; } .mk-bar2.on, button.mk-bar2:hover { background: #eef4ff; }
.mk-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 10px; } .mk-stat { display: flex; flex-direction: column; gap: 2px; padding: 12px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: left; } .mk-stat small { color: #6b7280; } .mk-stat b { font-size: 20px; }
.mk-tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; } .mk-tile { display: flex; flex-direction: column; align-items: center; gap: 6px; padding: 16px 8px; border: 1px solid #e5e9f2; border-radius: 12px; background: #fff; text-align: center; } .mk-tile small { color: #6b7280; font-size: 11px; } .mk-tile .mk-ic { color: var(--mk); } .mk-tile.on { border-color: var(--mk); background: #f3f7ff; }
.mk-code { padding: 12px 14px; border-radius: 10px; background: #0b1020; color: #d6e2ff; font: 12.5px/1.6 ui-monospace, SFMono-Regular, Menlo, monospace; white-space: pre-wrap; min-height: 90px; } textarea.mk-code { width: 100%; border: 0; }
.mk-center { margin: auto; display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center; } .mk-up { display: flex; flex-direction: column; align-items: center; gap: 6px; width: 100%; padding: 22px 12px; border: 2px dashed #cbd5e1; border-radius: 12px; background: #fff; color: #64748b; } .mk-up:hover { border-color: var(--mk); color: var(--mk); }
.mk canvas[data-draw] { display: block; width: 100%; height: 150px; border: 1px dashed #b8c4d9; border-radius: 10px; background: #fff; touch-action: none; cursor: crosshair; } .mk-drawwrap { position: relative; } .mk-drawwrap > span { position: absolute; left: 0; right: 0; top: 50%; transform: translateY(-50%); text-align: center; color: #94a3b8; pointer-events: none; }
.mk-eg { align-self: flex-start; padding: 1px 8px; border-radius: 6px; background: #fff7e6; color: #92400e; font-size: 11px; } .mk-topbar { display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap; }
.mk-filechip { display: inline-flex; align-items: center; gap: 6px; padding: 5px 10px; border-radius: 8px; background: #eef2f8; font-size: 12px; } .mk-two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; } .mk-grow { flex: 1; }
@container (max-width: 700px) { .mk-aside { display: none; } .mk { flex-wrap: wrap; } .mk-aside.mk-keep { display: flex; width: 100% !important; border-left: 0; border-top: 1px solid #e5e9f2; } }
@container (max-width: 560px) { .mk-hero { display: none; } .mk-tiles { grid-template-columns: repeat(2, minmax(0, 1fr)); } .mk-two { grid-template-columns: 1fr; } .mk-bar2 { grid-template-columns: 72px 1fr 40px; } .mk-side { display: none; } .mk-top { display: flex; align-items: center; gap: 8px; margin: -16px -14px 0; padding: 9px 14px; background: var(--mk-side); color: #fff; } .mk-top span { opacity: .8; font-size: 12px; } .mk-main { padding: 16px 14px; } .mk-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .mk-grid.two, .mk-srcs, .mk-fields { grid-template-columns: 1fr; } .mk-block { margin-left: 0; } }
@media (max-width: 860px) { .walk-main.uimode { grid-template-rows: minmax(0, 56%) minmax(0, 1fr); } .walk-shot.ui { padding: 0; } .mk { min-height: 100%; border-radius: 0; } .mk-main { max-height: none; } }
"""
