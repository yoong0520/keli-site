# -*- coding: utf-8 -*-
"""KELI 플랫폼 v2 사이트 생성기 — 리플렛 기준 · 메뉴 5 · 페이지 12 · 게시판 6 · Apple/Samsung 톤"""
import os, html, json, re, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 저장소 루트(gen/의 상위)
OUT = BASE
CONTENT = os.path.join(BASE, 'content')                                  # 관리자가 고치는 글 데이터
IMG_SRC = '/mnt/user-data/outputs/keli-portal-html/assets/img'           # 있을 때만 서비스 화면 이미지를 복사
REPO = 'yoong0520/keli-site'
SITE_URL = 'https://keli-aied.org/'

def _load_json(path, default):
    try:
        return json.load(open(path, encoding='utf-8'))
    except Exception:
        return default
E = html.escape
SITE = 'KELI'
EMAIL = 'contact@keliedu.org'
INSTA = 'https://www.instagram.com/hallym_keli/'
PHONE = '033-248-3044'
STAFF = '전형준'

# ------------------------------------------------------------------ 데이터
AREAS = [
    ('platform', '통합 플랫폼', 'Platforms'),
    ('career', '진로·연구', 'Career'),
    ('courseware', '전공 코스웨어', 'Courseware'),
    ('teaching', '학습·수업 지원', 'Teaching'),
    ('analytics', '분석·데이터', 'Analytics'),
    ('admin', '행정·평가', 'Admin'),
]
AREA_LABEL = {a[0]: a[1] for a in AREAS}
DRIVE = 'https://drive.google.com/file/d/%s/view'
GUIDE = 'https://ai.hallym.ac.kr/media/uploads/guides/%s.pdf'
DEMO_ALL = 'https://keliedu.org/keli/partners/video'
MANUAL_SITE = 'https://haimanual.csedu4all.com'

# (slug, name, area, one-liner(리플렛), headline, desc, features, usage, status, url, img, video, manual, stage)
SERVICES = [
    dict(slug='keli', name='KELI', area='platform', one='고등교육 AI 공유 플랫폼',
         head='고등교육 AI를 함께 설계·검증·확산하는 공유 플랫폼.',
         desc='대학·기업·기관이 교육 과제와 기술을 연결하고 실제 교육환경에서 적용 가능성을 함께 검증하는 고등교육 특화 협력 플랫폼입니다.',
         features=['대학 수요와 교육 과제 발굴', '기술 파트너 및 솔루션 연결', '실제 수업 기반 PoC 실증'],
         usage='대학별 회원과 권한을 관리하고 자료·서비스·협업 정보를 한 곳에서 공유합니다.',
         status='live', url='https://keliedu.org/keli', img='keli-logo.png', video=None, manual=None, stage=[]),
    dict(slug='hai-ai', name='HAI-AI', area='platform', one='AI 서비스 통합 포털',
         head='한림 AI 교육 서비스와 활용 정보를 연결하는 통합 포털.',
         desc='대학 구성원이 여러 AI 서비스를 한 번에 탐색하고 자신의 역할에 맞는 기능으로 빠르게 연결되도록 설계된 통합 접근 플랫폼입니다.',
         features=['통합 서비스 진입점 제공', '역할 기반 서비스 안내', '플랫폼 간 빠른 이동 지원'],
         usage='교수·학생·직원이 필요한 AI 서비스를 빠르게 선택하고 활용 환경으로 이동합니다.',
         status='live', url='https://ai.hallym.ac.kr/', img='hallym_portal_logo.png', video=None, manual=None, stage=[]),
    dict(slug='hai-way', name='HAI-Way', area='career', one='AI 진로 설계 플랫폼',
         head='진로·수강·채용 정보를 연결하는 커리어 인바디.',
         desc='진로 목표와 수강 이력을 바탕으로 맞춤형 커리큘럼과 직무를 추천하고, 포트폴리오 생성과 채용공고 추천·피드백을 지원합니다.',
         features=['커리큘럼·직무 추천', '포트폴리오 자동 생성', '채용공고 추천·피드백'],
         usage='학생은 수강 이력과 목표를 바탕으로 직무·교과를 추천받고 진로 포트폴리오를 만듭니다.',
         status='live', url='https://cib.k-university.ai', img='hai-way.jpg', video=DRIVE % '1ouC6XEhAb8Rha2LaxgFCv_WspJJdGM7o', manual=GUIDE % 'fcf51da27ef644c39444f158fc0b5119', stage=[]),
    dict(slug='hai-research', name='HAI-Research', area='career', one='AI 연구자 매칭',
         head='산학·교내 공동연구 파트너를 찾는 AI 연구자 매칭.',
         desc='연구자의 전문분야·성과·논문 주제를 분석하여 기업의 산학연구 수요와 교내 공동연구 주제에 적합한 연구자와 연구팀을 추천합니다.',
         features=['전문분야·성과 분석', '연구수요 기반 탐색', '연구팀 시너지 분석'],
         usage='기업의 연구 과제나 교내 공동연구 주제에 적합한 연구자와 팀 구성을 추천받습니다.',
         status='live', url='http://hairesearch.k-university.ai/', img='hai-research.jpg', video=DRIVE % '1L3boYfEaQWnsyFJb1-C8S56U1LYHU6gQ', manual=None, stage=[]),
    dict(slug='hai-mathtutor', name='HAI-MathTutor', area='courseware', one='AI 수학 튜터',
         head='풀이 과정과 오류를 진단하는 초개인화 AI 수학 튜터.',
         desc='수학 온톨로지 기반 문제은행과 교수자 문항 설계를 지원하고, 학습자의 손글씨 풀이 과정과 오류를 진단해 단계별 힌트를 제공하는 선형대수 특화 튜터입니다.',
         features=['수학 온톨로지 문제은행', '손글씨 풀이·오류 진단', '단계별 힌트 제공'],
         usage='학생은 풀이 과정에 맞춘 단계별 힌트를 받고 교수자는 문제은행과 학습 이력을 관리합니다.',
         status='live', url='https://math-ai.k-university.ai/hallym/auth/signin?from=aihub', img='hai-mathtutor.jpg', video=DRIVE % '17dGc2e8crL9khoAhDLZn0buaGU7FicXJ', manual=GUIDE % '901aae536b7a4abea39d7cdff831382d', stage=['practice']),
    dict(slug='hai-fist', name='HAI-FIST', area='courseware', one='과학수사 AI 코스웨어',
         head='융합과학수사 수업을 지원하는 사례·TBL 기반 AI 코스웨어.',
         desc='주교재를 분석해 강의계획·마인드맵·요약 콘텐츠를 생성하고, 판례 기반 모의범죄 시나리오와 퀴즈·학습분석을 제공하는 융합과학수사 전용 코스웨어입니다.',
         features=['교재 기반 강의계획·요약 생성', '판례 기반 모의범죄 시나리오', '퀴즈·학습분석'],
         usage='실제 판례 기반 모의범죄 시나리오로 팀 학습을 수행하고 학습성과를 확인합니다.',
         status='live', url='https://fist.k-university.ai', img='hai-fist.jpg', video=DRIVE % '1qbnn2do2fWm_QpIpJZk62R9jV0Op7m9m', manual=GUIDE % 'b4b55b5cdc494b1eb66eca4237f529fc', stage=['content', 'practice']),
    dict(slug='hai-korean', name='HAI-Korean', area='courseware', one='AI 한국어 코스웨어',
         head='TOPIK 문제·다국어 해설·발음 피드백을 제공하는 코스웨어.',
         desc='한국어 읽기, 쓰기, 표현, 교정 기능을 제공하여 언어 학습과 학문적 표현 역량을 강화하는 AI 기반 학습 서비스입니다.',
         features=['TOPIK 문제 생성', '숙달도별·다국어 해설', '발음·억양 피드백'],
         usage='글쓰기 과제와 한국어 학습 활동에서 표현 개선과 교정을 지원받습니다.',
         status=None, url=None, img=None, video=None, manual=None, stage=['practice']),
    dict(slug='hai-coder', name='HAI-Coder', area='courseware', one='AI 코딩 코스웨어',
         head='학습데이터로 문제·해설·경로를 설계하는 AI 코딩 코스웨어.',
         desc='기출·학습데이터를 기반으로 맞춤형 문제와 해설·학습경로를 제안하고, 오답 노트와 시계열 학습분석 대시보드를 제공하는 코딩 코스웨어입니다.',
         features=['맞춤형 문제·해설', 'AI 학습경로 설계', '취약개념 노트·학습패턴 분석'],
         usage='프로그래밍 수업에서 학생이 코드 오류를 스스로 수정하고 과제를 개선합니다.',
         status='soon', url=None, img='hai-coder.jpg', video=DRIVE % '1RidGGYe28QNLxuNL320GZ-8H5Vu03FNF', manual=GUIDE % '9f1110a24e714f1d8a74f4ed91c3316e', stage=['practice']),
    dict(slug='hai-security', name='HAI-Security', area='courseware', one='네트워크 보안 코스웨어',
         head='실무형 보안도구와 공격 시뮬레이션을 활용하는 코스웨어.',
         desc='학습자 수준별 보안 자료와 트러블슈팅 가이드를 제공하고, SIEM 기반 독립 실습환경과 실제 공격데이터 기반 시나리오를 제공하는 네트워크 보안 코스웨어입니다.',
         features=['수준별 보안 자료·가이드', 'SIEM 기반 독립 실습환경', '공격데이터 기반 시나리오'],
         usage='보안 관련 과목에서 개념 학습과 실습 과제를 연계해 수행합니다.',
         status='soon', url=None, img='hai-security.jpg', video=DRIVE % '1jnvuixsXhdpg6cMFU2a1ojJw9bLudsL9', manual=GUIDE % 'b8a835b53c734079a9a172af4b5bc863', stage=['practice']),
    dict(slug='hai-medlearn-x', name='HAI-MedLearn-X', area='courseware', one='AI 의학교육 플랫폼',
         head='교재 기반 의학교육 콘텐츠를 자동 생성하는 AI 코스웨어.',
         desc='교재 PDF를 OCR·다중 LLM으로 분석해 팟캐스트·퀴즈·임상 증례를 생성하고, 교과 특화 학습 시나리오와 출처 기반 RAG 질의응답을 제공합니다.',
         features=['PDF·다중 LLM 분석', '팟캐스트·퀴즈·증례 생성', '출처 기반 RAG 답변'],
         usage='교수자는 교재로 수업 전후 콘텐츠를 만들고 학생은 출처가 표시된 답변을 확인합니다.',
         status='live', url='https://mlx.k-university.ai/', img='hai-medlearnx.jpg', video=DRIVE % '1igf-qVcJnQdAsUjmMIaTYXvabjp-JcY8', manual=GUIDE % 'bf687738e24141fdaa532fa06ba7e63c', stage=['content']),
    dict(slug='hai-forum', name='HAI-Forum', area='teaching', one='액티브러닝 플랫폼',
         head='화상수업·AI 채점·학습분석을 결합한 액티브러닝 플랫폼.',
         desc='설치 없는 화상 세미나와 투표·퀴즈·분반토론을 지원하고, 서술형·코드 자동 채점과 발언·학습데이터 분석을 통한 조기 경보를 제공하는 플랫폼입니다.',
         features=['화상강의·투표·퀴즈·분반토론', '서술형·코드 자동채점', '조기 경보·학습분석'],
         usage='화상수업에서 토론과 퀴즈를 운영하고 AI 채점 결과와 학습 위험 신호를 확인합니다.',
         status='live', url='https://haiforum.k-university.ai', img='hai-forum.jpg', video=DRIVE % '1___3MHdpXRZi0DBiP-o1pseNaK2Fx3W8', manual=GUIDE % '1bb328c83e834c39bbc809e1cc7ccd36', stage=['class']),
    dict(slug='hai-pbl', name='HAI-PBL', area='teaching', one='PBL 협업 플랫폼',
         head='화상 협업·활동분석·포트폴리오를 결합한 PBL 시스템.',
         desc='화상수업과 마인드맵·칸반보드를 통합하고, AI로 팀 기여도와 문제해결 과정을 분석해 대시보드와 누적형 직무역량 포트폴리오를 제공합니다.',
         features=['화상협업·마인드맵·칸반보드', '팀 활동 AI 분석', '역량 포트폴리오'],
         usage='팀의 화상 협업 기록과 산출물을 분석해 기여도와 역량을 포트폴리오로 축적합니다.',
         status='soon', url=None, img='hai-pbl.jpg', video=DRIVE % '1oEOAzXWvekrEPQBLw29gtbOD25hr_z_3', manual=GUIDE % '49e68ed9bb79409097f44e3d6adf62b0', stage=['class']),
    dict(slug='hai-ai-prof', name='HAI-AI Prof', area='teaching', one='AI 교수 아바타 강의',
         head='AI 교수 아바타가 강의하는 서비스.',
         desc='AI 교수 아바타가 강의를 진행하는 서비스입니다. 상세 설명과 핵심 기능은 사무국 확정 후 반영됩니다.',
         features=[], usage='', status=None, url=None, img=None, video=None, manual=None, stage=['design']),
    dict(slug='hai-mate', name='HAI-Mate', area='teaching', one='수업 운영 AI 튜터',
         head='예복습·퀴즈·학생용 챗봇을 지원하는 교과목 지원 시스템.',
         desc='교과목 운영을 돕는 지원 시스템으로, 예복습과 퀴즈, 학생용 챗봇 기능을 제공합니다.',
         features=['예습·복습 지원', '퀴즈', '학생용 챗봇'],
         usage='',
         status='live', url='https://haimate.k-university.ai/v2/login', img='hai-mate.jpg', video=DRIVE % '1MytFy-Hq212246VvimqILDVdgKpSWqrn', manual=GUIDE % 'dae85c489b4c4abc893dba8dbae29d64', stage=['design', 'class']),
    dict(slug='hai-sync', name='HAI-Sync', area='teaching', one='AI 학습 파트너',
         head='AI 마이크로러닝 기반 자기주도 학습 플랫폼.',
         desc='AI 마이크로러닝을 기반으로 학습자의 자기주도 학습을 지원하는 플랫폼입니다. 상세 기능은 사무국 확정 후 반영됩니다.',
         features=[], usage='',
         status='soon', url=None, img='hai-sync.jpg', video=DRIVE % '1cnyxtGTVgaDDmCLuLsZPeILUtoN24jki', manual=GUIDE % '1586248eb4c948e0aab306892a7cd09a', stage=['practice']),
    dict(slug='hai-lrs', name='HAI-LRS', area='analytics', one='학습데이터 분석 인프라',
         head='xAPI 기반 학습데이터 통합·분석 인프라.',
         desc='AI와 국제표준 xAPI를 활용해 학습데이터를 통합 수집·저장·분석하고, 맞춤형 이탈 예측·피드백과 타 대학 확장을 지원하는 클라우드 플랫폼입니다.',
         features=['xAPI 학습기록 수집', '데이터 통합·분석', '이탈 예측·맞춤 피드백'],
         usage='여러 시스템의 학습기록을 통합해 이탈 위험을 예측하고 맞춤형 피드백에 활용합니다.',
         status='live', url='http://hailrs.k-university.ai', img='hai-lrs.jpg', video=DRIVE % '17lOBCCpcQluv9_qoNAPbftaRun4qK21w', manual=GUIDE % '3ccfe2b0965547fab06e94fa7c1d0b45', stage=['analysis']),
    dict(slug='hai-lens', name='HAI-Lens', area='analytics', one='AI 강의 분석 시스템',
         head='오프라인 강의를 4채널로 분석하는 AI 통합 시스템.',
         desc='오프라인 강의를 온라인 콘텐츠로 자동 전환하고, 음성·자료·영상·청중 반응을 통합 분석해 집중도와 구체적인 강의 개선 코칭을 제공합니다.',
         features=['오프라인 강의 자산화', '음성·자료·영상·반응 4채널 분석', 'AI 리포트·코칭'],
         usage='강의의 4채널 데이터를 분석해 청중 집중도와 구체적인 개선 제안을 확인합니다.',
         status='soon', url=None, img='hai-lens.jpg', video=DRIVE % '1JYRG0-kqpO6M7Ak4w3JCKBp75b7tuS6I', manual=None, stage=['analysis']),
    dict(slug='hai-check', name='HAI-Check', area='admin', one='AI 적응형 평가 플랫폼',
         head='학생 수준에 맞춰 문항을 조절하는 AI 적응형 진단평가.',
         desc='문해력·영어·SW 기초학력 문항을 구축하고, CAT 방식으로 난이도를 실시간 조절해 학생 수준을 진단하며 결과 조회·관리를 지원합니다.',
         features=['기초학력 문항 구축', '실시간 적응형 CAT', '수준 판별 규준'],
         usage='학생은 수준에 맞는 문항으로 진단받고 대학은 결과를 조회해 지원 계획에 활용합니다.',
         status='live', url='https://haicheck.k-university.ai/admin', img='hai-check.jpg', video=DRIVE % '1QrLzq8VLc3utfuchE8tVpkL85fesOilw', manual=GUIDE % '1527c4a963894138bc8ebbe6c2746184', stage=['assess']),
    dict(slug='hai-docs', name='HAI-Docs', area='admin', one='AI 행정 플랫폼',
         head='근거 답변·HWP 생성·감사 추적을 지원하는 행정 플랫폼.',
         desc='대학 규정·지침 원문에 근거한 답변과 출처를 제공하고, 기존 HWP 서식의 문서 초안과 답변·생성 이력의 감사 추적을 지원하는 AI 행정 플랫폼입니다.',
         features=['규정 기반 RAG 답변·출처', 'HWP 문서 생성', '이력·근거 감사 추적'],
         usage='행정 문서를 빠르게 찾고 핵심 내용을 확인하며 업무에 필요한 근거를 정리합니다.',
         status='soon', url=None, img='hai-docs.jpg', video=DRIVE % '1rmvZILkIQrsGk0oQnxve5mvvy08coRLA', manual=GUIDE % '510f1ce09cf842338ea5b8081d8d2635', stage=['analysis']),
]
STAGES = [('design', '설계'), ('content', '콘텐츠 생성'), ('class', '수업·상호작용'), ('practice', '실습·학습'), ('assess', '평가'), ('analysis', '분석·개선')]
STATUS = {'live': ('운영 중', 'live'), 'soon': ('오픈 예정', 'soon')}

UNIV = ['건양대학교', '계명대학교', '대전과학기술대학교', '대전대학교', '동서대학교', '동의대학교', '배재대학교', '백석문화대학교', '부산대학교', '서울시립대학교', '서울신학대학교', '아주대학교', '안산대학교', '우송대학교', '원광대학교', '위덕대학교', '인하대학교', '제주대학교', '충남대학교', '포항공과대학교', '한림대학교', '한성대학교', '호서대학교']
CORP = ['HM컴퍼니', '가르침에듀', '나이테듀', '니어네트웍스', '더캣코리아', '데이디', '디큐', '디피니션', '마인드로직', '문제G', '미라크소프트', '소풍앤컴퍼니', '수퍼코딩', '슈퍼러닝', '씨즈소프트', '아이스크림 arts', '아이오테드', '언택트에듀', '엘렉시', '온율티', '유비온', '인텔리시스', '인튜브', '지키다', '청운정보', '캐모릭스', '클라썸', '택스캔바스', '프리윌린', '플랭', '하이브시스템']

NOTICE_CATS = [('general', '일반'), ('recruit', '모집'), ('press', '보도')]
_NOTICE_KEY = {'일반': 'general', '모집': 'recruit', '보도': 'press'}
def _load_notices():
    items = _load_json(os.path.join(CONTENT, 'notices.json'), {}).get('items', [])
    items = [n for n in items if n.get('published', True) and n.get('title')]
    items.sort(key=lambda n: (not n.get('pinned'), ''), reverse=False)
    items.sort(key=lambda n: n.get('date', ''), reverse=True)
    items.sort(key=lambda n: 0 if n.get('pinned') else 1)
    return items
NOTICES = _load_notices()
def _load_archive():
    items = _load_json(os.path.join(CONTENT, 'archive.json'), {}).get('items', [])
    return [a for a in items if a.get('published', True) and a.get('title')]
ARCHIVE = _load_archive()
def _auto_covers():
    """표지가 없고 PDF 첨부가 있으면 첫 장을 표지로 만든다(pdftoppm, 있을 때만)"""
    import subprocess, shutil as _sh
    if not _sh.which('pdftoppm'):
        return
    os.makedirs(os.path.join(BASE, 'media', 'archive'), exist_ok=True)
    for a in ARCHIVE:
        if a.get('cover'):
            continue
        pdfs = [f for f in (a.get('files') or []) if str(f.get('url', '')).lower().endswith('.pdf') and os.path.exists(os.path.join(BASE, f['url']))]
        if not pdfs:
            continue
        out = os.path.join(BASE, 'media', 'archive', 'auto-' + a['id'])
        if not os.path.exists(out + '.jpg'):
            try:
                subprocess.run(['pdftoppm', '-f', '1', '-l', '1', '-r', '110', '-jpeg', '-singlefile', os.path.join(BASE, pdfs[0]['url']), out], check=True, capture_output=True, timeout=120)
            except Exception as e:
                print('auto cover failed', a['id'], e); continue
        a['cover'] = f'media/archive/auto-{a["id"]}.jpg'
# _auto_covers()  # 표지 그림 사용 안 함(사무국 결정)
HIDDEN = _load_json(os.path.join(CONTENT, 'hidden.json'), {})
def _not_hidden(kind, items):
    h = set(str(x) for x in HIDDEN.get(kind, []))
    return [it for it in items if str(it.get('id')) not in h]
ARCH_CATS = [('case', '실증 사례집'), ('trend', '기술 동향·연구'), ('manual', '매뉴얼·소개자료')]

