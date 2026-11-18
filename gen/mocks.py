# -*- coding: utf-8 -*-
"""HAI 체험관 「직접 해 보기」 — 실제로 눌리고 입력되는 체험용 화면(목업).
매뉴얼·소개자료에 실린 화면을 본떠 HTML로 다시 만든 것이며, 실제 서비스와 연결되지 않는다(입력 내용은 어디에도 보내지 않음).
화면 안 요소에 붙이는 속성(gen2.py WALK_JS 가 해석):
  data-goal        이 요소를 누르면(폼이면 보내면, 검색칸이면 입력하면) 미션 성공
  data-on          누르면 형제들 가운데 이것만 .on
  data-filter=K    [data-cat] 가운데 K 만 보이기(all = 전부)   · data-search  입력한 글자가 들어간 [data-cat] 만 보이기
  data-show-now=S  바로 보이기 · data-wait=S  잠깐(1.1초) 보였다 숨기기(입력 중 표시) · data-show=S  그 뒤에 보이기 · data-hide=S  숨기기
  data-echo=S      폼에 쓴 글을 S 에 넣기 · data-set="S|글"  S 의 글자를 바꾸기 · data-step=N  [data-stepper] 의 N 번째까지 .on
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

def side(brand, sub, groups, active, user=None, foot=(), go=None):
    go = go or {}
    h = f'<aside class="mk-side"><div class="mk-brand"><strong>{brand}</strong>{("<small>" + sub + "</small>") if sub else ""}</div>'
    for label, items in groups:
        h += (f'<span class="mk-grp">{label}</span>' if label else '') + ''.join((f'<button type="button" class="mk-nav{" on" if k == active else ""}" data-go="{go[k]}">{ic(i)}{t}</button>' if k in go else f'<span class="mk-nav{" on" if k == active else ""}">{ic(i)}{t}</span>') for k, i, t in items)
    h += '<span class="mk-sp"></span>' + ''.join(f'<span class="mk-nav">{ic(i)}{t}</span>' for i, t in foot)
    if user: h += f'<div class="mk-user"><span class="mk-uav">{ic("user", 14)}</span><span><b>{user[0]}</b><small>{user[1]}</small></span></div>'
    return h + '</aside>'

def frame(theme, side_html, top, main, aside=''):
    return (f'<div class="mk" style="{theme}">{side_html}<div class="mk-main"><div class="mk-top"><b>{top[0]}</b><span>{top[1]}</span></div>{main}</div>{aside}</div>')

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

MOCKS = {'hai-docs': _docs()}

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
@container (max-width: 700px) { .mk-aside { display: none; } }
@container (max-width: 560px) { .mk-side { display: none; } .mk-top { display: flex; align-items: center; gap: 8px; margin: -16px -14px 0; padding: 9px 14px; background: var(--mk-side); color: #fff; } .mk-top span { opacity: .8; font-size: 12px; } .mk-main { padding: 16px 14px; } .mk-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } .mk-grid.two, .mk-srcs, .mk-fields { grid-template-columns: 1fr; } .mk-block { margin-left: 0; } }
@media (max-width: 860px) { .walk-main.uimode { grid-template-rows: minmax(0, 56%) minmax(0, 1fr); } .walk-shot.ui { padding: 0; } .mk { min-height: 100%; border-radius: 0; } .mk-main { max-height: none; } }
"""