# ------------------------------------------------------------------ CSS
CSS = r"""
/* 레이아웃: 1200px 컨테이너, 섹션 여백으로 구분, 흰 바탕·검정 글·KELI 블루 하나 */
:root {
  --bg: #ffffff; --bg2: #f5f5f7; --fg: #1d1d1f; --muted: #6e6e73; --line: #d2d2d7;
  --accent: #0B5CFF; --accent-fg: #ffffff; --pink: #ef8aa5; --ok: #1a6b30; --ok-bg: #e3f3e7; --soon: #7a5200; --soon-bg: #fff1cc;
  --s1: #0B5CFF; --s1-bg: #e6eeff; --s2: #0e6b55; --s2-bg: #e1f4ee; --s3: #a14a00; --s3-bg: #fff0dc; --s4: #4b2fbf; --s4-bg: #ece8ff; --s5: #b02457; --s5-bg: #fde6ee; --s6: #3b6b10; --s6-bg: #ebf5df;
  --font: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard", "Noto Sans KR", "Malgun Gothic", sans-serif;
}
/* 기기 다크 모드와 무관하게 항상 흰 바탕(사무국 결정 2026-11-03). 다크는 html[data-theme="dark"]를 직접 넣을 때만 */
:root { color-scheme: light; }
:root[data-theme="dark"] { --bg: #000000; --bg2: #1d1d1f; --fg: #f5f5f7; --muted: #a1a1a6; --line: #424245; --accent: #2997ff; --accent-fg: #ffffff; --ok: #7ad48f; --ok-bg: #0f2a16; --soon: #f5c35a; --soon-bg: #2e2306; --s1: #8fc0ff; --s1-bg: #10264a; --s2: #7fd9bf; --s2-bg: #0d2f27; --s3: #ffb36b; --s3-bg: #3a2208; --s4: #c2b3ff; --s4-bg: #221a4d; --s5: #ff9bbd; --s5-bg: #3d1424; --s6: #b8e08a; --s6-bg: #1e3010; color-scheme: dark; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--bg); color: var(--fg); font-family: var(--font); font-size: 17px; line-height: 1.75; -webkit-font-smoothing: antialiased; word-break: keep-all; overflow-wrap: break-word; }
body::before { content: ""; position: fixed; inset: 0 0 auto; height: env(safe-area-inset-top, 0px); z-index: 10; background: var(--bg); }
img { max-width: 100%; height: auto; display: block; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
button, input, select, textarea { font: inherit; color: inherit; }
button { cursor: pointer; }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
@media (prefers-reduced-motion: reduce) { * { transition: none !important; scroll-behavior: auto !important; } }
.wrap { max-width: 1200px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); }
.narrow { max-width: 760px; }
h1, h2, h3 { margin: 0; letter-spacing: -0.02em; line-height: 1.25; text-wrap: balance; word-break: keep-all; }
h2 { line-height: 1.3; }
p, li, dd, td, th, label, .lead, .card p, .li .t, .li .m, .svc .body p, .step p, .note, .hint { word-break: keep-all; overflow-wrap: anywhere; text-wrap: pretty; }
.lead { text-wrap: balance; }
a, .chip, .badge, .btn { word-break: keep-all; }
h1 { font-size: clamp(34px, 6vw, 60px); font-weight: 700; }
h2 { font-size: clamp(28px, 4vw, 40px); font-weight: 700; }
h3 { font-size: 20px; font-weight: 600; letter-spacing: -0.01em; line-height: 1.5; }
p { margin: 0; }
.muted { color: var(--muted); }
.small { font-size: 14px; }
.eyebrow { font-size: 15px; font-weight: 600; color: var(--muted); }
.lead { font-size: clamp(17px, 2vw, 21px); line-height: 1.65; color: var(--muted); }
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 6px; height: 48px; padding: 0 24px; border-radius: 999px; background: var(--accent); color: var(--accent-fg); font-weight: 600; font-size: 16px; border: 0; white-space: nowrap; }
.btn:hover { text-decoration: none; filter: brightness(.92); }
a.btn, .util a.btn, .mnav a.btn, .ftr a.btn { color: var(--accent-fg); }
a.btn.ghost, .util a.btn.ghost { color: var(--fg); }
[hidden] { display: none !important; }
.btn.sm { height: 36px; padding: 0 16px; font-size: 14px; }
.btn.ghost { background: var(--bg2); color: var(--fg); }
.btn[disabled], .btn.disabled { opacity: .5; cursor: not-allowed; }
.more { font-weight: 500; }
.more::after { content: " ›"; }
.badge { display: inline-flex; align-items: center; height: 24px; padding: 0 10px; border-radius: 999px; font-size: 12px; font-weight: 600; background: var(--bg2); color: var(--muted); }
.badge.live { background: var(--ok-bg); color: var(--ok); }
.badge.soon { background: var(--soon-bg); color: var(--soon); }
.badge.pink { background: var(--pink); color: #1d1d1f; }
/* header */
.hdr { position: sticky; top: env(safe-area-inset-top, 0px); z-index: 20; background: color-mix(in srgb, var(--bg) 88%, transparent); backdrop-filter: saturate(180%) blur(20px); -webkit-backdrop-filter: saturate(180%) blur(20px); border-bottom: 1px solid var(--line); }
.hdr .bar { display: flex; align-items: center; justify-content: space-between; gap: 16px; height: 56px; }
.brand { font-weight: 800; font-size: 20px; letter-spacing: .06em; color: var(--fg); }
.brand:hover { text-decoration: none; } .brand img { display: block; height: 28px; width: auto; }
.nav { display: flex; align-items: center; gap: 28px; }
.nav a { color: var(--fg); font-size: 15px; }
.nav a.on { color: var(--accent); font-weight: 600; }
.util { display: flex; align-items: center; gap: 14px; }
.util a { color: var(--fg); font-size: 14px; }
.util .ico { display: inline-flex; width: 36px; height: 36px; align-items: center; justify-content: center; border-radius: 999px; }
.util .ico:hover { background: var(--bg2); }
.burger { display: none; width: 44px; height: 44px; border: 0; background: transparent; border-radius: 999px; }
.hdr .mnav { display: none; border-top: 1px solid var(--line); background: var(--bg); }
.mnav a { display: block; padding: 14px 0; border-bottom: 1px solid var(--line); color: var(--fg); font-size: 17px; }
.hdr .mnav[data-open="1"] { display: block; }
@media (max-width: 860px) { .nav, .util .txt { display: none; } .burger { display: inline-flex; align-items: center; justify-content: center; } }
/* sections */
.sec { padding-block: clamp(64px, 9vw, 120px); }
.sec.alt { background: var(--bg2); }
.sec.dark { background: #1d1d1f; color: #f5f5f7; }
.sec.dark .muted, .sec.dark .lead { color: #a1a1a6; }
.sec.dark .btn.ghost { background: #2c2c2e; color: #f5f5f7; }
.sec.dark .card { background: #2c2c2e; }
.sec.dark .badge { background: #3a3a3c; color: #d2d2d7; }
.head { display: flex; flex-direction: column; gap: 14px; margin-bottom: clamp(32px, 4vw, 56px); }
.head.center { align-items: center; text-align: center; }
.head .lead { max-width: 760px; }
.row { display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; flex-wrap: wrap; }
.grid { display: grid; gap: 20px; }
.g2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.g3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.g4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
@media (max-width: 1000px) { .g4 { grid-template-columns: repeat(2, minmax(0, 1fr)); } .g3 { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 640px) { .g2, .g3, .g4 { grid-template-columns: 1fr; } }
.grid > * { min-width: 0; }
.card { background: var(--bg2); border-radius: 20px; padding: 32px 28px; display: flex; flex-direction: column; gap: 16px; color: inherit; }
.card:hover { text-decoration: none; }
a.card:hover { background: color-mix(in srgb, var(--bg2) 85%, var(--fg) 6%); }
.sec.alt .card { background: var(--bg); }
.card .k { font-size: 13px; font-weight: 600; color: var(--muted); }
.card h3 { font-size: 19px; line-height: 1.55; }
.card > .more { margin-top: auto; }
.card.center { text-align: center; align-items: center; justify-content: center; padding: 36px 28px; }
.card.center h3 { max-width: 16em; }
.tbl td, .tbl th, .step p, .field .hint, .field .msg, .note, .hint, .chk span, details.li .body { line-height: 1.7; }
.stage { line-height: 1.5; }   /* 카드 끝 링크(›)는 카드 하단에 정렬 → 한 줄의 카드끼리 같은 위치 */
.card p { color: var(--muted); font-size: 15px; line-height: 1.75; margin: 0; }
.card .num { font-size: 40px; font-weight: 700; letter-spacing: -0.03em; color: var(--accent); line-height: 1; }
.hero { padding-block: clamp(72px, 10vw, 128px); text-align: center; }
.hero .wrap { display: flex; flex-direction: column; align-items: center; gap: 20px; }
.hero h1 { max-width: 900px; }
.hero h1.en { max-width: 1000px; font-size: clamp(32px, 4.6vw, 52px); }
.hero .lead { max-width: 760px; }
.hero .acts { display: flex; gap: 12px 24px; flex-wrap: wrap; justify-content: center; align-items: center; margin-top: 8px; }
.crumb { font-size: 13px; color: var(--muted); display: flex; gap: 8px; padding-top: 16px; flex-wrap: wrap; }
.crumb a { color: var(--muted); }
/* tabs */
.tabs { display: flex; gap: 8px; flex-wrap: wrap; }
.tab { height: 40px; padding: 0 18px; border-radius: 999px; border: 0; background: var(--bg2); color: var(--fg); font-size: 14px; font-weight: 500; }
.sec.alt .tab { background: var(--bg); }
.tab[aria-pressed="true"] { background: var(--fg); color: var(--bg); }
@media (max-width: 640px) { .tabs { flex-wrap: nowrap; overflow-x: auto; padding-bottom: 4px; } .tab { flex: 0 0 auto; } }
/* service cards */
.svc { display: flex; flex-direction: column; border-radius: 20px; overflow: hidden; background: var(--bg2); color: inherit; }
.svc:hover { text-decoration: none; background: color-mix(in srgb, var(--bg2) 85%, var(--fg) 6%); }
.sec.alt .svc { background: var(--bg); }
.svc .thumb { aspect-ratio: 16 / 10; max-width: 100%; background: var(--bg2); overflow: hidden; display: flex; align-items: center; justify-content: center; }
.svc .thumb img { width: 100%; height: 100%; object-fit: cover; object-position: top; }
.svc .thumb.logo img { object-fit: contain; padding: 28px; }
.svc .thumb .word { font-size: 28px; font-weight: 700; color: var(--muted); letter-spacing: -0.02em; }
.svc .body { padding: 20px 22px 24px; display: flex; flex-direction: column; gap: 6px; }
.svc .body .top { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.svc .body .k { font-size: 12px; font-weight: 600; color: var(--muted); }
.svc .body strong { font-size: 19px; font-weight: 600; letter-spacing: -0.01em; }
.svc .body p { font-size: 15px; color: var(--muted); }
/* lists */
.list { display: flex; flex-direction: column; border-top: 1px solid var(--line); }
.li { display: grid; grid-template-columns: 1fr auto; gap: 8px 24px; align-items: center; padding: 20px 4px; border-bottom: 1px solid var(--line); color: inherit; }
.li:hover { text-decoration: none; background: var(--bg2); }
.li .t { font-size: 17px; font-weight: 600; line-height: 1.55; }
.li .m { font-size: 14px; color: var(--muted); }
.li .d { font-size: 14px; color: var(--muted); white-space: nowrap; }
@media (max-width: 640px) { .li { grid-template-columns: 1fr; } .li .d { white-space: normal; } }
details.li { display: block; }
details.li summary { display: grid; grid-template-columns: 1fr auto; gap: 8px 24px; align-items: center; cursor: pointer; list-style: none; }
details.li summary::-webkit-details-marker { display: none; }
details.li .body { padding: 14px 0 6px; color: var(--muted); font-size: 15px; max-width: 760px; }
details.li .body p { margin: 0 0 10px; } details.li .body ul, details.li .body ol { margin: 0 0 10px; padding-left: 22px; } details.li .body li { margin: 2px 0; }
details.li .body img, details.li .body iframe { max-width: 100%; border-radius: 12px; } details.li .body table { border-collapse: collapse; } details.li .body td, details.li .body th { border-bottom: 1px solid var(--line); padding: 6px 10px; text-align: left; }
/* steps */
.steps { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px; }
.step { background: var(--bg2); border-radius: 20px; padding: 24px; display: flex; flex-direction: column; gap: 8px; }
.sec.alt .step { background: var(--bg); }
.step .n { font-size: 14px; font-weight: 700; color: var(--accent); }
.step strong { font-size: 19px; }
.step p { font-size: 15px; color: var(--muted); }
@media (max-width: 1100px) { .steps { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { .steps { grid-template-columns: 1fr; } }
/* tables */
.tbl-wrap { overflow-x: auto; }
table.tbl { width: 100%; border-collapse: collapse; font-size: 15px; }
table.tbl th, table.tbl td { text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
table.tbl th { color: var(--muted); font-weight: 600; font-size: 13px; }
/* forms */
.form { display: flex; flex-direction: column; gap: 18px; background: var(--bg2); border-radius: 24px; padding: clamp(20px, 4vw, 40px); }
.sec.alt .form { background: var(--bg); }
.field { display: flex; flex-direction: column; gap: 8px; min-width: 0; }
.field label { font-size: 14px; font-weight: 600; }
.field .hint { font-size: 13px; color: var(--muted); }
.field input, .field select, .field textarea { width: 100%; max-width: 100%; border: 1px solid var(--line); border-radius: 12px; padding: 13px 14px; background: var(--bg); color: var(--fg); font-size: 16px; }
.field input:focus, .field select:focus, .field textarea:focus { outline: 2px solid var(--accent); border-color: var(--accent); }
.field.err input, .field.err select, .field.err textarea { border-color: #c0392b; }
.field .msg { font-size: 13px; color: #c0392b; display: none; }
.field.err .msg { display: block; }
.chk { display: flex; gap: 10px; align-items: flex-start; font-size: 15px; }
.chk input { width: 18px; height: 18px; margin-top: 4px; }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.nowrap { white-space: nowrap; letter-spacing: -.02em; font-size: .93em; }
.chipgrps { display: flex; flex-direction: column; gap: 14px; }
.vid { display: flex; flex-direction: column; gap: 12px; }
.vid-play { position: relative; display: block; width: 100%; aspect-ratio: 16 / 9; border: 0; padding: 0; border-radius: 18px; overflow: hidden; background: #000; cursor: pointer; }
.vid-play img { width: 100%; height: 100%; object-fit: cover; display: block; opacity: .92; transition: transform .3s; }
.vid-play:hover img { transform: scale(1.03); }
.vid-play .play { position: absolute; left: 50%; top: 50%; width: 64px; height: 64px; margin: -32px 0 0 -32px; border-radius: 50%; background: rgba(255,255,255,.92); box-shadow: 0 6px 24px rgba(0,0,0,.25); }
.vid-play .play::after { content: ""; position: absolute; left: 26px; top: 20px; border-style: solid; border-width: 12px 0 12px 20px; border-color: transparent transparent transparent var(--accent); }
.vid-play .len { position: absolute; right: 10px; bottom: 10px; padding: 2px 8px; border-radius: 6px; background: rgba(0,0,0,.72); color: #fff; font-size: 12px; font-weight: 600; }
.vid iframe { width: 100%; aspect-ratio: 16 / 9; border: 0; border-radius: 18px; display: block; background: #000; }
.vid-body { display: flex; flex-direction: column; gap: 6px; } .vid-body .m { font-size: 13px; color: var(--muted); } .vid-body .t { font-size: 17px; font-weight: 600; line-height: 1.5; } .vid-body .more { font-size: 14px; }
.vids { gap: 28px 24px; }
.vid-ph { display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; background: linear-gradient(135deg, #0B5CFF, #4A8BFF 60%, #7FB0FF); color: #fff; font-weight: 700; font-size: 22px; letter-spacing: .02em; }
.g3.vids .vid-play .play { width: 52px; height: 52px; margin: -26px 0 0 -26px; } .g3.vids .vid-play .play::after { left: 20px; top: 15px; border-width: 11px 0 11px 18px; }
.arch-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 28px 24px; }
@media (max-width: 1199px) { .arch-grid { grid-template-columns: repeat(3, 1fr); } } @media (max-width: 899px) { .arch-grid { grid-template-columns: repeat(2, 1fr); gap: 20px 14px; } }
@media (max-width: 480px) { .arch-grid { grid-template-columns: 1fr; gap: 14px; } .acard { flex-direction: row; align-items: flex-start; gap: 14px; } .acard .acover { width: 96px; flex: 0 0 auto; } .acard .abody { padding-top: 4px; } }
.acard { display: flex; flex-direction: column; gap: 12px; color: inherit; } .acard:hover { text-decoration: none; } .acard:hover .acover { transform: translateY(-4px); box-shadow: 0 16px 36px rgba(0,0,0,.18); }
.acover { display: block; aspect-ratio: 3 / 4; border-radius: 14px; overflow: hidden; background: var(--bg2); box-shadow: 0 6px 20px rgba(0,0,0,.10); transition: transform .25s, box-shadow .25s; border: 1px solid var(--line); }
.acover img { width: 100%; height: 100%; object-fit: cover; object-position: top; display: block; }
.acover-ph { display: flex; align-items: center; justify-content: center; width: 100%; height: 100%; padding: 16px; text-align: center; background: linear-gradient(160deg, #0B5CFF, #4A8BFF 70%, #7FB0FF); color: #fff; font-weight: 700; font-size: 16px; line-height: 1.45; }
.abody { display: flex; flex-direction: column; gap: 4px; } .abody .t { font-size: 15px; font-weight: 600; line-height: 1.5; } .abody .m { font-size: 13px; color: var(--muted); line-height: 1.6; }
.arch-hero { display: grid; grid-template-columns: 1fr; gap: 0; align-items: start; text-align: left; max-width: 900px; margin: 0 auto; }
.arch-hero .acts { justify-content: flex-start; margin-top: 16px; } .arch-hero .eyebrow { display: inline-block; }
.arch-cover { border-radius: 16px; overflow: hidden; box-shadow: 0 18px 44px rgba(0,0,0,.18); border: 1px solid var(--line); background: var(--bg2); } .arch-cover img { display: block; width: 100%; }
@media (max-width: 760px) { .arch-hero { grid-template-columns: 1fr; gap: 24px; } .arch-cover { max-width: 260px; } }
.pdf-frame { width: 100%; height: min(78vh, 980px); min-height: 480px; border: 1px solid var(--line); border-radius: 16px; background: var(--bg2); }
.art-ol { padding-left: 22px; } .art-ol li { margin: 6px 0; }
.art-files { margin: 24px 0; padding: 18px 22px; border-radius: 16px; background: var(--bg2); }
.art-files a { word-break: break-all; overflow-wrap: anywhere; }
.art-files strong { display: block; font-size: 14px; margin-bottom: 6px; } .art-files ul { margin: 0; padding-left: 18px; } .art-files li { margin: 4px 0; }
/* 관리자 */
.adm { display: grid; grid-template-columns: 220px 1fr; gap: 40px; align-items: start; }
.adm-nav { position: sticky; top: 72px; display: flex; flex-direction: column; gap: 4px; }
.adm-nav a { display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; border-radius: 12px; color: var(--fg); font-weight: 500; }
.adm-nav a:hover { background: var(--bg2); text-decoration: none; } .adm-nav a.on { background: var(--fg); color: var(--bg); }
.adm-nav .cnt { font-size: 12px; color: var(--muted); } .adm-nav a.on .cnt { color: inherit; opacity: .7; }
.adm-main { min-width: 0; }
.adm-head { display: flex; justify-content: space-between; align-items: center; gap: 16px; flex-wrap: wrap; margin-bottom: 20px; }
.adm-head h2 { margin: 0; font-size: 26px; }
.adm .li { grid-template-columns: 1fr auto; }
.adm .li .acts { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }
.btn.xs { height: 30px; padding: 0 12px; font-size: 13px; } .btn.danger { background: #c0392b; color: #fff; } .btn.ghost.danger { background: transparent; color: #c0392b; border: 1px solid #c0392b; }
.adm .li.off { opacity: .55; }
.ed-bar { display: flex; flex-wrap: wrap; gap: 4px; padding: 8px; border: 1px solid var(--line); border-bottom: 0; border-radius: 12px 12px 0 0; background: var(--bg2); }
.ed-bar button { height: 32px; padding: 0 10px; border: 0; border-radius: 8px; background: transparent; font-size: 13px; font-weight: 600; } .ed-bar button:hover { background: var(--bg); } .ed-bar button.on { background: var(--fg); color: var(--bg); }
.ed-bar .sep { width: 1px; background: var(--line); margin: 4px 4px; }
.ed { min-height: 360px; border: 1px solid var(--line); border-radius: 0 0 12px 12px; padding: 18px 20px; background: var(--bg); font-size: 16px; line-height: 1.75; outline: none; overflow: auto; }
.ed:focus { border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent); }
.ed img { max-width: 100%; height: auto; } .ed table { border-collapse: collapse; width: 100%; } .ed td, .ed th { border: 1px solid var(--line); padding: 6px 10px; }
.ed-src { min-height: 360px; width: 100%; border: 1px solid var(--line); border-radius: 0 0 12px 12px; padding: 16px; font: 13px/1.6 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; background: var(--bg); color: var(--fg); resize: vertical; }
.files-box { display: flex; flex-direction: column; gap: 8px; } .files-box .f { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 14px; border-radius: 12px; background: var(--bg2); font-size: 14px; }
.toast { position: fixed; left: 50%; bottom: 24px; transform: translateX(-50%); z-index: 50; max-width: calc(100% - 32px); padding: 12px 18px; border-radius: 999px; background: var(--fg); color: var(--bg); font-size: 14px; font-weight: 600; box-shadow: 0 8px 30px rgba(0,0,0,.25); opacity: 0; pointer-events: none; transition: opacity .25s; }
.toast[data-show="1"] { opacity: 1; }
.deploy { display: flex; align-items: center; gap: 10px; padding: 10px 16px; border-radius: 12px; background: var(--bg2); font-size: 14px; }
.deploy .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--muted); flex: none; } .deploy[data-state="running"] .dot { background: #f5c35a; animation: blink 1s infinite; } .deploy[data-state="ok"] .dot { background: #2fbf71; } .deploy[data-state="fail"] .dot { background: #c0392b; }
@keyframes blink { 50% { opacity: .3; } }
.modal { position: fixed; inset: 0; z-index: 60; display: none; align-items: center; justify-content: center; padding: 16px; background: rgba(0,0,0,.45); }
.modal[data-open="1"] { display: flex; }
.modal .box { width: min(100%, 560px); max-height: 90vh; overflow: auto; border-radius: 20px; background: var(--bg); padding: 28px; box-shadow: 0 20px 60px rgba(0,0,0,.3); }
.modal .box.wide { width: min(100%, 960px); }
.login { max-width: 560px; margin: 0 auto; }
.kv { display: grid; grid-template-columns: auto 1fr; gap: 6px 16px; font-size: 14px; } .kv dt { color: var(--muted); } .kv dd { margin: 0; }
@media (max-width: 860px) { .adm { grid-template-columns: 1fr; gap: 20px; } .adm-nav { position: static; flex-direction: row; overflow-x: auto; padding-bottom: 4px; } .adm-nav a { white-space: nowrap; } .adm .li { grid-template-columns: 1fr; } .adm .li .acts { justify-content: flex-start; } }
.nav a:hover { text-decoration: none; color: var(--accent); }
.mega { position: absolute; left: 0; right: 0; top: 100%; background: var(--bg); border-bottom: 1px solid var(--line); box-shadow: 0 24px 48px rgba(0,0,0,.10); z-index: 40; }
.mega-inner { display: grid; grid-template-columns: 220px 1fr; gap: 40px; padding: 28px 16px 34px; }
.mega-intro { display: flex; flex-direction: column; gap: 8px; align-self: stretch; padding: 4px 32px 4px 0; border-right: 1px solid var(--line); }
.mega-intro .eyebrow { display: block; text-align: left; font-size: 12px; letter-spacing: .04em; color: var(--accent); margin: 0; } .mega-intro strong { font-size: 20px; line-height: 1.35; letter-spacing: -.01em; } .mega-intro p { margin: 0 0 6px; font-size: 14px; line-height: 1.65; color: var(--muted); } .mega-intro .more { font-size: 14px; }
.mega-cols { display: grid; grid-template-columns: repeat(5, 1fr); gap: 28px; }
.mega-col-title { display: block; font-size: 16px; font-weight: 700; color: var(--fg); padding-bottom: 10px; margin-bottom: 8px; border-bottom: 2px solid var(--fg); }
.mega-col-title:hover { text-decoration: none; color: var(--accent); border-color: var(--accent); }
.mega-col ul { list-style: none; margin: 0; padding: 0; } .mega-col li a { display: block; padding: 6px 0; font-size: 15px; color: var(--muted); line-height: 1.5; } .mega-col li a:hover, .mega-col li a:focus-visible { color: var(--accent); text-decoration: none; font-weight: 600; }
.mega-col.hot .mega-col-title { color: var(--accent); border-color: var(--accent); }
.hdr { position: sticky; }
.mnav .mgrp { padding: 6px 0; border-bottom: 1px solid var(--line); } .mnav .mtop { font-weight: 700; } .mnav .msub { display: flex; flex-wrap: wrap; gap: 0 18px; padding: 0 0 6px 12px; } .mnav .msub a { font-size: 15px; color: var(--muted); padding: 4px 0; }
@media (max-width: 1024px) { .mega-inner { grid-template-columns: 1fr; gap: 20px; } .mega-intro { display: none; } .mega-cols { gap: 20px; } }
@media (max-width: 860px) { .mega { display: none !important; } }
.cover { margin: 0 0 28px; } .cover img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; border-radius: 20px; display: block; background: var(--bg2); }
.li-thumb { display: block; width: 128px; aspect-ratio: 16 / 10; border-radius: 12px; overflow: hidden; background: var(--bg2); flex: 0 0 auto; } .li-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.li.li-ev { grid-template-columns: auto 1fr auto; }
.li-thumb-ph { display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0B5CFF, #4A8BFF); color: #fff; font-size: 12px; font-weight: 700; text-align: center; padding: 6px; }
@media (max-width: 640px) { .li.li-ev { grid-template-columns: 1fr; } .li-thumb { width: 100%; } }
.card-thumb { display: block; margin: -32px -28px 4px; aspect-ratio: 16 / 9; overflow: hidden; border-radius: 20px 20px 0 0; background: var(--bg2); } .card-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.art { margin-top: 32px; font-size: 17px; line-height: 1.85; }
.art > p { margin: 0 0 16px; }
.art-lead { font-size: 19px; line-height: 1.7; color: var(--fg); margin: 0 0 28px !important; }
.art-h { font-size: 22px; font-weight: 700; letter-spacing: -0.01em; margin: 40px 0 14px; padding-left: 14px; border-left: 4px solid var(--accent); line-height: 1.3; }
.art-h:first-child { margin-top: 0; }
.art-kv { display: grid; grid-template-columns: 110px 1fr; gap: 10px 18px; margin: 0 0 24px; padding: 22px 26px; background: var(--bg2); border-radius: 18px; }
.art-kv dt { color: var(--muted); font-size: 15px; font-weight: 600; } .art-kv dd { margin: 0; }
.art-ul { list-style: none; padding: 0; margin: 0 0 24px; display: flex; flex-direction: column; gap: 10px; }
.art-ul li { position: relative; padding-left: 20px; }
.art-ul li::before { content: ""; position: absolute; left: 0; top: .72em; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }
ol.art-ul { counter-reset: n; } ol.art-ul li::before { content: counter(n); counter-increment: n; width: auto; height: auto; top: 0; background: none; color: var(--accent); font-weight: 700; font-size: 15px; }
.art-sum { background: var(--bg2); border-radius: 18px; padding: 22px 26px; margin: 0 0 28px; }
.art-sum .k { display: block; font-size: 13px; font-weight: 600; color: var(--muted); margin-bottom: 10px; }
.art-sum .art-ul { margin: 0; gap: 8px; }
.art-fig { margin: 28px 0; } .art-fig img { max-width: 100%; width: auto; height: auto; border-radius: 18px; display: block; margin: 0 auto; }
.art-fig figcaption { margin-top: 10px; font-size: 14px; color: var(--muted); text-align: center; }
.art-tbl { margin: 0 0 24px; }
@media (max-width: 640px) { .art-kv { grid-template-columns: 1fr; gap: 4px 0; } .art-kv dt { margin-top: 8px; } .art-kv dt:first-child { margin-top: 0; } .art { font-size: 16px; } .art-lead { font-size: 17px; } }
.post { margin-top: 28px; font-size: 17px; line-height: 1.85; } .post p { margin: 0 0 14px; } .post ul, .post ol { margin: 0 0 14px; padding-left: 22px; } .post li { margin: 4px 0; } .post h3 { margin: 24px 0 8px; } .post img { max-width: 100%; border-radius: 16px; margin: 8px 0; } .post table { border-collapse: collapse; width: 100%; } .post td, .post th { border-bottom: 1px solid var(--line); padding: 8px 10px; text-align: left; }
.kv { display: grid; grid-template-columns: 96px 1fr; gap: 10px 16px; margin: 0; } .kv dt { color: var(--muted); font-size: 15px; } .kv dd { margin: 0; }
[data-ev-empty][hidden] { display: none; }
.chipgrp { display: flex; flex-direction: column; gap: 8px; padding-top: 10px; border-top: 1px solid var(--line); }
.chipgrp:first-child { border-top: 0; padding-top: 0; }
.chipgrp .gk { font-size: 13px; font-weight: 600; color: var(--muted); }
.chip { display: inline-flex; align-items: center; height: 36px; padding: 0 14px; border-radius: 999px; background: var(--bg2); font-size: 14px; color: var(--fg); }
.sec.alt .chip { background: var(--bg); }
.chip.sel { display: inline-flex; gap: 8px; cursor: pointer; }
.chip.sel input { width: 16px; height: 16px; }
.done { background: var(--ok-bg); color: var(--ok); border-radius: 16px; padding: 20px; font-size: 15px; display: none; }
.done[data-show="1"] { display: block; }
.done code { font-weight: 700; }
/* footer */
.ftr { background: #1d1d1f; color: #d2d2d7; padding-block: 48px 40px; font-size: 14px; }
:root[data-theme="dark"] .ftr, .ftr { color: #d2d2d7; }
.ftr .wrap { display: flex; flex-direction: column; gap: 28px; }
.ftr .cols { display: grid; grid-template-columns: 1.6fr 1fr 1fr; gap: 32px; }
@media (max-width: 760px) { .ftr .cols { grid-template-columns: 1fr; } }
.ftr .col { display: flex; flex-direction: column; gap: 8px; }
.ftr strong { color: #ffffff; font-size: 15px; }
.ftr a { color: #d2d2d7; }
.ftr .copy { display: inline-flex; align-items: center; gap: 8px; }
.ftr .copy button { height: 28px; padding: 0 10px; border-radius: 999px; border: 1px solid #424245; background: transparent; color: #d2d2d7; font-size: 12px; }
.ftr .bot { display: flex; justify-content: space-between; gap: 16px; flex-wrap: wrap; border-top: 1px solid #424245; padding-top: 20px; color: #a1a1a6; font-size: 13px; }
.empty { background: var(--bg2); border-radius: 20px; padding: 40px 24px; text-align: center; color: var(--muted); }
.sec.alt .empty { background: var(--bg); }
.gallery { display: flex; gap: 12px; overflow-x: auto; padding-bottom: 6px; }
.gallery img { height: 260px; width: auto; max-width: none; border-radius: 16px; }
.kv { display: grid; grid-template-columns: 140px 1fr; gap: 10px 20px; font-size: 15px; }
.kv dt { color: var(--muted); }
.kv dd { margin: 0; }
@media (max-width: 520px) { .kv { grid-template-columns: 1fr; } }
.stages { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; }
.stage { border-radius: 14px; background: var(--bg2); padding: 12px 10px 14px; font-size: 14px; font-weight: 600; text-align: center; color: var(--muted); display: flex; flex-direction: column; gap: 4px; align-items: center; opacity: .55; }
.stage .no { font-size: 12px; font-weight: 700; letter-spacing: .04em; }
.stage.on { opacity: 1; }
.stage.s1.on { background: var(--s1-bg); color: var(--s1); } .stage.s2.on { background: var(--s2-bg); color: var(--s2); } .stage.s3.on { background: var(--s3-bg); color: var(--s3); }
.stage.s4.on { background: var(--s4-bg); color: var(--s4); } .stage.s5.on { background: var(--s5-bg); color: var(--s5); } .stage.s6.on { background: var(--s6-bg); color: var(--s6); }
.stbar { display: grid; grid-template-columns: repeat(6, 1fr); gap: 3px; margin-top: 10px; }
.stbar span { height: 5px; border-radius: 3px; background: var(--line); opacity: .5; }
.stbar span.on { opacity: 1; } .stbar .s1.on { background: var(--s1); } .stbar .s2.on { background: var(--s2); } .stbar .s3.on { background: var(--s3); } .stbar .s4.on { background: var(--s4); } .stbar .s5.on { background: var(--s5); } .stbar .s6.on { background: var(--s6); }
.flow { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; }
.flow-step { display: flex; flex-direction: column; gap: 12px; min-width: 0; }
.fs-head { position: relative; height: 72px; padding: 12px 22px 12px 18px; display: flex; flex-direction: column; justify-content: center; gap: 2px; clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 50%, calc(100% - 14px) 100%, 0 100%, 12px 50%); }
.flow-step:first-child .fs-head { clip-path: polygon(0 0, calc(100% - 14px) 0, 100% 50%, calc(100% - 14px) 100%, 0 100%); border-radius: 14px 0 0 14px; }
.fs-head .no { font-size: 12px; font-weight: 700; letter-spacing: .06em; opacity: .8; } .fs-head .lb { font-size: 16px; font-weight: 700; line-height: 1.25; }
.flow-step.s1 .fs-head { background: var(--s1-bg); color: var(--s1); } .flow-step.s2 .fs-head { background: var(--s2-bg); color: var(--s2); } .flow-step.s3 .fs-head { background: var(--s3-bg); color: var(--s3); }
.flow-step.s4 .fs-head { background: var(--s4-bg); color: var(--s4); } .flow-step.s5 .fs-head { background: var(--s5-bg); color: var(--s5); } .flow-step.s6 .fs-head { background: var(--s6-bg); color: var(--s6); }
.fs-list { display: flex; flex-direction: column; gap: 6px; padding: 0 4px; }
.fs-list .chip { height: auto; min-height: 34px; padding: 6px 12px; font-size: 14px; justify-content: flex-start; background: var(--bg); }
.fs-list .chip.src-manual { font-weight: 700; color: var(--fg); }
.flow-step.s1 .chip.src-manual { color: var(--s1); } .flow-step.s2 .chip.src-manual { color: var(--s2); } .flow-step.s3 .chip.src-manual { color: var(--s3); } .flow-step.s4 .chip.src-manual { color: var(--s4); } .flow-step.s5 .chip.src-manual { color: var(--s5); } .flow-step.s6 .chip.src-manual { color: var(--s6); }
.fs-list .chip.muted { color: var(--muted); font-weight: 400; }
@media (max-width: 1000px) { .flow { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (max-width: 640px) { .flow { grid-template-columns: repeat(2, minmax(0, 1fr)); } .fs-head { height: 64px; padding-left: 14px; } .fs-head .lb { font-size: 15px; } }
@media (max-width: 760px) { .stages { grid-template-columns: repeat(3, minmax(0, 1fr)); } .stage { padding: 12px 6px; font-size: 13px; } }
@media (max-width: 400px) { .stages { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.cta { display: flex; flex-direction: column; align-items: center; text-align: center; gap: 16px; }
.cta .acts { display: flex; gap: 12px 24px; flex-wrap: wrap; justify-content: center; align-items: center; }
.vs { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20px; }
@media (max-width: 640px) { .vs { grid-template-columns: 1fr; } }
.note { font-size: 13px; color: var(--muted); }
br.d { display: none; }
@media (min-width: 761px) { br.d { display: inline; } }
"""

JS = r"""
(function(){
  var qs=function(s,r){return (r||document).querySelector(s)}, qsa=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
  // mobile nav
  var b=qs('.burger'), m=qs('.mnav');
  if(b&&m){ b.addEventListener('click',function(){ var o=m.getAttribute('data-open')==='1'; m.setAttribute('data-open',o?'0':'1'); b.setAttribute('aria-expanded',String(!o)); }); }
  // generic tab filters: [data-tabs] buttons filter [data-items] children by data-key
  qsa('[data-tabs]').forEach(function(bar){
    var target=qs('[data-items="'+bar.getAttribute('data-tabs')+'"]'); if(!target) return;
    var count=qs('[data-count="'+bar.getAttribute('data-tabs')+'"]');
    function apply(key){
      var n=0; qsa('[data-key]',target).forEach(function(el){ var on=(key==='all'||el.getAttribute('data-key')===key); el.hidden=!on; if(on)n++; });
      qsa('.tab',bar).forEach(function(t){ t.setAttribute('aria-pressed',String(t.getAttribute('data-val')===key)); });
      if(count) count.textContent=n+'개';
      try{ localStorage.setItem('tab:'+bar.getAttribute('data-tabs'),key);}catch(e){}
    }
    qsa('.tab',bar).forEach(function(t){ t.addEventListener('click',function(){ apply(t.getAttribute('data-val')); }); });
    var init='all'; try{ init=localStorage.getItem('tab:'+bar.getAttribute('data-tabs'))||'all'; }catch(e){}
    var h=location.hash.replace('#',''); if(h && qs('.tab[data-val="'+h+'"]',bar)) init=h;
    apply(init);
  });
  // forms (demo: validate, show receipt)
  function validate(f){ var ok=true; qsa('.field',f).forEach(function(fd){ var inp=qs('input,select,textarea',fd); if(!inp) return; var bad=false; if(inp.required && !inp.value.trim()) bad=true; if(inp.type==='email' && inp.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(inp.value)) bad=true; fd.classList.toggle('err',bad); if(bad) ok=false; }); var ag=qs('input[type=checkbox][required]',f); if(ag&&!ag.checked){ ok=false; ag.focus(); } return ok; }
  qsa('form[data-demo]').forEach(function(f){
    f.addEventListener('submit',function(e){ e.preventDefault(); if(!validate(f)) return; var d=qs('.done',f); var id=f.getAttribute('data-demo').toUpperCase()+'-'+new Date().toISOString().slice(0,10).replace(/-/g,'')+'-'+String(Math.floor(Math.random()*900)+100); if(d){ var c=qs('code',d); if(c) c.textContent=id; d.setAttribute('data-show','1'); d.scrollIntoView({block:'nearest'}); } var sub=qs('button[type=submit]',f); if(sub){ sub.disabled=true; sub.textContent='접수되었습니다'; } });
  });
  // prefill service from ?service= or #svc=
  var p=new URLSearchParams(location.search); var svc=p.get('service');
  if(svc){ qsa('input[name="services"]').forEach(function(c){ if(c.value===svc) c.checked=true; }); var sel=qs('#f-type'); }
  // copy buttons
  qsa('[data-copy]').forEach(function(btn){ btn.addEventListener('click',function(){ var t=btn.getAttribute('data-copy'); function ok(){ btn.textContent='복사됨'; setTimeout(function(){btn.textContent='복사';},1500);} if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(t).then(ok,function(){ fallback(); }); } else fallback(); function fallback(){ var s=document.createElement('textarea'); s.value=t; document.body.appendChild(s); s.select(); try{document.execCommand('copy'); ok();}catch(e){} document.body.removeChild(s);} }); });
  // stats: admin-entered numbers (assets/stats.json) + live course count (assets/stats.live.json) + count-up
  (function(){
    if(!qsa('[data-stat]').length) return;
    function fmt(n){ return Number(n).toLocaleString('ko-KR'); }
    function setStat(k,v){ qsa('[data-stat="'+k+'"]').forEach(function(e){ if(e.hasAttribute('data-count')) e.setAttribute('data-count',String(v)); else e.textContent=(typeof v==='number')?fmt(v):String(v); }); }
    function countUp(){
      var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      qsa('[data-count]').forEach(function(el){
        var to=parseInt(el.getAttribute('data-count'),10)||0;
        if(reduce||!('IntersectionObserver' in window)){ el.textContent=fmt(to); return; }
        el.textContent='0';
        var io=new IntersectionObserver(function(en){ if(!en[0].isIntersecting) return; io.disconnect();
          var t0=null, dur=1400;
          function step(ts){ if(!t0) t0=ts; var p=Math.min(1,(ts-t0)/dur), e=1-Math.pow(1-p,3); el.textContent=fmt(Math.round(to*e)); if(p<1) requestAnimationFrame(step); }
          requestAnimationFrame(step); },{threshold:0.35});
        io.observe(el);
      });
    }
    function load(u){ return fetch(u,{cache:'no-store'}).then(function(r){ if(!r.ok) throw new Error(u); return r.json(); }); }
    var manual=null;
    if(location.protocol==='file:'){ countUp(); return; }   // zip을 로컬에서 열었을 때는 내장값으로
    load('assets/stats.json').then(function(s){ manual=s;
      if(s.services!=null) setStat('services',s.services);
      if(s.universities!=null) setStat('universities',s.universities);
      if(s.companies!=null) setStat('companies',s.companies);
      if(s.universities!=null&&s.companies!=null) setStat('partners',Number(s.universities)+Number(s.companies));
      if(s.courses!=null&&s.courses!==''){ setStat('courses',s.courses); setStat('courses_note','사무국 입력값'); }
    }).catch(function(){}).then(function(){ return load('assets/stats.live.json'); }).then(function(l){
      if(l&&l.courses){ setStat('courses_live',l.courses); setStat('courses_date',l.fetched_at||''); if(!(manual&&manual.courses!=null&&manual.courses!=='')){ setStat('courses',l.courses); setStat('courses_note','한림 AI 교육 포털 '+(l.fetched_at||'')+' 기준'); } }
    }).catch(function(){}).then(countUp);
  })();
  // 관리자가 숨긴 자동 연동 글(content/hidden.json → window.KELI_HIDDEN)은 다시 그릴 때도 뺀다
  function hid(kind, items){ var h=((window.KELI_HIDDEN||{})[kind])||[]; return items.filter(function(it){ return h.indexOf(String(it.id))<0; }); }
  // events feed: AI교육확산센터 [KELI] 글 (assets/events.live.json) → [data-events] 다시 그리기
  (function(){
    var boxes=qsa('[data-events]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function status(it){ var now=new Date(Date.now()+9*3600e3).toISOString().slice(0,16); if(it.start&&now<it.start) return ['upcoming','예정']; if(it.end&&now<=it.end) return ['live','진행 중']; return ['ended','종료']; }
    function href(it,pages){ return pages.indexOf(String(it.id))>-1 ? 'event-'+it.id+'.html' : it.url; }
    function ext(it,pages){ return pages.indexOf(String(it.id))>-1 ? '' : ' target="_blank" rel="noopener"'; }
    function badge(it){ var s=status(it); return '<span class="badge '+(s[0]==='upcoming'?'live':'')+'">'+s[1]+'</span>'; }
    function d(it){ return (it.start||'').slice(0,10).replace(/-/g,'.'); }
    function th(it,c){ return it.thumb?'<span class="'+c+'"><img src="'+esc(it.thumb)+'" alt="" loading="lazy"></span>':''; }
    function card(it,p){ return '<a class="card card-ev" href="'+href(it,p)+'"'+ext(it,p)+'>'+th(it,'card-thumb')+'<div class="row"><span class="k">'+esc((it.badges||['행사'])[0])+'</span>'+badge(it)+'</div><h3>'+esc(it.title)+'</h3><p>'+esc(it.when)+'<br>'+esc(it.place)+'</p><span class="more">자세히 보기</span></a>'; }
    function row(it,p){ return '<a class="li li-ev" href="'+href(it,p)+'"'+ext(it,p)+'>'+th(it,'li-thumb')+'<span><span class="m">'+esc((it.badges||['행사'])[0])+' · '+esc(it.place)+'</span><br><span class="t">'+esc(it.title)+'</span><br><span class="m">'+esc(it.when)+'</span></span><span class="d">'+d(it)+' '+badge(it)+'</span></a>'; }
    function short(it,p){ return '<a class="li" href="'+href(it,p)+'"'+ext(it,p)+'><span><span class="m">'+esc((it.badges||['행사'])[0])+'</span><br><span class="t">'+esc(it.title)+'</span></span><span class="d">'+d(it)+'</span></a>'; }
    fetch('assets/events.live.json',{cache:'no-store'}).then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(f){
      var items=hid('events', f.items||[]); if(!items.length) return;
      boxes.forEach(function(b){ var p=(b.getAttribute('data-pages')||'').split(','); var kind=b.getAttribute('data-events');
        if(kind==='home') b.innerHTML=card(items[0],p);
        else if(kind==='rows') b.innerHTML=items.slice(0,3).map(function(it){ return short(it,p); }).join('');
        else if(kind==='list') b.innerHTML=items.map(function(it){ return row(it,p); }).join('');
      });
      var up=items.some(function(it){ return status(it)[0]!=='ended'; }); var em=qs('[data-ev-empty]'); if(em) em.hidden=up;
      var fd=qs('[data-feed-date]'); if(fd&&f.fetched_at) fd.textContent=f.fetched_at;
      qsa('[data-ev-status]').forEach(function(el){ var id=(el.closest('[data-ev]')||{}).getAttribute? el.closest('[data-ev]').getAttribute('data-ev'):null; var it=items.filter(function(x){ return String(x.id)===id; })[0]; if(it){ var s=status(it); el.textContent=s[1]; el.className='badge '+(s[0]==='upcoming'?'live':''); } });
    }).catch(function(){});
  })();
  // press feed: 한림대 보도자료(press.live.json) + 한국대학신문 기사(unn.live.json) 병합 → [data-press] 다시 그리기
  (function(){
    var boxes=qsa('[data-press]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function href(it,p){ return it.src==='unn' ? it.url : (p.indexOf(String(it.id))>-1 ? 'press-'+it.id+'.html' : it.url); }
    function ext(it,p){ return (it.src==='unn' || p.indexOf(String(it.id))<0) ? ' target="_blank" rel="noopener"' : ''; }
    function th(it){ return it.thumb ? '<span class="li-thumb"><img src="'+esc(it.thumb)+'" alt="" loading="lazy"></span>' : '<span class="li-thumb li-thumb-ph"><span>'+(it.src==='unn'?'한국대학신문':'한림대학교')+'</span></span>'; }
    function meta(it){ return it.src==='unn' ? '언론 보도 · 한국대학신문'+(it.reporter?' · '+esc(it.reporter):'') : '보도자료 · 한림대학교'+(it.category?' · '+esc(it.category):''); }
    function row(it,p,sum){ return '<a class="li li-ev" href="'+href(it,p)+'"'+ext(it,p)+'>'+th(it)+'<span><span class="m">'+meta(it)+'</span><br><span class="t">'+esc(it.title)+'</span>'+(sum&&it.summary?'<br><span class="m">'+esc(it.summary.slice(0,90))+'</span>':'')+'</span><span class="d">'+esc(it.date||'')+'</span></a>'; }
    function load(u){ return fetch(u,{cache:'no-store'}).then(function(r){ return r.ok ? r.json() : {items:[]}; }).catch(function(){ return {items:[]}; }); }
    Promise.all([load('assets/press.live.json'), load('assets/unn.live.json')]).then(function(fs){
      var a=hid('press', fs[0].items||[]), b=hid('unn', (fs[1].items||[]).map(function(x){ x.src='unn'; return x; }));
      var items=a.concat(b).sort(function(x,y){ return (y.date||'').localeCompare(x.date||''); }); if(!items.length) return;
      boxes.forEach(function(bx){ var p=(bx.getAttribute('data-pages')||'').split(','); var kind=bx.getAttribute('data-press');
        if(kind==='rows') bx.innerHTML=items.slice(0,3).map(function(it){ return row(it,p,false); }).join('');
        else if(kind==='list') bx.innerHTML=items.map(function(it){ return row(it,p,true); }).join('');
      });
      var fd=qs('[data-press-date]'); if(fd&&fs[0].fetched_at) fd.textContent=fs[0].fetched_at;
    });
  })();
  // videos: 클릭하면 그 자리에서 YouTube 재생 (처음엔 썸네일만 → 데이터 절약)
  function wirePlay(root){ qsa('.vid-play', root||document).forEach(function(b){ if(b._wired) return; b._wired=true; b.addEventListener('click',function(){ var v=b.closest('.vid'); var f=document.createElement('iframe'); f.src=v.getAttribute('data-embed'); f.title=b.getAttribute('aria-label')||'영상'; f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share'; f.setAttribute('allowfullscreen',''); b.replaceWith(f); }); }); }
  wirePlay();
  (function(){
    var boxes=qsa('[data-videos]'); if(!boxes.length||location.protocol==='file:') return;
    function esc(s){ return String(s||'').replace(/[&<>"]/g,function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
    function card(v){ var meta=[(v.group==='keli'?'KELI 영상':'HAI · 소프트랩'), v.published||v.published_text||'', v.views||''].filter(Boolean).join(' · ');
      return '<div class="vid" data-vid="'+esc(v.id)+'" data-embed="'+esc(v.embed)+'"><button type="button" class="vid-play" aria-label="'+esc(v.title)+' 재생"><img src="'+esc(v.thumb)+'" alt="" loading="lazy"><span class="play"></span>'+(v.length?'<span class="len">'+esc(v.length)+'</span>':'')+'</button><div class="vid-body"><span class="m">'+esc(meta)+'</span>'+(v.is_live_recording?'<span class="badge" style="margin-left:6px">실시간 녹화</span>':'')+'<strong class="t">'+esc(v.title)+'</strong><a class="more" href="'+esc(v.url)+'" target="_blank" rel="noopener">YouTube에서 보기</a></div></div>'; }
    fetch('assets/videos.live.json',{cache:'no-store'}).then(function(r){ if(!r.ok) throw 0; return r.json(); }).then(function(f){
      var items=hid('videos', f.items||[]); if(!items.length) return; var keli=items.filter(function(v){ return v.group==='keli'; }), rel=items.filter(function(v){ return v.group!=='keli'; });
      boxes.forEach(function(b){ var k=b.getAttribute('data-videos');
        if(k==='hub') b.innerHTML=keli.concat(rel).slice(0,2).map(card).join('');
        else if(k==='keli') b.innerHTML=keli.map(card).join('')||'<div class="empty">아직 KELI 영상이 없습니다.</div>';
        else if(k==='related') b.innerHTML=rel.map(card).join('');
      });
      var fd=qs('[data-video-date]'); if(fd&&f.fetched_at) fd.textContent=f.fetched_at;
      wirePlay();
    }).catch(function(){});
  })();
  // mega menu: 상단 메뉴에 올리거나(마우스) 누르면(터치) 전체 메뉴 펼침
  (function(){
    var mega=qs('#mega'), hdr=qs('.hdr'); if(!mega||!hdr) return;
    var navLinks=qsa('.nav a[data-menu]'), timer=null, coarse=window.matchMedia&&window.matchMedia('(pointer: coarse)').matches;
    function open(key){ clearTimeout(timer); mega.hidden=false; qsa('.mega-col',mega).forEach(function(c){ c.classList.toggle('hot', c.getAttribute('data-menu')===key); }); navLinks.forEach(function(a){ a.setAttribute('aria-expanded', a.getAttribute('data-menu')===key?'true':'false'); }); }
    function close(){ clearTimeout(timer); timer=setTimeout(function(){ mega.hidden=true; navLinks.forEach(function(a){ a.setAttribute('aria-expanded','false'); }); },160); }
    navLinks.forEach(function(a){
      a.setAttribute('aria-haspopup','true'); a.setAttribute('aria-expanded','false');
      a.addEventListener('mouseenter',function(){ open(a.getAttribute('data-menu')); });
      a.addEventListener('focus',function(){ open(a.getAttribute('data-menu')); });
      a.addEventListener('click',function(e){ if(window.innerWidth<=860) return; var k=a.getAttribute('data-menu'); var hot=qs('.mega-col.hot',mega); if(mega.hidden||!hot||hot.getAttribute('data-menu')!==k){ e.preventDefault(); open(k); } });
    });
    qs('.nav').addEventListener('mouseenter', function(){ var cur=qs('.nav a.on')||navLinks[0]; if(mega.hidden) open(cur?cur.getAttribute('data-menu'):null); });
    qs('.nav').addEventListener('mouseleave', close); mega.addEventListener('mouseenter', function(){ clearTimeout(timer); }); mega.addEventListener('mouseleave', close);
    hdr.addEventListener('focusout', function(e){ if(!hdr.contains(e.relatedTarget)) close(); });
    document.addEventListener('keydown', function(e){ if(e.key==='Escape'){ mega.hidden=true; } });
    document.addEventListener('click', function(e){ if(!hdr.contains(e.target)) mega.hidden=true; });
  })();
  // search
  var si=qs('#q'); if(si){ var rows=qsa('#results [data-q]'), rc=qs('#rc'); function run(){ var v=si.value.trim().toLowerCase(), n=0; rows.forEach(function(r){ var on=!v||r.getAttribute('data-q').indexOf(v)>-1; r.hidden=!on; if(on)n++; }); if(rc) rc.textContent=n+'건'; } si.addEventListener('input',run); var q0=p.get('q'); if(q0){ si.value=q0; } run(); }
})();
"""

# ------------------------------------------------------------------ 공통 조각
NAV = [('about.html', 'KELI 소개'), ('services.html', '마켓플레이스'), ('join.html', '참여·도입'), ('archive.html', '아카이브'), ('news.html', '소식')]
NEWS_PAGES = {'news.html', 'notice.html', 'events.html', 'newsletter.html', 'videos.html'}
# 상단 메뉴를 누르거나 올리면 펼쳐지는 전체 메뉴(메가 메뉴). 각 메뉴 아래 게시판·섹션 바로가기
MEGA = [
    ('about.html', 'KELI 소개', [('about.html#offer', '무엇을 제공하나'), ('about.html#why', '왜 KELI인가'), ('about.html#vision', '비전'), ('about.html#structure', '구조 · 참여 기관'), ('about.html#office', '사무국 · 연락처'), ('en.html', 'English')]),
    ('services.html', '마켓플레이스', [('services.html', 'HAI Ecosystems 19'), ('services.html#platform', '통합 플랫폼'), ('services.html#career', '진로 · 연구'), ('services.html#courseware', '전공 코스웨어'), ('services.html#teaching', '학습 · 수업 지원'), ('services.html#analytics', '분석 · 데이터'), ('services.html#admin', '행정 · 평가'), ('demos.html', '전체 데모 영상'), ('curriculum.html', '수업 6단계와 서비스')]),
    ('join.html', '참여 · 도입', [('join.html', '참여 방법 · 절차'), ('join.html#members', '참여 기관'), ('join.html#inquiry', '도입 문의'), ('newsletter.html', '뉴스레터 구독')]),
    ('archive.html', '아카이브', [('archive-case.html', '실증 사례집'), ('archive-trend.html', '기술 동향 · 연구'), ('archive-manual.html', '매뉴얼 · 소개자료')]),
    ('news.html', '소식', [('notice.html', '공지사항'), ('events.html', '행사'), ('videos.html', '영상'), ('newsletter.html', '뉴스레터 · 보도자료'), ('search.html', '검색')]),
]

def header(current):
    def on(h):
        if h == 'news.html' and current in NEWS_PAGES: return ' class="on"'
        if h == 'services.html' and (current.startswith('service') or current == 'curriculum.html'): return ' class="on"'
        return ' class="on"' if h == current else ''
    links = ''.join(f'<a href="{h}"{on(h)} data-menu="{h}">{t}</a>' for h, t in NAV)
    mlinks = ''.join(f'<div class="mgrp"><a class="mtop" href="{h}">{t}</a><div class="msub">' + ''.join(f'<a href="{sh}">{st}</a>' for sh, st in subs) + '</div></div>' for h, t, subs in MEGA) + '<div class="mgrp"><div class="msub"><a href="search.html">검색</a><a href="en.html">English</a><a href="join.html#inquiry">도입 문의</a></div></div>'
    cols = ''.join(f'<div class="mega-col" data-menu="{h}"><a class="mega-col-title" href="{h}">{t}</a><ul>' + ''.join(f'<li><a href="{sh}">{st}</a></li>' for sh, st in subs) + '</ul></div>' for h, t, subs in MEGA)
    mega = f'''<div class="mega" id="mega" hidden><div class="wrap mega-inner">
<div class="mega-intro"><span class="eyebrow">K-University AI EduTech &amp; Learning Initiative</span><strong>고등교육 AI 공유 플랫폼</strong><p>한림대학교가 수업에서 검증한 AI 교육 서비스를 대학·기관과 함께 씁니다.</p><a class="more" href="join.html#inquiry">도입 문의</a><a class="more" href="demos.html">전체 데모 영상</a></div>
<div class="mega-cols">{cols}</div>
</div></div>'''
    return f'''<header class="hdr"><div class="wrap bar">
<a class="brand" href="index.html" aria-label="KELI 홈"><img src="assets/img/keli-logo.png" alt="KELI" width="62" height="28"></a>
<nav class="nav" aria-label="주요 메뉴">{links}</nav>
<div class="util">
<a class="ico txt" href="search.html" aria-label="검색"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg></a>
<a class="txt" href="en.html">ENG</a>
<a class="btn sm" href="join.html#inquiry">도입 문의</a>
<button class="burger" aria-label="메뉴 열기" aria-expanded="false"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
</div></div>
<nav class="mnav wrap" data-open="0" aria-label="모바일 메뉴">{mlinks}</nav>
{mega}
</header>'''

FOOTER = f'''<footer class="ftr"><div class="wrap">
<div class="cols">
<div class="col"><strong>KELI 사무국</strong><span>한림대학교 AI교육혁신원 AI교육확산센터</span>
<span class="copy">{EMAIL} <button type="button" data-copy="{EMAIL}">복사</button></span>
<span>(24252) 강원특별자치도 춘천시 한림대학길 1</span>
<a href="{INSTA}" target="_blank" rel="noopener">Instagram @hallym_keli</a></div>
<div class="col"><strong>바로가기</strong><a href="services.html">마켓플레이스</a><a href="join.html#inquiry">도입 문의</a><a href="archive.html">아카이브</a><a href="newsletter.html">뉴스레터 구독</a></div>
<div class="col"><strong>관련 사이트</strong><a href="https://www.hallym.ac.kr" target="_blank" rel="noopener">한림대학교</a><a href="https://aiadvcenter.csedu4all.com" target="_blank" rel="noopener">AI교육확산센터</a><a href="https://ai.hallym.ac.kr" target="_blank" rel="noopener">한림 AI 교육 포털</a><a href="{MANUAL_SITE}" target="_blank" rel="noopener">HAI 활용 매뉴얼</a></div>
</div>
<div class="bot"><span>주관 한림대학교 · 후원 교육부 글로컬대학30 · © Hallym University</span><span><a href="privacy.html">개인정보처리방침</a> · <a href="terms.html">이용약관</a> · <a href="en.html">English</a> · <a href="admin.html">관리자</a></span></div>
</div></footer>'''

def doc(fname, title, body, desc='KELI는 한림대학교가 개발하고 수업에서 검증한 AI 교육 서비스를 국내외 대학·기관에 제공하고 함께 확산하는 고등교육 AI 공유 플랫폼입니다.', skeleton=True):
    head_bits = f'''<title>{E(title)}</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="color-scheme" content="light">
<meta name="description" content="{E(desc)}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="assets/site.css">'''
    inner = f'''{head_bits}
{header(fname)}
<main id="main">
{body}
</main>
{FOOTER}
<script>window.KELI_HIDDEN={json.dumps({k: [str(x) for x in HIDDEN.get(k, [])] for k in ('events', 'press', 'videos', 'unn')}, ensure_ascii=False)};</script>
<script src="assets/site.js"></script>{'<script src="assets/admin.js"></script>' if fname == 'admin.html' else ''}'''
    if fname == 'admin.html':
        head_bits = head_bits.replace('<meta name="description"', '<meta name="robots" content="noindex, nofollow">\n<meta name="description"', 1)
    if not skeleton:
        return inner
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{inner}
</body>
</html>
'''.replace('<link rel="stylesheet" href="assets/site.css">', '<link rel="stylesheet" href="assets/site.css">\n</head>\n<body>', 1)

# ------------------------------------------------------------------ 줄바꿈 정리
# 규칙: (1) 문장은 마침표(.!?) 뒤에서 줄을 바꾼다 → <br>
#       (2) 단어·어절·조사 중간에서는 절대 끊지 않는다 → 단어결합자(U+2060)
#           - 가운뎃점(대학·기관), 하이픈(HAI-AI, K-University)
#           - 영문·숫자·닫는괄호·따옴표 뒤에 바로 붙는 조사((화)에, "기업"으로, KELI는)
#           - 날짜 표기(2026. 10. 20.)는 줄바꿈 없는 공백으로 묶는다
#       (3) 1개 교과목 × 1개 서비스 × 1개 학기 같은 수량 표현은 숫자와 단위명사를 묶는다
WJ = '⁠'
_SKIP = re.compile(r'(<title>.*?</title>|<script\b.*?</script>|<style\b.*?</style>|<textarea\b.*?</textarea>|<select\b.*?</select>)', re.S)
_TXT = re.compile(r'>([^<]+)<')
_ABBR = {'dr', 'mr', 'mrs', 'ms', 'prof', 'e.g', 'i.e', 'vs', 'etc', 'no', 'inc', 'ltd', 'co', 'univ', 'st', 'jr', 'sr', 'fig', 'vol', 'pp', 'cf', 'al'}
_SENT = re.compile(r'(?<=[가-힣A-Za-z\)\]」』”’"\'])([.!?])\s+(?=\S)')
_SENT_TAG = re.compile(r'(?<=[가-힣\)\]」』”’"\'])([.!?])\s+(?=<(?:a|span|strong|em|b|i)\b)')

_EN_FN = re.compile(r'\b(a|an|the|of|to|in|for|and|or|but|with|by|on|at|as|from|into|is|are|be|per|via|its|our|their)\s+(?=[A-Za-z0-9(\["])', re.I)

_ENT = {'&middot;': '\u00b7', '&hellip;': '\u2026', '&lsquo;': '\u2018', '&rsquo;': '\u2019', '&ldquo;': '\u201c', '&rdquo;': '\u201d', '&nbsp;': '\u00a0', '&#39;': "'"}
def _join_words(t, en=False):
    for k, v in _ENT.items():                                                        # 외부 글의 엔티티를 실제 글자로
        t = t.replace(k, v)
    t = re.sub(r'(?<=\d\.) (?=\d)', ' ', t)                                    # 2026. 10. 20.
    t = re.sub(r'(?<=\d개) (?=(?:교과목|서비스|학기))', ' ', t)                   # 1개 교과목 × 1개 학기
    if en:  # 영문: 관사·전치사·접속사 뒤에서 줄이 끊기지 않게(줄은 접속사 '앞'에서 바뀜) + 숫자와 단위 결합
        t = _EN_FN.sub(lambda m: m.group(1) + '\u00a0', t)
        t = re.sub(r'(?<=\d) (?=(?:universities|companies|services|courses|semester|course|service)\b)', '\u00a0', t)
        t = re.sub(r'\(([A-Za-z-]+) ([A-Za-z-]+)\)', lambda m: '(' + m.group(1) + '\u00a0' + m.group(2) + ')', t)   # (HAI Ecosystems)
    t = t.replace('·', WJ + '·' + WJ)                                   # 대학·기관
    t = re.sub(r'(?<=[A-Za-z0-9가-힣])-(?=[A-Za-z0-9가-힣])', WJ + '-' + WJ, t)         # HAI-AI, K-에듀테크
    t = t.replace('\u2026', WJ + '\u2026' + WJ)                                          # 출범…AI
    t = re.sub(r'(?<=[▲■●◆▶※])\s*', WJ, t)                                               # ▲항목              # HAI-AI, K-University
    t = re.sub(r'(?<=\S)([–—~])(?=\S)', lambda m: WJ + m.group(1) + WJ, t)           # 한림대학교–춘천교육대학교, 09:30~17:00
    t = re.sub(r'(?<=[A-Za-z0-9\)\]」』”’"\'%])(?=[가-힣])', WJ, t)                 # (화)에, "기업"으로, KELI는
    t = re.sub(r'(?<=[가-힣A-Za-z0-9])(?=[\(\[「『])', WJ, t)                       # 도입(유상·협의)
    return t

def _break_sentences(t):
    def rep(m):
        tok = re.search(r'([A-Za-z.]+)$', t[:m.start()])
        if tok:
            w = tok.group(1).lower().rstrip('.')
            if w in _ABBR or len(w) == 1:
                return m.group(0)
        return m.group(1) + '<br>'
    return _SENT.sub(rep, t)

def nb(html_, en=False):
    out = []
    for i, seg in enumerate(_SKIP.split(html_)):
        if i % 2 == 1:   # title/script/style/textarea/select: <br> 없이 결합자만
            if seg.startswith(('<title', '<select')):
                seg = _TXT.sub(lambda m: '>' + _join_words(m.group(1), en) + '<', seg)
            out.append(seg)
            continue
        seg = _TXT.sub(lambda m: '>' + _break_sentences(_join_words(m.group(1), en)) + '<', seg)
        seg = _SENT_TAG.sub(lambda m: m.group(1) + '<br>', seg)
        out.append(seg)
    return ''.join(out)

def write(fname, title, body, desc=None):
    kw = {'desc': desc} if desc else {}
    open(os.path.join(OUT, fname), 'w', encoding='utf-8').write(nb(doc(fname, title, body, **kw)))

def status_badge(s):
    if not s['status']: return ''
    t, c = STATUS[s['status']]
    return f'<span class="badge {c}">{t}</span>'

def svc_card(s):
    if s['img']:
        logo = ' logo' if s['img'].endswith('.png') else ''
        thumb = f'<div class="thumb{logo}"><img src="assets/img/services/{s["img"]}" alt="{E(s["name"])} 화면" loading="lazy"></div>'
    else:
        thumb = f'<div class="thumb"><span class="word">{E(s["name"])}</span></div>'
    return f'''<a class="svc" href="service-{s['slug']}.html" data-key="{s['area']}">{thumb}<div class="body"><div class="top"><span class="k">{AREA_LABEL[s['area']]}</span>{status_badge(s)}</div><strong>{E(s['name'])}</strong><p>{E(s['one'])}</p>{stage_bar(s)}</div></a>'''

def tabs(name, items, all_label='전체'):
    btns = f'<button type="button" class="tab" data-val="all" aria-pressed="true">{all_label}</button>' + ''.join(f'<button type="button" class="tab" data-val="{k}" aria-pressed="false">{v}</button>' for k, v in items)
    return f'<div class="tabs" role="group" aria-label="분류" data-tabs="{name}">{btns}</div>'

def crumb(*items):
    parts = ['<a href="index.html">홈</a>']
    for h, t in items:
        parts.append('›'); parts.append(f'<a href="{h}">{E(t)}</a>' if h else f'<span>{E(t)}</span>')
    return '<div class="wrap"><div class="crumb">' + ' '.join(parts) + '</div></div>'

def steps4():
    return '''<div class="steps">
<div class="step"><span class="n">1</span><strong>문의</strong><p>도입 문의 폼 또는 사무국 이메일로 기관명·관심 서비스·적용 교과목을 알려 주세요.</p></div>
<div class="step"><span class="n">2</span><strong>상담·시연</strong><p>사무국이 무상으로 서비스를 시연하고 적용 방법을 안내합니다.</p></div>
<div class="step"><span class="n">3</span><strong>시범 도입</strong><p><span class="nowrap">1개 교과목 × 1개 서비스 × 1개 학기부터</span><br>수업 효과를 확인합니다.</p></div>
<div class="step"><span class="n">4</span><strong>정식 도입</strong><p>교과목·범위·기간을 정해 운영하며 이용 조건은 사무국과 협의합니다.</p></div>
</div>'''

# ------------------------------------------------------------------ 수업 6단계 배치: HAI 활용 매뉴얼(haimanual.csedu4all.com) 기준
MANUAL_STAGES = {   # 매뉴얼 data.js steps 항목 → 이 사이트 slug (2026. 10. 21. 판)
    'hai-pbl': ['design', 'class'],
    'hai-fist': ['content', 'assess', 'analysis'],
    'hai-medlearn-x': ['content', 'practice', 'analysis'],
    'hai-mathtutor': ['content', 'practice', 'assess'],
    'hai-forum': ['class', 'assess', 'analysis'],
    'hai-lrs': ['analysis'],
}
for _s in SERVICES:
    if _s['slug'] in MANUAL_STAGES:
        _s['stage'] = MANUAL_STAGES[_s['slug']]; _s['stage_src'] = 'manual'
    else:
        _s['stage_src'] = 'office' if _s['stage'] else 'none'
STAGE_NO = {k: f'{i+1:02d}' for i, (k, _) in enumerate(STAGES)}
STAGE_CLS = {k: f's{i+1}' for i, (k, _) in enumerate(STAGES)}

def stage_bar(s):
    """카드용 6칸 색 띠: 맡는 단계만 색, 나머지는 연회색"""
    return '<div class="stbar" aria-label="수업 단계">' + ''.join(f'<span class="{STAGE_CLS[k]}{" on" if k in s["stage"] else ""}" title="{v}"></span>' for k, v in STAGES) + '</div>'

# ------------------------------------------------------------------ 외부 글 재디자인: 가져온 본문을 KELI 스타일 블록으로
_MARK = re.compile(r'^\s*[■□▲△●○◆◇▶▷※★☆]\s*')
_KV = re.compile(r'^\s*([^:：]{1,14}?)\s*[:：]\s*(\S.*)$', re.S)
_CAP = re.compile(r'^\s*(?:&lt;|<|\[|\(|【)?\s*사진\s*\d*\s*[:：]?\s*(.*?)\s*(?:&gt;|>|\]|\)|】)?\s*$', re.S)

def _inner_text(h):
    return html.unescape(re.sub(r'<[^>]+>', '', h)).strip()

def _clean_inline(h):
    """문단 안쪽 HTML: 허용 태그만 남은 상태. 앞뒤 공백·줄바꿈 정리"""
    return re.sub(r'\s+', ' ', h).strip()

def restyle(body_html, kind='event'):
    """<p>·<ul>·<img>로 된 본문을 lead · 핵심 요약 · 소제목 · 핵심 정보(kv) · 점 목록 · 그림(캡션) 블록으로 바꿈"""
    if not body_html:
        return ''
    toks = re.findall(r'<(p|ul|ol|h3|h4|blockquote|table)\b[^>]*>(.*?)</\1>', body_html, flags=re.S)
    out, pending_fig, summary, lead_done, seen_heading = [], None, [], False, False
    def flush_summary():
        nonlocal summary
        if summary:
            out.append('<div class="art-sum"><span class="k">핵심 요약</span><ul class="art-ul">' + ''.join(f'<li>{s}</li>' for s in summary) + '</ul></div>')
            summary = []
    for tag, inner in toks:
        inner = _clean_inline(inner)
        text = _inner_text(inner)
        if tag in ('h3', 'h4'):
            flush_summary(); out.append(f'<h2 class="art-h">{_MARK.sub("", inner).strip()}</h2>'); seen_heading = True; continue
        if tag == 'table':
            flush_summary(); out.append(f'<div class="tbl-wrap"><table class="tbl art-tbl">{inner}</table></div>'); continue
        if tag in ('ul', 'ol'):
            flush_summary()
            lis = [_clean_inline(x) for x in re.findall(r'<li\b[^>]*>(.*?)</li>', inner, flags=re.S)]
            lis = [x for x in lis if _inner_text(x)]
            if not lis:
                continue
            kv = [(_KV.match(_inner_text(x)), x) for x in lis]
            if len(lis) >= 2 and sum(1 for m, _ in kv if m) >= max(2, int(len(lis) * 0.6)):
                rows = ''
                for m, x in kv:
                    if m:
                        rows += f'<dt>{html.escape(m.group(1).strip())}</dt><dd>{html.escape(m.group(2).strip())}</dd>'
                    else:
                        rows += f'<dt></dt><dd>{x}</dd>'
                out.append(f'<dl class="art-kv">{rows}</dl>')
            else:
                out.append(f'<{tag} class="art-ul">' + ''.join(f'<li>{x}</li>' for x in lis) + f'</{tag}>')
            continue
        # p / blockquote
        if not text and '<img' not in inner:
            continue
        img = re.search(r'<img[^>]+>', inner)
        if img:
            flush_summary()
            if pending_fig: out.append(pending_fig)
            pending_fig = f'<figure class="art-fig">{img.group(0)}</figure>'
            rest = _inner_text(inner.replace(img.group(0), ''))
            if rest:
                pending_fig = pending_fig.replace('</figure>', f'<figcaption>{html.escape(rest)}</figcaption></figure>')
            continue
        cap = _CAP.match(text)
        if cap and pending_fig and len(text) < 120:
            out.append(pending_fig.replace('</figure>', f'<figcaption>{html.escape(cap.group(1))}</figcaption></figure>')); pending_fig = None
            continue
        if pending_fig:
            out.append(pending_fig); pending_fig = None
        bold_only = re.fullmatch(r'\s*<(strong|b)>(.*?)</\1>\s*', inner, flags=re.S)
        if (_MARK.match(text) and len(text) <= 40) or (bold_only and len(text) <= 40):
            flush_summary()
            t = _MARK.sub('', text).strip().rstrip(':：')
            out.append(f'<h2 class="art-h">{html.escape(t)}</h2>'); seen_heading = True
            continue
        if text.count('▲') >= 2:                                                  # "▲A ▲B ▲C" 나열 → 목록
            flush_summary()
            head, *parts = re.split(r'\s*▲\s*', inner)
            parts = [x.strip() for x in parts if _inner_text(x)]
            if _inner_text(head):
                out.append(f'<p>{head.strip()}</p>')
            out.append('<ul class="art-ul">' + ''.join(f'<li>{x}</li>' for x in parts) + '</ul>')
            continue
        if re.match(r'^\s*[-–ㆍ·]\s+', text) and not seen_heading and not lead_done:
            summary.append(re.sub(r'^\s*[-–ㆍ·]\s+', '', inner)); continue
        flush_summary()
        if not lead_done and not seen_heading:
            out.append(f'<p class="art-lead">{inner}</p>'); lead_done = True
        else:
            out.append(f'<p>{inner}</p>')
    flush_summary()
    if pending_fig: out.append(pending_fig)
    return '<div class="art">' + '\n'.join(out) + '</div>' if out else ''

# ------------------------------------------------------------------ 행사: AI교육확산센터 소식의 [KELI] 글 연동
def _load_feed():
    return _load_json(os.path.join(OUT, 'assets', 'events.live.json'), {"source": "https://aiadvcenter.csedu4all.com/news/stories", "fetched_at": "", "items": []})
FEED = _load_feed()
FEED_ITEMS = _not_hidden('events', FEED.get('items', []))
FEED_IDS = ','.join(str(i['id']) for i in FEED_ITEMS)

def ev_status(it):
    """예정 · 진행 중 · 종료 — 생성 시각(KST) 기준. 화면에서는 JS가 다시 계산"""
    import datetime
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime('%Y-%m-%dT%H:%M')
    s, e = it.get('start') or '', it.get('end') or ''
    if s and now < s: return ('upcoming', '예정')
    if e and now <= e: return ('live', '진행 중')
    return ('ended', '종료')

def ev_href(it):
    return f'event-{it["id"]}.html'

def ev_badge(it):
    k, t = ev_status(it)
    return f'<span class="badge {"live" if k == "upcoming" else ""}" data-ev-status>{t}</span>'

def ev_thumb(it, cls='li-thumb'):
    return f'<span class="{cls}"><img src="{it["thumb"]}" alt="" loading="lazy"></span>' if it.get('thumb') else ''

def ev_row(it):
    return f'<a class="li li-ev" href="{ev_href(it)}" data-ev="{it["id"]}">{ev_thumb(it)}<span><span class="m">{E((it.get("badges") or ["행사"])[0])} · {E(it.get("place") or "")}</span><br><span class="t">{E(it["title"])}</span><br><span class="m">{E(it.get("when") or "")}</span></span><span class="d">{E((it.get("start") or "")[:10].replace("-", "."))} {ev_badge(it)}</span></a>'

def ev_card(it):
    return f'<a class="card card-ev" href="{ev_href(it)}" data-ev="{it["id"]}">{ev_thumb(it, "card-thumb")}<div class="row"><span class="k">{E((it.get("badges") or ["행사"])[0])}</span>{ev_badge(it)}</div><h3>{E(it["title"])}</h3><p>{E(it.get("when") or "")}<br>{E(it.get("place") or "")}</p><span class="more">자세히 보기</span></a>'

FEED_NOTE = f'AI교육확산센터 소식(aiadvcenter.csedu4all.com/news/stories) 중 제목이 [KELI]로 시작하는 글을 자동으로 가져옵니다. <span data-feed-date>{E(FEED.get("fetched_at", ""))}</span> 기준 {len(FEED_ITEMS)}건.'

# ------------------------------------------------------------------ 뉴스레터: 한림대 보도자료 중 KELI·켈리 글 연동
def _load_press():
    return _load_json(os.path.join(OUT, 'assets', 'press.live.json'), {"source": "https://www.hallym.ac.kr/pr/5865/subview.do", "fetched_at": "", "items": []})
PRESS = _load_press()
PRESS_ITEMS = _not_hidden('press', PRESS.get('items', []))
PRESS_IDS = ','.join(str(i['id']) for i in PRESS_ITEMS)
UNN = _load_json(os.path.join(OUT, 'assets', 'unn.live.json'), {"source": "https://news.unn.net", "fetched_at": "", "items": []})
UNN_ITEMS = _not_hidden('unn', UNN.get('items', []))
for _u in UNN_ITEMS:
    _u['src'] = 'unn'
PRESS_ALL = sorted(PRESS_ITEMS + UNN_ITEMS, key=lambda x: x.get('date') or '', reverse=True)   # 한림대 보도자료 + 한국대학신문, 최신순

def pr_href(it):
    return it['url'] if it.get('src') == 'unn' else f'press-{it["id"]}.html'
def pr_ext(it):
    return ' target="_blank" rel="noopener"' if it.get('src') == 'unn' else ''
def pr_thumb(it, cls='li-thumb'):
    return f'<span class="{cls}"><img src="{E(it["thumb"])}" alt="" loading="lazy"></span>' if it.get('thumb') else f'<span class="{cls} li-thumb-ph"><span>{"한국대학신문" if it.get("src") == "unn" else "한림대학교"}</span></span>'
def pr_meta(it):
    if it.get('src') == 'unn':
        return '언론 보도 · 한국대학신문' + ((' · ' + E(it['reporter'])) if it.get('reporter') else '')
    return '보도자료 · 한림대학교' + ((' · ' + E(it['category'])) if it.get('category') else '')

def pr_row(it, summary=True):
    s = f'<br><span class="m">{E((it.get("summary") or "")[:90])}</span>' if summary and it.get('summary') else ''
    return f'<a class="li li-ev" href="{pr_href(it)}"{pr_ext(it)} data-pr="{it["id"]}">{pr_thumb(it)}<span><span class="m">{pr_meta(it)}</span><br><span class="t">{E(it["title"])}</span>{s}</span><span class="d">{E(it.get("date") or "")}</span></a>'

PRESS_NOTE = f'한림대학교 보도자료(hallym.ac.kr › 홍보 › 보도자료) 중 제목에 KELI 또는 켈리가 들어간 글 {len(PRESS_ITEMS)}건과, 한국대학신문(news.unn.net)에서 「한림대 KELI」·「한림대 켈리」로 검색한 기사 {len(UNN_ITEMS)}건을 자동으로 가져옵니다. 신문 기사는 제목·요약·사진만 보여 주고 원문으로 연결합니다. <span data-press-date>{E(PRESS.get("fetched_at", ""))}</span> 기준.'

# ------------------------------------------------------------------ 영상: 한림대학교 유튜브(@HALLYMNEWS)의 KELI 영상 연동
def _load_videos():
    return _load_json(os.path.join(OUT, 'assets', 'videos.live.json'), {"source": "https://www.youtube.com/@HALLYMNEWS", "fetched_at": "", "items": []})
VIDEOS = _load_videos()
VIDEO_ITEMS = _not_hidden('videos', VIDEOS.get('items', []))
VIDEOS_KELI = [v for v in VIDEO_ITEMS if v.get('group') == 'keli']
VIDEOS_REL = [v for v in VIDEO_ITEMS if v.get('group') != 'keli']

def vid_card(v):
    meta = ' · '.join(x for x in [('KELI 영상' if v.get('group') == 'keli' else 'HAI · 소프트랩'), v.get('published') or v.get('published_text') or '', v.get('views') or ''] if x)
    live = '<span class="badge" style="margin-left:6px">실시간 녹화</span>' if v.get('is_live_recording') else ''
    return (f'<div class="vid" data-vid="{v["id"]}" data-embed="{E(v["embed"])}">'
            f'<button type="button" class="vid-play" aria-label="{E(v["title"])} 재생"><img src="{v["thumb"]}" alt="" loading="lazy"><span class="play"></span>'
            f'{("<span class=\"len\">" + E(v["length"]) + "</span>") if v.get("length") else ""}</button>'
            f'<div class="vid-body"><span class="m">{E(meta)}</span>{live}<strong class="t">{E(v["title"])}</strong>'
            f'<a class="more" href="{v["url"]}" target="_blank" rel="noopener">YouTube에서 보기</a></div></div>')

VIDEO_NOTE = f'한림대학교 유튜브 채널(youtube.com/@HALLYMNEWS)에서 제목이나 설명에 KELI 또는 켈리가 들어간 영상을 자동으로 가져옵니다. <span data-video-date>{E(VIDEOS.get("fetched_at", ""))}</span> 기준 KELI 영상 {len(VIDEOS_KELI)}건, 관련 영상 {len(VIDEOS_REL)}건.'

# ------------------------------------------------------------------ 데모 영상: 한림 AI 교육 포털(ai.hallym.ac.kr/hallym-ai) 서비스별 영상 연동
PORTAL_DEMOS = 'https://ai.hallym.ac.kr/hallym-ai'
DEMOS = _load_json(os.path.join(OUT, 'assets', 'demos.live.json'), {"source": PORTAL_DEMOS, "fetched_at": "", "items": []})
DEMO_ITEMS = DEMOS.get('items', [])
DEMO_CATS = []
for _d in DEMO_ITEMS:
    if _d.get('category') not in DEMO_CATS: DEMO_CATS.append(_d.get('category'))

def demo_card(d):
    st = '<span class="badge live">운영 중</span>' if d.get('status') == 'live' else '<span class="badge soon">준비 중</span>'
    name = E(d['name']) + (f' <span class="muted" style="font-weight:500">· {E(d["audience"])}</span>' if d.get('audience') else '')
    media = f'<img src="{d["thumb"]}" alt="" loading="lazy">' if d.get('thumb') else f'<span class="vid-ph"><span>{E(d["name"])}</span></span>'
    return (f'<div class="vid" id="demo-{d["id"]}" data-embed="{E(d["embed"])}">'
            f'<button type="button" class="vid-play" aria-label="{E(d["name"])} 데모 영상 재생">{media}<span class="play"></span></button>'
            f'<div class="vid-body"><span class="m">{E(d.get("category", ""))} {st}</span><strong class="t">{name}</strong>'
            f'<span class="small muted">{E(d.get("summary", ""))}</span></div></div>')

DEMO_NOTE = f'한림 AI 교육 포털의 「한림 AI」 화면(ai.hallym.ac.kr/hallym-ai)에 등록된 서비스별 데모 영상을 자동으로 가져옵니다. <span data-demo-date>{E(DEMOS.get("fetched_at", ""))}</span> 기준 {len({d["service_id"] for d in DEMO_ITEMS})}개 서비스 · 영상 {len(DEMO_ITEMS)}건.'

# ------------------------------------------------------------------ 홈 숫자 3 (관리자 입력 + 포털 자동 수집)
STATS = _load_json(os.path.join(OUT, 'assets', 'stats.json'), {
    "_안내": "KELI 사무국이 관리자 화면(admin.html)에서 고치는 파일입니다. 숫자만 바꾸고 저장하면 1~2분 뒤 홈 화면에 반영됩니다. courses를 null로 두면 한림 AI 교육 포털의 AI 강좌 수를 자동으로 씁니다.",
    "services": 19, "universities": 23, "companies": 31, "courses": None,
    "basis": "2026. 10. KELI 리플렛 · 포털 파트너 목록",
})
def _load_live():
    return _load_json(os.path.join(OUT, 'assets', 'stats.live.json'), {"courses": 1275, "fetched_at": "2026. 10. 29.", "source": "https://ai.hallym.ac.kr/"})
LIVE = _load_live()
def write_stats_files():
    json.dump(STATS, open(os.path.join(OUT, 'assets', 'stats.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(LIVE, open(os.path.join(OUT, 'assets', 'stats.live.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(FEED, open(os.path.join(OUT, 'assets', 'events.live.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(PRESS, open(os.path.join(OUT, 'assets', 'press.live.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(VIDEOS, open(os.path.join(OUT, 'assets', 'videos.live.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(UNN, open(os.path.join(OUT, 'assets', 'unn.live.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    json.dump(DEMOS, open(os.path.join(OUT, 'assets', 'demos.live.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def html_body(b):
    """게시물 본문: HTML이면 그대로, 평문이면 <p>로 감쌈"""
    b = b.strip()
    return b if b.startswith('<') else '<p>' + b + '</p>'

def page_admin():
    body = f"""
<section class="sec" style="padding-top:40px;padding-bottom:80px"><div class="wrap">
<div class="row" style="margin-bottom:28px;align-items:center"><div><span class="eyebrow">KELI 관리자</span><h1 style="font-size:clamp(28px,4vw,40px);margin:4px 0 0">글을 올리고, 고치고, 지웁니다.</h1></div><div class="acts" style="display:flex;gap:8px;flex-wrap:wrap"><a class="btn ghost sm" href="index.html" target="_blank" rel="noopener">사이트 보기</a><button class="btn ghost sm" type="button" id="adm-logout" hidden>로그아웃</button></div></div>

<div id="adm-login" class="login" hidden>
<form class="form" id="login-form" novalidate>
<p class="lead" style="margin:0 0 4px;text-align:left">GitHub 토큰으로 들어갑니다.</p>
<p class="small muted" style="margin:0">이 사이트의 글은 GitHub 저장소({REPO})의 파일에 저장되고, 저장하면 1~2분 뒤 자동으로 배포됩니다. 그래서 저장소에 쓸 수 있는 토큰이 필요합니다. 토큰은 이 브라우저에만 저장되고 어디에도 전송되지 않습니다(GitHub 호출 제외).</p>
<div class="field"><label for="tok">GitHub 토큰 (Fine-grained personal access token)</label><input id="tok" type="password" autocomplete="off" placeholder="github_pat_…"><span class="msg" id="tok-msg"></span></div>
<label class="chk"><input type="checkbox" id="tok-keep" checked><span>이 브라우저에 기억하기(공용 PC에서는 끄세요)</span></label>
<div class="acts"><button class="btn" type="submit" id="tok-go">들어가기</button><a class="more" href="#help" id="tok-help">토큰 만드는 방법</a></div>
</form>
<div class="card" style="margin-top:20px" id="help-card">
<span class="k">토큰 만드는 방법 (한 번만)</span>
<ol style="padding-left:20px;margin:8px 0 0;font-size:15px">
<li>GitHub 로그인 → 오른쪽 위 프로필 → Settings → 왼쪽 맨 아래 Developer settings → Personal access tokens → Fine-grained tokens → Generate new token</li>
<li>Token name: KELI 관리자 / Expiration: 1년(또는 원하는 기간)</li>
<li>Repository access: Only select repositories → <strong>{REPO}</strong> 선택</li>
<li>Permissions → Repository permissions: <strong>Contents: Read and write</strong>, <strong>Actions: Read and write</strong> (나머지는 그대로)</li>
<li>Generate token → 나온 문자열(github_pat_…)을 위 칸에 붙여 넣기</li>
</ol>
<p class="small muted" style="margin:10px 0 0">저장소가 다른 사람 소유이면 그 사람이 유은님 계정을 저장소 Collaborator(Write)로 먼저 초대해야 합니다. 토큰을 잃어버리면 같은 방법으로 새로 만들면 됩니다.</p>
</div>
</div>

<div id="adm-app" class="adm" hidden>
<nav class="adm-nav" aria-label="관리자 메뉴">
<a href="#home" data-view="home">대시보드</a>
<a href="#notices" data-view="notices">공지사항 <span class="cnt" data-cnt="notices"></span></a>
<a href="#archive" data-view="archive">아카이브 <span class="cnt" data-cnt="archive"></span></a>
<a href="#stats" data-view="stats">홈 숫자</a>
<a href="#feeds" data-view="feeds">자동 연동 글</a>
<a href="#help" data-view="help">도움말</a>
</nav>
<div class="adm-main">
<div class="deploy" id="deploy" data-state="idle"><span class="dot"></span><span id="deploy-text">배포 상태를 확인하는 중…</span><a id="deploy-link" class="more" href="https://github.com/{REPO}/actions" target="_blank" rel="noopener" style="margin-left:auto">배포 기록</a></div>
<div id="view" style="margin-top:20px"></div>
</div>
</div>
</div></section>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<div class="modal" id="modal" role="dialog" aria-modal="true"><div class="box" id="modal-box"></div></div>
<script>window.KELI_ADMIN={{repo:"{REPO}",branch:"main",site:"{SITE_URL}",workflow:"pages.yml"}};</script>
"""
    write('admin.html', 'KELI 관리자', body)

# ------------------------------------------------------------------ 페이지
def page_index():
    cards = ''.join(svc_card(s) for s in SERVICES)
    notices = ''.join(f'<a class="li" href="notice-{n["id"]}.html"><span><span class="t">{E(n["title"])}</span></span><span class="d">{n["date"]}</span></a>' for n in NOTICES[:3])
    body = f'''
<section class="hero"><div class="wrap">
<span class="eyebrow">K-University AI EdTech and Learning Initiative</span>
<h1>대학이 함께 만드는<br>AI 기반 고등교육 혁신 생태계.</h1>
<p class="lead">한림대가 개발하고 수업에서 검증한 AI 교육 서비스를 <br class="d">국내외 대학·기관에 제공하고 함께 확산합니다.</p>
<div class="acts"><a class="btn" href="services.html">서비스 둘러보기</a><a class="more" href="join.html#inquiry">도입 문의</a></div>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="grid g3" id="stats">
<div class="card"><span class="num" data-stat="services" data-count="{STATS['services']}">{STATS['services']}</span><h3>AI 교육 서비스</h3><p>한림대가 개발하고 수업에서 검증한 HAI Ecosystems</p></div>
<div class="card"><span class="num" data-stat="partners" data-count="{STATS['universities'] + STATS['companies']}">{STATS['universities'] + STATS['companies']}</span><h3>참여 기관</h3><p>대학 <span data-stat="universities">{STATS['universities']}</span> · 에듀테크 기업 <span data-stat="companies">{STATS['companies']}</span></p></div>
<div class="card"><span class="num" data-stat="courses" data-count="{LIVE['courses']}">{LIVE['courses']:,}</span><h3>AI 결합 강좌</h3><p>한림대학교 누적 운영 강좌 · <span data-stat="courses_note">한림 AI 교육 포털 {LIVE['fetched_at']} 기준</span></p></div>
</div>
<p class="note" style="margin-top:16px">기준: 서비스·참여 기관 수는 사무국이 직접 입력합니다(2026. 10. KELI 리플렛·포털 파트너 목록). AI 결합 강좌 수는 한림 AI 교육 포털(ai.hallym.ac.kr)의 "AI 강좌 수"를 매일 자동으로 가져옵니다.</p>
</div></section>

<section class="sec" id="services"><div class="wrap">
<div class="head"><span class="eyebrow">HAI Ecosystems</span><h2>수업 설계부터 평가·분석까지, 19개 서비스.</h2><p class="lead">한림대학교가 직접 개발해 수업에서 검증한 뒤 KELI Marketplace에 먼저 올린 서비스입니다. 다른 대학과 기관도 도입할 수 있습니다.</p></div>
{tabs('home-svc', [(a[0], a[1]) for a in AREAS])}
<div class="grid g4" data-items="home-svc" style="margin-top:24px">{cards}</div>
<div class="cta" style="margin-top:40px"><div class="acts"><a class="btn ghost" href="demos.html">전체 데모 영상</a><a class="btn ghost" href="{MANUAL_SITE}" target="_blank" rel="noopener">HAI 활용 매뉴얼</a></div></div>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="head"><span class="eyebrow">참여 방법</span><h2>모든 참여는 KELI 사무국을 통해 시작합니다.</h2><p class="lead">첫걸음은 1개 교과목 × 1개 서비스 × 1개 학기. 시범 도입은 무상 또는 협의, 정식 도입은 기관별 협의입니다.</p></div>
{steps4()}
<div class="cta" style="margin-top:40px"><div class="acts"><a class="btn" href="join.html#inquiry">도입 문의</a><a class="more" href="join.html">참여 방법 자세히</a></div></div>
</div></section>

<section class="sec"><div class="wrap">
<div class="grid g2" style="gap:48px">
<div>
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">행사</h2><a class="more" href="events.html">전체 보기</a></div>
<div data-events="home" data-pages="{FEED_IDS}">{ev_card(FEED_ITEMS[0]) if FEED_ITEMS else '<div class="empty">아직 등록된 행사가 없습니다.</div>'}</div>
<p class="note" style="margin-top:12px">예정된 행사가 등록되면 이 자리에 먼저 보입니다.</p>
</div>
<div>
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">공지사항</h2><a class="more" href="notice.html">전체 보기</a></div>
<div class="list">{notices}</div>
<form class="form" data-demo="nl" style="margin-top:20px;padding:20px;gap:12px" novalidate>
<div class="field"><label for="nl-email">뉴스레터 받기</label><div style="display:flex;gap:8px;flex-wrap:wrap"><input id="nl-email" type="email" placeholder="이메일 주소" required style="flex:1;min-width:200px"><button class="btn" type="submit">구독</button></div><span class="msg">이메일 주소를 확인해 주세요.</span></div>
<div class="done"><span>구독 신청이 접수되었습니다. 확인 메일의 링크를 누르면 구독이 완료됩니다. (접수번호 <code></code>)</span></div>
</form>
</div>
</div>
</div></section>
'''
    return body

def page_about():
    body = crumb((None, 'KELI 소개')) + f'''
<section class="hero" style="padding-top:48px"><div class="wrap">
<span class="eyebrow">KELI란</span>
<h1>한림대가 먼저 만들고 검증한 것을,<br>여러 대학이 나누어 씁니다.</h1>
<p class="lead">KELI는 한림대학교가 자체 개발한 고등교육 맞춤형 AI 교육 서비스 HAI Ecosystems를 국내외 대학·기관에 제공하고, 함께 검증·확산하는 고등교육 AI 공유 플랫폼입니다.</p>
<div class="chips"><span class="chip">주관 · 한림대학교 KELI 사무국</span><span class="chip">대상 · 국내외 대학·기관·기업</span><span class="chip">제공 · 무상 시범 도입 → 유상 정식 도입</span></div>
</div></section>

<section class="sec alt" id="offer"><div class="wrap">
<div class="head"><h2>무엇을 제공하나요.</h2></div>
<div class="grid g3">
<a class="card" href="services.html"><span class="k">HAI Ecosystems</span><h3>한림대 자체 개발 AI 교육 서비스</h3><p>수업 설계부터 평가·분석까지, 6영역 19개 서비스.</p><span class="more">서비스 보기</span></a>
<a class="card" href="services.html"><span class="k">KELI Marketplace</span><h3>서비스 탐색부터 도입 신청까지</h3><p>영역별로 찾고, 데모 영상과 매뉴얼을 확인하고, 도입을 문의합니다.</p><span class="more">마켓 보기</span></a>
<a class="card" href="join.html"><span class="k">실증·연수 지원</span><h3>한 학기 시범 운영과 효과 분석</h3><p>교수자 연수와 효과 분석 리포트를 함께 제공합니다.</p><span class="more">참여 방법</span></a>
</div>
</div></section>

<section class="sec" id="why"><div class="wrap">
<div class="head"><h2>왜 함께 만드나요.</h2><p class="lead">대학마다 따로 만들면 비용과 인력이 중복됩니다. 한림대가 먼저 만들고 검증한 것을 여러 대학이 나누어 씁니다.</p></div>
<div class="vs">
<div class="card"><span class="k">따로 만들면</span><h3>대학마다 비용·인력 중복</h3><p>유사한 AI 튜터·챗봇을 반복 개발하고, 사업이 끝나면 유지보수가 끊깁니다.</p></div>
<div class="card" style="background:var(--accent);color:var(--accent-fg)"><span class="k" style="color:inherit;opacity:.8">함께 만들면</span><h3>한 번 만들어 함께 씁니다</h3><p style="color:inherit;opacity:.9">검증된 서비스에 소규모 대학도 같은 품질로 접근하고, 여러 대학의 운영 결과가 근거로 쌓입니다.</p></div>
</div>
</div></section>

<section class="sec alt" id="vision"><div class="wrap">
<div class="head"><span class="eyebrow">Vision</span><h2>K-University 모델을 함께 개발·공유·확산하고,<br>글로벌 고등교육의 AI 대전환을 선도합니다.</h2></div>
<div class="grid g3">
<div class="card center"><h3>검증된 AI 서비스를<br>여러 대학이 함께 씁니다</h3></div>
<div class="card center"><h3>대학·기업·기관이<br>함께 개발하고 실증합니다</h3></div>
<div class="card center"><h3>K-University 모델을<br>국내외로 확산합니다</h3></div>
</div>
</div></section>

<section class="sec" id="structure"><div class="wrap">
<div class="head"><h2>KELI 구조.</h2></div>
<div class="tbl-wrap"><table class="tbl">
<tbody>
<tr><th>서비스 영역</th><td>플랫폼 · 진로 · 코스웨어 · 수업 · 데이터 · 행정</td></tr>
<tr><th>운영 사이클</th><td>발견 → 연결 → 실증 → 확산</td></tr>
<tr><th>참여 주체</th><td>국내외 대학 · 에듀테크 기업 · 유관기관</td></tr>
<tr><th>참여 방식</th><td>공동 실증 · 공동 개발 · Marketplace 등재</td></tr>
<tr><th>운영 기구</th><td>총회 · 운영위원회 · 기술표준위원회 · 품질윤리위원회</td></tr>
<tr><th>사무국 역할</th><td>협의체 운영 · 참여 문의 · 회원 협력 · 포털 운영</td></tr>
</tbody></table></div>
</div></section>

<section class="sec alt" id="office"><div class="wrap">
<div class="grid g2" style="align-items:center;gap:48px">
<div class="head" style="margin:0"><h2>KELI 사무국.</h2><p class="lead">한림대학교 AI교육혁신원 AI교육확산센터가 사무국을 맡고 있습니다. 궁금한 점은 언제든 연락 주세요.</p></div>
<div class="card">
<dl class="kv"><dt>이메일</dt><dd><span class="copy">{EMAIL} <button type="button" class="btn sm ghost" data-copy="{EMAIL}">복사</button></span></dd><dt>주소</dt><dd>(24252) 강원특별자치도 춘천시 한림대학길 1 한림대학교</dd><dt>포털</dt><dd>keliedu.org/keli</dd><dt>Instagram</dt><dd><a href="{INSTA}" target="_blank" rel="noopener">@hallym_keli</a></dd></dl>
<a class="btn" href="join.html#inquiry" style="align-self:flex-start;margin-top:8px">도입 문의</a>
</div>
</div>
</div></section>
'''
    write('about.html', 'KELI 소개', body)

def page_services():
    cards = ''.join(svc_card(s) for s in SERVICES)
    body = crumb((None, '마켓플레이스')) + f'''
<section class="hero" style="padding-top:48px"><div class="wrap">
<span class="eyebrow">HAI Ecosystems · Hallym AI</span>
<h1>한림대학교가 수업에서 써 온<br>AI 교육 서비스.</h1>
<p class="lead">직접 개발해 수업에서 검증한 뒤 KELI Marketplace에 먼저 올린 서비스입니다. 다른 대학과 기관도 도입할 수 있습니다.</p>
<div class="acts"><a class="btn ghost" href="demos.html">전체 데모 영상</a><a class="btn ghost" href="{MANUAL_SITE}" target="_blank" rel="noopener">HAI 활용 매뉴얼</a><a class="more" href="curriculum.html">수업에 결합하는 방법</a></div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap">
<div class="row" style="margin-bottom:20px">{tabs('svc', [(a[0], a[1]) for a in AREAS])}<span class="muted small"><span data-count="svc">19개</span> 서비스</span></div>
<div class="grid g3" data-items="svc">{cards}</div>
</div></section>
<section class="sec alt"><div class="wrap">
<div class="grid g2" style="align-items:center;gap:48px">
<div class="head" style="margin:0"><span class="eyebrow">파트너 서비스</span><h2>에듀테크 기업의 서비스도 Marketplace에 등재됩니다.</h2><p class="lead">등재 후 대학 수업에서 효과를 검증받습니다. 첫걸음은 서비스 등재 신청입니다.</p></div>
<div class="card"><h3>등재를 원하시면</h3><p>도입 문의 폼에서 참여 유형을 "에듀테크 기업"으로 선택하고 등재 희망 서비스명을 적어 주세요. 사무국이 품질·보안 기준과 절차를 안내합니다.</p><a class="btn" href="join.html?type=company#inquiry" style="align-self:flex-start;margin-top:8px">등재 문의</a></div>
</div>
</div></section>
'''
    write('services.html', 'KELI 마켓플레이스', body)

def page_service(s):
    area = AREA_LABEL[s['area']]
    if s['img']:
        logo = ' logo' if s['img'].endswith('.png') else ''
        shot = f'<div class="svc" style="background:var(--bg2)"><div class="thumb{logo}"><img src="assets/img/services/{s["img"]}" alt="{E(s["name"])} 서비스 화면"></div></div>'
    else:
        shot = f'<div class="svc"><div class="thumb"><span class="word">{E(s["name"])}</span></div></div><p class="note" style="margin-top:8px">서비스 화면은 등록 예정입니다.</p>'
    links = ''
    if s['url']: links += f'<a class="more" href="{s["url"]}" target="_blank" rel="noopener">서비스 바로가기</a>'
    links += f'<a class="more" href="{s["video"] or DEMO_ALL}" target="_blank" rel="noopener">데모 영상</a>'
    links += f'<a class="more" href="{s["manual"] or MANUAL_SITE}" target="_blank" rel="noopener">매뉴얼</a>'
    feats = ''.join(f'<div class="card"><h3>{E(f)}</h3></div>' for f in s['features']) if s['features'] else '<div class="card"><h3>핵심 기능</h3><p>사무국 확정 후 반영됩니다.</p></div>'
    usage = f'<p class="lead" style="max-width:760px">{E(s["usage"])}</p>' if s['usage'] else ''
    stages = ''.join(f'<div class="stage {STAGE_CLS[k]}{" on" if k in s["stage"] else ""}"><span class="no">{STAGE_NO[k]}</span>{v}</div>' for k, v in STAGES)
    stage_note = {'manual': f'색이 칠해진 단계가 이 서비스가 맡는 단계입니다. 출처: <a href="{MANUAL_SITE}" target="_blank" rel="noopener">HAI 활용 매뉴얼</a>(수업의 순간마다 HAI ECOSYSTEM이 함께합니다).',
                  'office': '색이 칠해진 단계가 이 서비스가 맡는 단계입니다. HAI 활용 매뉴얼에 아직 배치되지 않은 서비스라 사무국 배치(확정 전)입니다.',
                  'none': '통합 플랫폼·진로 서비스는 특정 수업 단계에 매이지 않습니다.'}[s['stage_src']]
    status = STATUS[s['status']][0] if s['status'] else '확인 중'
    provider = '한림대학교 (HAI Ecosystems)'
    siblings = [x for x in SERVICES if x['area'] == s['area'] and x['slug'] != s['slug']]
    sib = ''.join(svc_card(x) for x in siblings[:3])
    body = crumb(('services.html', '마켓플레이스'), (None, s['name'])) + f'''
<section class="hero" style="padding-top:40px;padding-bottom:40px"><div class="wrap">
<span class="eyebrow">{area}</span>
<h1>{E(s['name'])}</h1>
<p class="lead">{E(s['head'])}</p>
<div class="acts"><a class="btn" href="join.html?service={s['slug']}#inquiry">도입 문의</a>{links}</div>
</div></section>
<section class="sec" style="padding-top:24px"><div class="wrap">
<div class="grid g2" style="gap:48px;align-items:start">
<div>{shot}</div>
<div style="display:flex;flex-direction:column;gap:24px">
<p style="font-size:19px;line-height:1.8">{E(s['desc'])}</p>
<dl class="kv"><dt>제공</dt><dd>{provider}</dd><dt>운영 상태</dt><dd>{status}</dd><dt>이용 방식</dt><dd>시범 도입(무상 또는 협의) → 정식 도입(유상·기관별 협의)</dd><dt>매뉴얼</dt><dd><a href="{s['manual'] or MANUAL_SITE}" target="_blank" rel="noopener">{'PDF 열기' if s['manual'] else 'HAI 활용 매뉴얼 사이트'}</a></dd></dl>
</div>
</div>
</div></section>
<section class="sec alt"><div class="wrap">
<div class="head"><h2>핵심 기능.</h2>{usage}</div>
<div class="grid g3">{feats}</div>
</div></section>
<section class="sec"><div class="wrap">
<div class="head"><h2>수업의 어느 단계에서 쓰나요.</h2><p class="lead">설계부터 분석·개선까지 수업 6단계 중 이 서비스가 맡는 단계입니다.</p></div>
<div class="stages">{stages}</div>
<p class="note" style="margin-top:12px">{stage_note} <a href="curriculum.html">AI 융합교육과정 보기</a></p>
</div></section>
{'<section class="sec alt"><div class="wrap"><div class="row" style="margin-bottom:20px"><h2 style="font-size:28px">같은 영역의 서비스</h2><a class="more" href="services.html#' + s['area'] + '">' + area + ' 전체</a></div><div class="grid g3">' + sib + '</div></div></section>' if sib else ''}
<section class="sec"><div class="wrap"><div class="cta"><h2>내 교과목에 적용하려면.</h2><p class="lead">첫걸음은 1개 교과목 × 1개 서비스 × 1개 학기입니다.</p><div class="acts"><a class="btn" href="join.html?service={s['slug']}#inquiry">도입 문의</a><a class="more" href="archive.html#case">실증 사례 보기</a></div></div></div></section>
'''
    write(f'service-{s["slug"]}.html', f'{s["name"]} · KELI', body, desc=s['head'])

def page_curriculum():
    cols = ''
    for k, v in STAGES:
        items = [s for s in SERVICES if k in s['stage']]
        chips = ''.join(f'<a class="chip{" src-manual" if s["stage_src"] == "manual" else ""}" href="service-{s["slug"]}.html">{E(s["name"])}</a>' for s in items) or '<span class="chip muted">배치 예정</span>'
        cols += f'<div class="flow-step {STAGE_CLS[k]}"><div class="fs-head"><span class="no">{STAGE_NO[k]}</span><span class="lb">{v}</span></div><div class="fs-list">{chips}</div></div>'
    body = crumb(('services.html', '마켓플레이스'), (None, 'AI 융합교육과정')) + f'''
<section class="hero" style="padding-top:48px"><div class="wrap">
<span class="eyebrow">AI 융합교육과정</span>
<h1>수업 설계부터 평가·분석까지,<br>AI를 수업에 결합합니다.</h1>
<p class="lead">HAI Ecosystems를 교과목에 어떻게 결합하는지 보여주는 모델 페이지입니다. 연수 안내가 아니라, 어떤 단계에서 어떤 서비스를 쓰는지를 설명합니다.</p>
</div></section>
<section class="sec alt"><div class="wrap">
<div class="head"><h2>수업 6단계와 서비스.</h2><p class="lead">수업의 순간마다 어떤 HAI 서비스가 함께하는지, 단계별로 보여줍니다. 하나의 플랫폼이 전 과정을 대체하기보다 수업 목적과 단계에 따라 여러 서비스를 골라 조합하는 구조입니다.</p></div>
<div class="flow">{cols}</div>
<p class="note" style="margin-top:16px"><span class="chip src-manual" style="height:26px;font-size:12px;margin-right:6px">진한 글씨</span>는 <a href="{MANUAL_SITE}" target="_blank" rel="noopener">HAI 활용 매뉴얼</a>의 "수업의 순간마다, HAI ECOSYSTEM이 함께합니다" 배치를 그대로 옮긴 것이고, 나머지는 매뉴얼에 아직 없는 서비스를 사무국이 배치한 것(확정 전)입니다. 매뉴얼의 풀리캠퍼스, SmartLEAD, CLASSUM, HAI-EpiLearn, HAI-WebP, HAI-Tutor는 KELI 제공 목록(19종)에 없어 제외했습니다.</p>
</div></section>
<section class="sec"><div class="wrap">
<div class="head"><h2>AI 결합 수업 모델.</h2><p class="lead">AI 교수·조교·튜터의 활용 정도에 따라 교과목 유형을 단계로 나누고, 수업은 사전지식 → 진단 → 처방의 3단계(HTHT)로 운영합니다.</p></div>
<div class="grid g3">
<div class="card"><span class="k">사전지식</span><h3>학습자가 먼저 익힙니다</h3><p>AI 튜터·코스웨어로 기초 개념을 미리 학습합니다.</p></div>
<div class="card"><span class="k">진단</span><h3>어디서 막히는지 확인합니다</h3><p>적응형 평가와 학습데이터로 수준과 취약점을 진단합니다.</p></div>
<div class="card"><span class="k">처방</span><h3>맞춤 지원으로 완전학습</h3><p>수준에 맞는 힌트·피드백과 교수자의 개별 지도가 이어집니다.</p></div>
</div>
</div></section>
<section class="sec alt"><div class="wrap">
<div class="head"><h2>운영 계획과 가이드북.</h2></div>
<div class="grid g3">
<a class="card" href="{GUIDE % 'd4ce49e79df9428abbe587634ce096ba'}" target="_blank" rel="noopener"><span class="k">PDF</span><h3>AI 융합교육 활성화를 위한 교육과정 운영 계획</h3><p>한림대학교</p></a>
<a class="card" href="{GUIDE % '7a53ea4f0683488c8d74b873e62de7fd'}" target="_blank" rel="noopener"><span class="k">PDF</span><h3>HTHT 기반 생성형 AI 결합 교과목 수업 가이드북 ver 1.5</h3><p>교육혁신센터</p></a>
<a class="card" href="{GUIDE % '29aa9e48e59f49b695c81b09c000caa6'}" target="_blank" rel="noopener"><span class="k">PDF</span><h3>교수자를 위한 AI 활용 가이드라인</h3><p>교육혁신센터</p></a>
</div>
</div></section>
<section class="sec"><div class="wrap"><div class="cta"><h2>내 교과목에 적용하려면.</h2><p class="lead">첫걸음은 1개 교과목 × 1개 서비스 × 1개 학기입니다.</p><div class="acts"><a class="btn" href="join.html#inquiry">도입 문의</a><a class="more" href="archive.html#case">실증 사례 보기</a></div></div></div></section>
'''
    write('curriculum.html', 'AI 융합교육과정 · KELI', body)

def page_join():
    # 관심 서비스: 6영역별로 묶어서 표시
    svc_opts = ''
    for key, label, _en in AREAS:
        chips = ''.join(f'<label class="chip sel"><input type="checkbox" name="services" value="{s["slug"]}"> {E(s["name"])}</label>' for s in SERVICES if s['area'] == key)
        svc_opts += f'<div class="chipgrp"><span class="gk">{label}</span><div class="chips">{chips}</div></div>'
    univ = ''.join(f'<span class="chip">{E(u)}</span>' for u in UNIV)
    corp = ''.join(f'<span class="chip">{E(c)}</span>' for c in CORP)
    body = crumb((None, '참여·도입')) + f'''
<section class="hero" style="padding-top:48px"><div class="wrap">
<span class="eyebrow">참여 방법</span>
<h1>모든 참여는<br>KELI 사무국을 통해 시작합니다.</h1>
<p class="lead">대학은 수업 도입으로, 기업은 서비스 등재로, 기관은 공동 과제 제안으로. 첫걸음은 작게 시작합니다.</p>
<div class="acts"><a class="btn" href="#inquiry">도입 문의</a></div>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="head"><h2>참여하면 이런 일이 생깁니다.</h2></div>
<div class="grid g3">
<div class="card"><span class="k">국내외 대학</span><h3>HAI 서비스를 수업에 도입하고, 시범 운영 후 정식 도입</h3><p>첫걸음: 1교과목 · 1서비스 · 1학기</p></div>
<div class="card"><span class="k">에듀테크 기업</span><h3>Marketplace 등재 후 수업에서 효과 검증</h3><p>첫걸음: 서비스 등재 신청</p></div>
<div class="card"><span class="k">유관기관</span><h3>공동 연구·실증 참여, 정책·표준 근거 확보</h3><p>첫걸음: 공동 과제 제안</p></div>
</div>
</div></section>

<section class="sec"><div class="wrap">
<div class="head"><h2>도입 절차.</h2></div>
{steps4()}
<div class="grid g2" style="margin-top:40px">
<div class="card"><div class="row"><h3>시범 도입 · 실증</h3><span class="badge">무상 또는 협의</span></div><p><span class="nowrap">1개 교과목 × 1개 서비스 × 1개 학기부터</span><br>수업 효과를 확인합니다.</p></div>
<div class="card"><div class="row"><h3>정식 도입</h3><span class="badge">유상 · 기관별 협의</span></div><p>교과목·범위·기간을 정해 운영하며 이용 조건은 KELI 사무국과 협의합니다.</p></div>
</div>
</div></section>

<section class="sec alt"><div class="wrap">
<div class="head"><h2>참여 유형.</h2></div>
<div class="grid g3">
<div class="card"><h3>국내외 대학</h3><p>KELI 협의체 회원으로 참여합니다.</p></div>
<div class="card"><h3>해외 대학·기관</h3><p>현지화 라이선스와 국제 프로그램으로 참여합니다.</p></div>
<div class="card"><h3>에듀테크 기업</h3><p>Marketplace 등재와 공동 개발로 참여합니다.</p></div>
</div>
</div></section>

<section class="sec" id="members"><div class="wrap">
<div class="head"><h2>함께하는 기관.</h2><p class="lead">대학 {len(UNIV)}곳, 에듀테크 기업 {len(CORP)}곳이 참여하고 있습니다.</p></div>
<h3 style="margin-bottom:12px">대학</h3><div class="chips" style="margin-bottom:28px">{univ}</div>
<h3 style="margin-bottom:12px">에듀테크 기업</h3><div class="chips">{corp}</div>
<p class="note" style="margin-top:16px">2026. 10. 기준 KELI 포털 파트너 목록. 가입·탈퇴에 따라 갱신됩니다.</p>
</div></section>

<section class="sec alt" id="inquiry"><div class="wrap">
<div class="grid g2" style="gap:48px;align-items:start">
<div class="head" style="margin:0"><h2>도입·참여 문의.</h2><p class="lead">기관명·관심 서비스·적용 교과목을 적어 보내 주세요. 사무국이 이메일로 답변드립니다.</p>
<div class="card" style="margin-top:8px"><span class="k">이메일로 보내시려면</span><p><span class="copy">{EMAIL} <button type="button" class="btn sm ghost" data-copy="{EMAIL}">복사</button></span></p><p>메일 제목 앞에 [서비스 도입 문의]를 붙여 주시면 빠릅니다.</p><p>소식은 <a href="{INSTA}" target="_blank" rel="noopener">Instagram @hallym_keli</a>에서도 볼 수 있습니다.</p></div></div>
<form class="form" data-demo="inq" novalidate>
<div class="field"><label for="f-type">참여 유형</label><select id="f-type" name="type" required><option value="">선택</option><option value="univ">국내 대학</option><option value="abroad">해외 대학·기관</option><option value="company">에듀테크 기업</option><option value="agency">유관기관</option></select><span class="msg">참여 유형을 선택해 주세요.</span></div>
<div class="grid g2" style="gap:16px">
<div class="field"><label for="f-org">기관명</label><input id="f-org" name="org" type="text" required placeholder="예) ○○대학교"><span class="msg">기관명을 입력해 주세요.</span></div>
<div class="field"><label for="f-name">담당자</label><input id="f-name" name="name" type="text" required placeholder="성명"><span class="msg">담당자 성명을 입력해 주세요.</span></div>
<div class="field"><label for="f-email">이메일</label><input id="f-email" name="email" type="email" required placeholder="name@univ.ac.kr"><span class="msg">이메일 주소를 확인해 주세요.</span></div>
<div class="field"><label for="f-tel">연락처</label><input id="f-tel" name="tel" type="tel" placeholder="선택"></div>
</div>
<div class="field"><label>관심 서비스</label><span class="hint">영역별로 골라 주세요. 여러 개를 고를 수 있습니다. 기업은 등재 희망 서비스명을 아래 내용에 적어 주세요.</span><div class="chipgrps">{svc_opts}</div></div>
<div class="field"><label for="f-course">적용 교과목</label><input id="f-course" name="course" type="text" placeholder="예) 선형대수학 (2027-1학기, 수강 60명)"></div>
<div class="field"><label for="f-body">문의 내용</label><textarea id="f-body" name="body" rows="5" placeholder="원하시는 참여 방식, 일정, 궁금한 점을 적어 주세요."></textarea></div>
<label class="chk"><input type="checkbox" id="f-agree" required><span>개인정보 수집·이용에 동의합니다. 문의 처리 목적으로만 이용하며 처리 후 파기합니다. <a href="privacy.html">개인정보처리방침</a></span></label>
<div><button class="btn" type="submit">문의 보내기</button></div>
<div class="done"><span>접수되었습니다. 접수번호 <code></code> · 사무국이 입력하신 이메일로 답변드립니다. (시연 화면: 실제 발송은 백엔드 연동 후 동작합니다)</span></div>
</form>
</div>
</div></section>
'''
    write('join.html', '참여·도입 · KELI', body)

ARCH_ICON = {'pdf': 'PDF', 'doc': '문서', 'video': '영상', 'link': '링크', 'image': '이미지'}
def arch_has_page(a):
    fs = a.get('files') or []
    return bool(a.get('body')) or len(fs) > 1 or (fs and a.get('url'))
def arch_meta(a):
    bits = [a.get('org') or '', a.get('author') or '', a.get('period') or a.get('date') or '']
    return ' · '.join(E(b) for b in bits if b)
def arch_card(a):
    href, ext = arch_href(a)
    cover = f'<img src="{E(a["cover"])}" alt="" loading="lazy">' if a.get('cover') else f'<span class="acover-ph"><span>{E(a["title"])}</span></span>'
    return (f'<a class="acard" href="{E(href)}"{ext}><span class="acover">{cover}</span>'
            f'<span class="abody"><span class="m"><span class="badge">{ARCH_ICON.get(a.get("type"), "자료")}</span></span><strong class="t">{E(a["title"])}</strong><span class="m">{arch_meta(a)}</span></span></a>')
def arch_href(a):
    """목록에서 누르면: 설명 글·첨부 여러 개 → 자료 페이지 / 외부 주소 → 새 창 / 파일 하나 → 그 파일"""
    if arch_has_page(a):
        return f'archive-{a["id"]}.html', ''
    fs = a.get('files') or []
    if a.get('url'):
        return a['url'], ' target="_blank" rel="noopener"'
    if fs:
        return fs[0]['url'], ' target="_blank" rel="noopener"'
    return 'archive.html', ''

def page_archive():
    def row(a):
        href, ext = arch_href(a)
        fs = a.get('files') or []
        extra = (f' · {E(a["author"])}' if a.get('author') else '') + (f' · 첨부 {len(fs)}' if len(fs) > 1 else '')
        return f'<a class="li" href="{E(href)}"{ext}><span><span class="badge" style="margin-right:8px">{ARCH_ICON.get(a.get("type"), "자료")}</span><span class="t">{E(a["title"])}</span><br><span class="m">{E(a.get("org", ""))}{extra}</span></span><span class="d">{E(a.get("date", ""))}</span></a>'
    for a in ARCHIVE:
        if arch_has_page(a): page_archive_detail(a)
    secs = ''
    for key, label in ARCH_CATS:
        items = [a for a in ARCHIVE if a['cat'] == key]
        rows = ''.join(row(a) for a in items) if items else '<p class="muted" style="padding:20px 4px;border-bottom:1px solid var(--line)">아직 등록된 자료가 없습니다.</p>'
        secs += f'''
<section class="sec" id="{key}" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px"><a href="archive-{key}.html" style="color:inherit">{label}</a></h2><a class="more" href="archive-{key}.html">전체 보기 · {len(items)}건</a></div><div class="list">{rows}</div>
</div></section>'''
        page_archive_cat(key, label, items, row)
    body = crumb((None, '아카이브')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap">
<span class="eyebrow">아카이브</span>
<h1>검증된 경험을<br>다음 대학의 근거로.</h1>
<p class="lead">실증 사례집, 기술 동향·연구, 매뉴얼·소개자료를 한 곳에 모았습니다.</p>
</div></section>{secs}
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<p class="note">자료는 새 창에서 열립니다. 일부 PDF는 한림 AI 교육 포털에 있습니다.</p>
</div></section>
'''
    write('archive.html', '아카이브 · KELI', body)

ARCH_CAT_LEAD = {'case': '한림대학교 교수진이 실제 수업에 AI를 결합해 설계·운영한 기록입니다. 교과목별 계획서·주차별 세부 계획·결과보고서를 담았습니다.',
                 'trend': '월간 에듀테크 솔루션 분석 보고서와 AI 튜터 분석 보고서 등, KELI 연구진이 펴내는 동향·연구 자료입니다.',
                 'manual': 'HAI Ecosystems 활용 매뉴얼과 가이드라인, KELI 소개 자료를 모았습니다.'}
def page_archive_cat(key, label, items, row):
    rows = ''.join(row(a) for a in items) if items else '<p class="muted" style="padding:20px 4px;border-bottom:1px solid var(--line)">아직 등록된 자료가 없습니다.</p>'
    body = crumb(('archive.html', '아카이브'), (None, label)) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap"><span class="eyebrow">아카이브</span><h1>{E(label)}.</h1><p class="lead">{E(ARCH_CAT_LEAD.get(key, ''))}</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">{E(label)}</h2><span class="muted small">{len(items)}개 자료</span></div><div class="list">{rows}</div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px"><p class="note">자료는 새 창 또는 자료 페이지에서 열립니다. 다른 분류: {' · '.join(f'<a href="archive-{k}.html">{l}</a>' for k, l in ARCH_CATS if k != key)}</p></div></section>
'''
    write(f'archive-{key}.html', f'{label} · KELI 아카이브', body)

def page_archive_detail(a):
    cat = dict(ARCH_CATS).get(a.get('cat'), '아카이브')
    files = a.get('files') or []
    pdfs = [f for f in files if str(f.get('url', '')).lower().endswith('.pdf')]
    fl = ''
    if files:
        rows = ''
        for f in files:
            size = f' <span class="muted small">({E(f["size"])})</span>' if f.get('size') else ''
            rows += f'<li><a href="{E(f["url"])}" target="_blank" rel="noopener" download>{E(f["name"])}</a>{size}</li>'
        fl = f'<div class="art-files"><strong>자료 파일</strong><ul>{rows}</ul></div>'
    acts = ''
    if pdfs:
        size = f' ({E(pdfs[0]["size"])})' if pdfs[0].get('size') else ''
        acts += f'<a class="btn" href="#viewer">PDF 바로 보기</a><a class="btn ghost" href="{E(pdfs[0]["url"])}" download>내려받기{size}</a>'
    elif files:
        acts += f'<a class="btn" href="{E(files[0]["url"])}" target="_blank" rel="noopener" download>내려받기</a>'
    if a.get('url'):
        acts += f'<a class="btn ghost" href="{E(a["url"])}" target="_blank" rel="noopener">원문 · 외부 주소</a>'
    cover = ''   # 사무국 결정(2026-11-03): 아카이브에 표지 그림을 쓰지 않음
    viewer = ''
    if pdfs:
        f = pdfs[0]
        viewer = (f'<section class="sec" id="viewer" style="padding-top:0"><div class="wrap"><div class="row" style="margin-bottom:12px"><h2 style="font-size:24px">본문 보기</h2>'
                  f'<a class="more" href="{E(f["url"])}" target="_blank" rel="noopener">새 창에서 열기</a></div>'
                  f'<iframe class="pdf-frame" src="{E(f["url"])}#view=FitH" title="{E(a["title"])} PDF" loading="lazy"></iframe>'
                  f'<p class="note" style="margin-top:10px">휴대전화에서는 첫 장만 보일 수 있습니다. 그럴 때는 내려받기를 눌러 주세요.</p></div></section>')
    others = [o for o in ARCHIVE if o['id'] != a['id'] and o.get('cat') == a.get('cat')]
    others_html = ''
    if others:
        rr = ''
        for o in others[:5]:
            h, ext = arch_href(o)
            rr += f'<a class="li" href="{E(h)}"{ext}><span><span class="m">{E(o.get("org", ""))}{(" · " + E(o["author"])) if o.get("author") else ""}</span><br><span class="t">{E(o["title"])}</span></span><span class="d">{E(o.get("date", ""))}</span></a>'
        others_html = f'<div class="list">{rr}</div>'
    meta = arch_meta(a) + ((' · ' + E(a['date'])) if a.get('period') and a.get('date') else '')
    article = f'<article class="art">{html_body(a["body"])}</article>' if a.get('body') else ''
    body = crumb(('archive.html', '아카이브'), (f'archive-{a.get("cat", "")}.html', cat), (None, a['title'])) + f'''
<section class="hero" style="padding-top:40px;padding-bottom:40px"><div class="wrap"><div class="arch-hero">
{cover}
<div class="arch-info"><span class="eyebrow">아카이브 · {E(cat)}</span><h1 style="font-size:clamp(26px,3.6vw,38px)">{E(a["title"])}</h1>
<p class="muted">{meta}</p>
<div class="acts">{acts}</div></div>
</div></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
{article}
{fl}
</div></section>
{viewer}
<section class="sec alt"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">{E(cat)}의 다른 자료</h2><a class="more" href="archive-{E(a.get("cat", ""))}.html">전체 보기</a></div>
{others_html or '<p class="muted small">다른 자료가 없습니다.</p>'}
</div></section>
'''
    write(f'archive-{a["id"]}.html', f'{a["title"]} · KELI 아카이브', body, desc=(_inner_text(html_body(a['body']))[:150] if a.get('body') else f'{cat} · {a.get("org", "")}'))

def page_news_hub():
    pr = ''.join(pr_row(it, summary=False) for it in PRESS_ALL[:3])
    ev = ''.join(f'<a class="li" href="{ev_href(it)}" data-ev="{it["id"]}"><span><span class="m">{E((it.get("badges") or ["행사"])[0])}</span><br><span class="t">{E(it["title"])}</span></span><span class="d">{E((it.get("start") or "")[:10].replace("-", "."))}</span></a>' for it in FEED_ITEMS[:3])
    nt = ''.join(f'<a class="li" href="notice-{n["id"]}.html"><span><span class="m">{n["cat"]}</span><br><span class="t">{E(n["title"])}</span></span><span class="d">{n["date"]}</span></a>' for n in NOTICES[:3])
    body = crumb((None, '소식')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap"><span class="eyebrow">소식</span><h1>소식.</h1></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">공지사항</h2><a class="more" href="notice.html">전체 보기</a></div><div class="list">{nt}</div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">행사</h2><a class="more" href="events.html">전체 보기</a></div><div class="list" data-events="rows" data-pages="{FEED_IDS}">{ev}</div>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">영상</h2><a class="more" href="videos.html">전체 보기</a></div>
<div class="grid g2 vids" data-videos="hub">{''.join(vid_card(v) for v in (VIDEOS_KELI + VIDEOS_REL)[:2])}</div>
<p class="note" style="margin-top:12px">썸네일을 누르면 이 자리에서 바로 재생됩니다. 출처: 한림대학교 유튜브(@HALLYMNEWS).</p>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">뉴스레터</h2><a class="more" href="newsletter.html">지난 호 보기</a></div>
<form class="form" data-demo="nl" style="padding:24px;gap:12px" novalidate>
<div class="field"><label for="nl-email">KELI 소식을 이메일로 받아 보세요</label><div style="display:flex;gap:8px;flex-wrap:wrap"><input id="nl-email" type="email" placeholder="이메일 주소" required style="flex:1;min-width:200px"><button class="btn" type="submit">구독하기</button></div><span class="msg">이메일 주소를 확인해 주세요.</span></div>
<div class="done"><span>구독 신청이 접수되었습니다. 확인 메일의 링크를 누르면 구독이 완료됩니다. (접수번호 <code></code>)</span></div>
</form>
<div class="row" style="margin:32px 0 16px"><h3 style="font-size:20px">보도자료</h3><a class="more" href="newsletter.html#press">전체 보기</a></div>
<div class="list" data-press="rows" data-pages="{PRESS_IDS}">{pr}</div>
</div></section>
'''
    write('news.html', '소식 · KELI', body)

def notice_files(n):
    fs = n.get('files') or []
    if not fs:
        return ''
    return '<div class="art-files"><strong>첨부파일</strong><ul>' + ''.join(f'<li><a href="{E(f["url"])}" target="_blank" rel="noopener" download>{E(f["name"])}</a>{(" <span class=\"muted small\">(" + E(f["size"]) + ")</span>") if f.get("size") else ""}</li>' for f in fs) + '</ul></div>'

def page_notice():
    rows = ''
    for n in NOTICES:
        link = f'<p style="margin-top:8px"><a class="more" href="{E(n["link"])}">관련 페이지</a></p>' if n.get('link') else ''
        pin = '<span class="badge live" style="margin-right:8px">고정</span>' if n.get('pinned') else ''
        rows += f'<details class="li" id="{n["id"]}" data-key="{_NOTICE_KEY.get(n["cat"], "general")}"><summary><span>{pin}<span class="badge" style="margin-right:8px">{E(n["cat"])}</span><span class="t">{E(n["title"])}</span></span><span class="d">{E(n.get("date", ""))}</span></summary><div class="body art">{html_body(n["body"])}{notice_files(n)}{link}<p style="margin-top:8px"><a class="more" href="notice-{n["id"]}.html">글 페이지로 보기</a></p></div></details>'
        page_notice_detail(n)
    body = crumb(('news.html', '소식'), (None, '공지사항')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap"><span class="eyebrow">공지사항</span><h1>공지사항.</h1><p class="lead">제목을 누르면 본문이 펼쳐집니다.</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:20px">{tabs('ntc', [('general','일반'),('recruit','모집'),('press','보도')])}</div>
<div class="list" data-items="ntc">{rows}</div>
</div></section>
'''
    write('notice.html', '공지사항 · KELI', body)

def page_notice_detail(n):
    others = ''.join(f'<a class="li" href="notice-{o["id"]}.html"><span><span class="m">{E(o["cat"])}</span><br><span class="t">{E(o["title"])}</span></span><span class="d">{E(o.get("date", ""))}</span></a>' for o in NOTICES if o['id'] != n['id'])[:3000]
    link = f'<p><a class="btn ghost sm" href="{E(n["link"])}">관련 페이지</a></p>' if n.get('link') else ''
    body = crumb(('news.html', '소식'), ('notice.html', '공지사항'), (None, n['title'])) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:32px"><div class="wrap narrow" style="max-width:900px;text-align:left">
<span class="eyebrow">공지사항 · {E(n["cat"])}</span><h1 style="font-size:clamp(28px,4vw,40px)">{E(n["title"])}</h1>
<p class="muted">{E(n.get("date", ""))} · KELI 사무국</p>
</div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<article class="art">{html_body(n["body"])}</article>
{notice_files(n)}{link}
</div></section>
<section class="sec alt"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">다른 공지</h2><a class="more" href="notice.html">전체 보기</a></div>
<div class="list">{others}</div>
</div></section>
'''
    write(f'notice-{n["id"]}.html', f'{n["title"]} · KELI 공지사항', body, desc=_inner_text(html_body(n['body']))[:150])

def page_events():
    rows = ''.join(ev_row(it) for it in FEED_ITEMS)
    upcoming = [it for it in FEED_ITEMS if ev_status(it)[0] != 'ended']
    body = crumb(('news.html', '소식'), (None, '행사')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap"><span class="eyebrow">행사</span><h1>국제 심포지엄, 데모데이, 매칭데이.</h1><p class="lead">예정된 행사가 등록되면 가장 위에 보이고, 참가 신청을 바로 할 수 있습니다.</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="empty" style="margin-bottom:28px" data-ev-empty{"" if not upcoming else " hidden"}>지금 예정된 행사가 없습니다. 지난 행사는 아래에서 볼 수 있습니다.</div>
<div class="list" data-events="list" data-pages="{FEED_IDS}">{rows}</div>
<p class="note" style="margin-top:16px">{FEED_NOTE} 원문은 각 행사 페이지의 "원문 보기"로 열 수 있습니다.</p>
</div></section>
'''
    write('events.html', '행사 · KELI', body)

def page_feed_event(it):
    k, t = ev_status(it)
    posted = it.get('posted') or (it.get('start') or '')[:10].replace('-', '.')
    files = ''.join(f'<a class="li" href="{f["url"]}" target="_blank" rel="noopener"><span><span class="badge" style="margin-right:8px">파일</span><span class="t">{E(f["name"])}</span></span><span class="d">내려받기</span></a>' for f in it.get('files', []))
    others = ''.join(f'<a class="li" href="{ev_href(o)}"><span><span class="t">{E(o["title"])}</span></span><span class="d">{E((o.get("start") or "")[:10].replace("-", "."))}</span></a>' for o in FEED_ITEMS if o['id'] != it['id'])[:4000]
    closed = k == 'ended'
    dis = ' disabled' if closed else ''
    body_html = restyle(it.get('body_html'), 'event') or f'<div class="art"><p class="art-lead">{E(it.get("summary") or "")}</p></div>'
    body = crumb(('news.html', '소식'), ('events.html', '행사'), (None, it['title'])) + f'''
<section class="hero" style="padding-top:40px;padding-bottom:40px"><div class="wrap">
<span class="eyebrow">{E((it.get("badges") or ["행사"])[0])}</span>
<h1>{E(it['title'])}</h1>
<div class="chips" style="justify-content:center"><span class="chip">{E(it.get('when') or '')}</span><span class="chip">{E(it.get('place') or '')}</span>{ev_badge(it)}</div>
</div></section>
<section class="sec" style="padding-top:16px"><div class="wrap narrow" style="max-width:900px">
{('<figure class="cover"><img src="' + it["thumb"] + '" alt="' + E(it["title"]) + ' 대표 사진"></figure>') if it.get('thumb') else ''}
<dl class="kv"><dt>게시일</dt><dd>{E(posted)}</dd><dt>일시</dt><dd>{E(it.get('when') or '')}</dd><dt>장소</dt><dd>{E(it.get('place') or '')}</dd><dt>출처</dt><dd>AI교육확산센터 소식 · <a href="{it['url']}" target="_blank" rel="noopener">원문 보기</a></dd></dl>
{body_html}
{('<div class="head" style="margin-top:40px"><h2>첨부파일.</h2></div><div class="list">' + files + '</div>') if files else ''}
</div></section>
<section class="sec alt"><div class="wrap narrow" style="max-width:900px">
<div class="head"><h2>참가 신청.</h2><p class="lead">{'이 행사는 접수가 마감되었습니다. 다음 행사에서는 같은 양식으로 신청합니다.' if closed else '아래 양식으로 신청하면 접수번호와 확인 메일을 받습니다.'}</p></div>
<form class="form" data-demo="evt" novalidate>
<div class="field"><label for="e-type">참가 대상</label><select id="e-type"{dis}><option>교원·교육관계자</option><option>기업·기관</option><option>정부·공공</option><option>학생</option></select></div>
<div class="grid g2" style="gap:16px">
<div class="field"><label for="e-name">성명</label><input id="e-name" type="text"{dis} placeholder="국문"></div>
<div class="field"><label for="e-org">소속</label><input id="e-org" type="text"{dis} placeholder="기관명"></div>
<div class="field"><label for="e-email">이메일</label><input id="e-email" type="email"{dis} placeholder="1인 1신청 · 중복 신청은 자동으로 막힙니다"></div>
<div class="field"><label for="e-tel">연락처</label><input id="e-tel" type="tel"{dis}></div>
</div>
<div class="field"><label>관심 분야</label><div class="chips"><span class="chip">AI 코스웨어</span><span class="chip">학습분석·교육 데이터</span><span class="chip">대학 행정·학생지원 AI</span><span class="chip">전공 특화 LLM</span><span class="chip">국제협력·공동연구</span></div></div>
<div>{'<button class="btn disabled" type="button" disabled>접수 마감</button>' if closed else '<button class="btn" type="submit">참가 신청</button>'}</div>
<div class="done"><span>신청이 접수되었습니다. 접수번호 <code></code> · 확인 메일을 보내 드립니다. (시연 화면)</span></div>
</form>
</div></section>
<section class="sec"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">다른 행사</h2><a class="more" href="events.html">전체 보기</a></div><div class="list">{others}</div>
</div></section>
'''
    write(ev_href(it), f'{it["title"]} · KELI', body)

def page_newsletter():
    rows = ''.join(pr_row(it) for it in PRESS_ALL)
    body = crumb(('news.html', '소식'), (None, '뉴스레터')) + f'''
<section class="hero" style="padding-top:48px"><div class="wrap"><span class="eyebrow">뉴스레터</span><h1>KELI 소식을<br>이메일로 받아 보세요.</h1><p class="lead">새 서비스, 행사, 보도자료를 발행호마다 정리해 보냅니다. 언제든 해지할 수 있습니다.</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<form class="form" data-demo="nl" novalidate>
<div class="grid g2" style="gap:16px">
<div class="field"><label for="n-email">이메일</label><input id="n-email" type="email" required placeholder="name@univ.ac.kr"><span class="msg">이메일 주소를 확인해 주세요.</span></div>
<div class="field"><label for="n-org">소속 (선택)</label><input id="n-org" type="text" placeholder="기관명"></div>
</div>
<label class="chk"><input type="checkbox" id="n-agree" required><span>뉴스레터 수신과 개인정보 수집·이용에 동의합니다. <a href="privacy.html">개인정보처리방침</a></span></label>
<div><button class="btn" type="submit">구독하기</button></div>
<div class="done"><span>구독 신청이 접수되었습니다. 확인 메일의 링크를 누르면 구독이 완료됩니다. (접수번호 <code></code>)</span></div>
</form>
</div></section>
<section class="sec alt" id="press"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">보도자료</h2><span class="muted small">{len(PRESS_ALL)}건</span></div>
<div class="list" data-press="list" data-pages="{PRESS_IDS}">{rows}</div>
<p class="note" style="margin-top:16px">{PRESS_NOTE}</p>
</div></section>
'''
    write('newsletter.html', '뉴스레터 · KELI', body)

def page_press(it):
    files = ''.join(f'<a class="li" href="{f["url"]}" target="_blank" rel="noopener"><span><span class="badge" style="margin-right:8px">파일</span><span class="t">{E(f["name"])}</span></span><span class="d">내려받기</span></a>' for f in it.get('files', []))
    others = ''.join(f'<a class="li" href="{pr_href(o)}"><span><span class="t">{E(o["title"])}</span></span><span class="d">{E(o.get("date") or "")}</span></a>' for o in PRESS_ITEMS if o['id'] != it['id'])
    body = crumb(('news.html', '소식'), ('newsletter.html#press', '보도자료'), (None, it['title'])) + f'''
<section class="hero" style="padding-top:40px;padding-bottom:32px"><div class="wrap">
<span class="eyebrow">보도자료{(" · " + E(it["category"])) if it.get("category") else ""}</span>
<h1 style="font-size:clamp(28px,3.4vw,44px)">{E(it['title'])}</h1>
<p class="lead">{E(it.get('date') or '')} · 한림대학교 커뮤니케이션팀 · <a href="{it['url']}" target="_blank" rel="noopener">원문 보기</a></p>
</div></section>
<section class="sec" style="padding-top:8px"><div class="wrap narrow" style="max-width:900px">
{restyle(it.get('body_html'), 'press') or '<div class="art"><p class="art-lead">' + E(it.get('summary') or '') + '</p></div>'}
{('<div class="head" style="margin-top:40px"><h2>첨부파일.</h2></div><div class="list">' + files + '</div>') if files else ''}
<p class="note" style="margin-top:28px">출처: 한림대학교 홍보 보도자료. 본문과 사진의 저작권은 한림대학교에 있습니다.</p>
</div></section>
<section class="sec alt"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">다른 보도자료</h2><a class="more" href="newsletter.html#press">전체 보기</a></div><div class="list">{others}</div>
</div></section>
'''
    write(pr_href(it), f'{it["title"]} · KELI', body)

def page_demos():
    secs = ''
    for cat in DEMO_CATS:
        items = [d for d in DEMO_ITEMS if d.get('category') == cat]
        secs += f'''
<section class="sec" style="padding-top:0"><div class="wrap">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:26px">{E(cat)}</h2><span class="muted small">{len(items)}건</span></div>
<div class="grid g3 vids">{''.join(demo_card(d) for d in items)}</div>
</div></section>'''
    body = crumb(('services.html', '마켓플레이스'), (None, '전체 데모 영상')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap"><span class="eyebrow">HAI Ecosystems · 데모 영상</span><h1>서비스를 먼저<br>영상으로 봅니다.</h1><p class="lead">한림 AI 교육 포털에 등록된 서비스별 데모 영상을 한곳에 모았습니다. 썸네일을 누르면 이 자리에서 바로 재생됩니다.</p>
<div class="acts"><a class="btn ghost" href="services.html">서비스 목록</a><a class="btn ghost" href="{PORTAL_DEMOS}" target="_blank" rel="noopener">한림 AI 교육 포털</a><a class="more" href="join.html#inquiry">도입 문의</a></div></div></section>{secs}
<section class="sec" style="padding-top:0"><div class="wrap"><p class="note">{DEMO_NOTE} 영상 저작권은 한림대학교에 있습니다.</p></div></section>
'''
    write('demos.html', '전체 데모 영상 · KELI', body)

def page_videos():
    keli = ''.join(vid_card(v) for v in VIDEOS_KELI) or '<div class="empty">아직 KELI 영상이 없습니다.</div>'
    rel = ''.join(vid_card(v) for v in VIDEOS_REL)
    body = crumb(('news.html', '소식'), (None, '영상')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:40px"><div class="wrap"><span class="eyebrow">영상</span><h1>KELI를 영상으로.</h1><p class="lead">국제 심포지엄 실시간 녹화부터 HAI Ecosystems 소개까지, 한림대학교 유튜브의 KELI 영상을 이 자리에서 바로 봅니다.</p></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">KELI 영상</h2><span class="muted small">{len(VIDEOS_KELI)}건</span></div>
<div class="grid g2 vids" data-videos="keli">{keli}</div>
</div></section>
<section class="sec alt"><div class="wrap narrow" style="max-width:900px">
<div class="row" style="margin-bottom:16px"><h2 style="font-size:28px">관련 영상</h2><span class="muted small">HAI Ecosystems · 에듀테크 소프트랩 {len(VIDEOS_REL)}건</span></div>
<div class="grid g2 vids" data-videos="related">{rel}</div>
<p class="note" style="margin-top:16px">{VIDEO_NOTE} <a href="{VIDEOS.get("source", "https://www.youtube.com/@HALLYMNEWS")}" target="_blank" rel="noopener">채널 바로가기</a></p>
</div></section>
'''
    write('videos.html', '영상 · KELI', body)

def page_search():
    idx = [(f'service-{s["slug"]}.html', s['name'], s['one'] + ' · ' + AREA_LABEL[s['area']]) for s in SERVICES]
    idx += [('about.html', 'KELI 소개', '정의 · 비전 · 구조 · 사무국'), ('services.html', '마켓플레이스', 'HAI Ecosystems 19'), ('curriculum.html', 'AI 융합교육과정', '수업 6단계와 서비스'), ('join.html', '참여·도입', '도입 절차 · 이용 방식 · 참여 기관 · 문의'), ('archive.html', '아카이브', '사례집 · 기술 동향 · 매뉴얼'), ('notice.html', '공지사항', '소식'), ('events.html', '행사', '심포지엄 · 데모데이 · 매칭데이'), ('newsletter.html', '뉴스레터', '구독')]
    idx += [(ev_href(it), it['title'], '행사 · ' + (it.get('when') or '')) for it in FEED_ITEMS]
    idx += [(pr_href(it), it['title'], ('언론 보도 · ' if it.get('src') == 'unn' else '보도자료 · ') + (it.get('date') or '')) for it in PRESS_ALL]
    idx += [('videos.html', v['title'], '영상 · ' + (v.get('published') or v.get('published_text') or '')) for v in VIDEO_ITEMS]
    idx += [(f'demos.html#demo-{d["id"]}', d['name'] + ' 데모 영상' + (' (' + d['audience'] + ')' if d.get('audience') else ''), '데모 영상 · ' + d.get('category', '')) for d in DEMO_ITEMS]
    idx += [(arch_href(a)[0], a['title'], '아카이브 · ' + dict(ARCH_CATS).get(a.get('cat'), '')) for a in ARCHIVE]
    idx += [(f'notice-{n["id"]}.html', n['title'], '공지사항 · ' + n['cat'] + ' · ' + n.get('date', '')) for n in NOTICES]
    rows = ''.join(f'<a class="li" href="{h}" data-q="{E((t + " " + d).lower())}"><span class="t">{E(t)}</span><span class="d">{E(d)}</span></a>' for h, t, d in idx)
    body = crumb((None, '검색')) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:32px"><div class="wrap"><h1>검색.</h1></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow" style="max-width:900px">
<div class="field" style="margin-bottom:24px"><label for="q">검색어</label><input id="q" type="search" placeholder="예) 수학, 진단평가, 참여"><span class="hint"><span id="rc"></span></span></div>
<div class="list" id="results">{rows}</div>
</div></section>
'''
    write('search.html', '검색 · KELI', body)

def page_en():
    svc = ''.join(f'<a class="svc" href="service-{s["slug"]}.html"><div class="body"><span class="k">{dict((a[0],a[2]) for a in AREAS)[s["area"]]}</span><strong>{E(s["name"])}</strong><p>{E(s["one"])}</p></div></a>' for s in SERVICES)
    body = f'''
<section class="hero"><div class="wrap"><span class="eyebrow">K-University AI EdTech and Learning Initiative</span><h1 class="en">A higher-education AI ecosystem,<br>built together by universities.</h1><p class="lead">KELI is a national-level shared platform. Hallym University develops and classroom-tests AI education services (HAI Ecosystems) and provides them to universities and institutions in Korea and abroad.</p><div class="acts"><a class="btn" href="#contact">Contact us</a><a class="more" href="index.html">한국어</a></div></div></section>
<section class="sec alt"><div class="wrap"><div class="head"><h2>What KELI offers.</h2></div><div class="grid g3">
<div class="card"><h3>HAI Ecosystems</h3><p>19 AI education services developed and classroom-tested by Hallym University, from course design to assessment and analytics.</p></div>
<div class="card"><h3>KELI Marketplace</h3><p>An online portal to browse services and request adoption.</p></div>
<div class="card"><h3>Pilot and training support</h3><p>One-semester pilot operation, faculty training and an effectiveness report.</p></div>
</div></div></section>
<section class="sec"><div class="wrap"><div class="head"><h2>How to join.</h2><p class="lead">Every participation starts with the KELI Secretariat. First step: one course, one service, one semester.</p></div>
<div class="steps"><div class="step"><span class="n">1</span><strong>Inquiry</strong><p>Email the secretariat with your institution, service of interest and target course.</p></div><div class="step"><span class="n">2</span><strong>Consultation & demo</strong><p>Free demonstration and guidance.</p></div><div class="step"><span class="n">3</span><strong>Pilot</strong><p>One-semester trial in a real course.</p></div><div class="step"><span class="n">4</span><strong>Adoption</strong><p>Subscription or license agreed with the secretariat.</p></div></div>
<div class="grid g3" style="margin-top:32px"><div class="card"><h3>Universities</h3><p>Join as a KELI consortium member.</p></div><div class="card"><h3>Overseas universities & institutions</h3><p>Localised licence and international programmes.</p></div><div class="card"><h3>EdTech companies</h3><p>Marketplace listing and co-development.</p></div></div>
</div></section>
<section class="sec alt"><div class="wrap"><div class="head"><h2>Services.</h2></div><div class="grid g4">{svc}</div></div></section>
<section class="sec" id="contact"><div class="wrap"><div class="cta"><h2>Contact the KELI Secretariat.</h2><p class="lead">Center for AI Education Advancement, Hallym University</p><div class="acts"><span class="copy">{EMAIL} <button type="button" class="btn sm ghost" data-copy="{EMAIL}">Copy</button></span></div><p class="note">Please start your subject line with [Service inquiry]. 1 Hallymdaehak-gil, Chuncheon, Gangwon State, 24252, Republic of Korea. Follow us on <a href="{INSTA}" target="_blank" rel="noopener">Instagram @hallym_keli</a>.</p></div></div></section>
'''
    html_ = doc('en.html', 'KELI — English', body, desc='KELI is a national-level shared AI platform for higher education led by Hallym University.')
    open(os.path.join(OUT, 'en.html'), 'w', encoding='utf-8').write(nb(html_.replace('<html lang="ko">', '<html lang="en">'), en=True))

def page_policy(fname, title, en):
    body = crumb((None, title)) + f'''
<section class="hero" style="padding-top:48px;padding-bottom:32px"><div class="wrap"><span class="eyebrow">{en}</span><h1>{title}.</h1></div></section>
<section class="sec" style="padding-top:0"><div class="wrap narrow"><div class="card"><p>현행 keliedu.org/keli에 게시된 {title} 원문을 그대로 이관합니다. 도입 문의·행사 참가·뉴스레터 구독 폼으로 수집하는 항목(기관명·성명·이메일·연락처)과 보존 기간을 반영해 개정합니다.</p><p class="note">원문 확정 전 임시 안내입니다. 문의: {EMAIL}</p></div></div></section>
'''
    write(fname, f'{title} · KELI', body)

# ------------------------------------------------------------------ 실행
def main():
    # OUT은 git 저장소. 루트의 *.html만 지우고 다시 만들며, assets/·media/·content/·cert/ 등은 보존한다.
    for f in os.listdir(OUT):
        if f.endswith('.html'): os.remove(os.path.join(OUT, f))
    os.makedirs(os.path.join(OUT, 'assets', 'img', 'services'), exist_ok=True)
    write_stats_files()
    open(os.path.join(OUT, 'assets', 'site.css'), 'w', encoding='utf-8').write(CSS)
    open(os.path.join(OUT, 'assets', 'site.js'), 'w', encoding='utf-8').write(JS)
    shutil.copy(os.path.join(BASE, 'gen', 'admin.js'), os.path.join(OUT, 'assets', 'admin.js'))
    if os.path.isdir(IMG_SRC):   # 서비스 화면 이미지 원본이 있는 작업 환경에서만 복사(저장소에는 이미 들어 있음)
        for s in SERVICES:
            if s['img']:
                src = os.path.join(IMG_SRC, 'services' if s['img'].endswith('.jpg') else '', s['img'])
                if os.path.exists(src): shutil.copy(src, os.path.join(OUT, 'assets', 'img', 'services', s['img']))
    _leaf = '/mnt/user-data/attachments/b9bbc33e-fd1f-5ee5-a71b-6bf5eaebf405/74220322-image.png'
    if os.path.exists(_leaf):
        from PIL import Image
        im = Image.open(_leaf).convert('RGB')
        im.thumbnail((1600, 1600)); im.save(os.path.join(OUT, 'assets', 'img', 'keli-leaflet.jpg'), quality=82, optimize=True)
    elif not os.path.exists(os.path.join(OUT, 'assets', 'img', 'keli-leaflet.jpg')):
        print('warning: assets/img/keli-leaflet.jpg missing')

    open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(nb(doc('index.html', 'KELI 플랫폼', page_index())))
    if not os.environ.get('CI'):
        open(os.path.join(OUT, 'index.artifact.html'), 'w', encoding='utf-8').write(nb(doc('index.html', 'KELI 플랫폼', page_index(), skeleton=False)))
    page_about(); page_services()
    for s in SERVICES: page_service(s)
    page_curriculum(); page_join(); page_archive(); page_news_hub(); page_notice(); page_events()
    for it in FEED_ITEMS: page_feed_event(it)
    for it in PRESS_ITEMS: page_press(it)
    page_videos(); page_demos()
    page_newsletter(); page_search(); page_en()
    page_policy('privacy.html', '개인정보처리방침', 'Privacy'); page_policy('terms.html', '이용약관', 'Terms')
    page_admin()
    print('pages', len([f for f in os.listdir(OUT) if f.endswith('.html')]))

if __name__ == '__main__':
    main()
