/* KELI 글 서식(템플릿) — 관리자 편집기의 "서식" 버튼으로 넣는다.
   사이트의 글 스타일(.art-lead · .art-kv · .art-h · .art-ul · .art-sum · .art-fig · .art-quote · .art-note · .art-btn · .tbl)만 쓰므로
   인라인 스타일 없이도 사이트 디자인(Zoom 블루 · 둥근 상자 · 줄바꿈 규칙)이 그대로 적용된다.
   {{ }} 안은 바꿔 쓰는 자리. 제목 · 날짜 · 분류 · 작성자는 글 머리글에 자동으로 붙으므로 본문에 다시 쓰지 않는다. */
window.KELI_TEMPLATES = [
  { id: 'event', group: '소식·공지', name: '행사 안내', desc: '일시·장소·대상·신청이 있는 안내문. 심포지엄 · 데모데이 · 세미나 · 설명회',
    html:
'<dl class="art-kv"><dt>일시</dt><dd>{{2026. 12. 10.(수) 14:00–17:00}}</dd><dt>장소</dt><dd>{{한림대학교 일송아트홀 (강원 춘천시 한림대학길 1)}}</dd><dt>대상</dt><dd>{{대학·기관 교직원, 에듀테크 기업 관계자}}</dd><dt>신청</dt><dd><strong>{{12. 5.(금)까지 사전 등록}}</strong> · {{참가비 무료 · 현장 등록 가능}}</dd><dt>문의</dt><dd>KELI 사무국 033-248-3242 / contact@keliedu.org</dd></dl>' +
'<p class="art-lead">{{한 줄로 행사의 취지를 씁니다. 예: 한림대학교가 수업에서 검증한 AI 교육 서비스를 직접 체험하고, 도입을 상담할 수 있는 자리입니다.}}</p>' +
'<p>안녕하십니까. 한림대학교 AI교육혁신원 KELI 사무국입니다.</p>' +
'<p>{{행사 소개 문단. 무엇을 하는 행사인지, 누가 오면 좋은지, 어떤 것을 얻어 갈 수 있는지 서너 문장으로 씁니다.}}</p>' +
'<h2 class="art-h">프로그램</h2>' +
'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>시간</th><th>내용</th><th>진행</th></tr></thead><tbody><tr><td>{{14:00–14:20}}</td><td>{{개회 · KELI 소개}}</td><td>{{KELI 사무국}}</td></tr><tr><td>{{14:20–15:30}}</td><td>{{HAI Ecosystems 시연}}</td><td>{{서비스별 담당}}</td></tr><tr><td>{{15:30–17:00}}</td><td>{{도입 상담 · 네트워킹}}</td><td>{{전체}}</td></tr></tbody></table></div>' +
'<h2 class="art-h">참가 신청</h2>' +
'<p>{{신청 방법을 씁니다. 예: 아래 버튼을 눌러 신청서를 작성해 주세요. 신청 확인 메일은 접수 후 2일 안에 보내 드립니다.}}</p>' +
'<p><a class="art-btn" href="{{https://forms.gle/…}}" target="_blank" rel="noopener">참가 신청서 바로가기</a></p>' +
'<figure class="art-fig"><p class="ph">{{여기에 커서를 두고 위의 "이미지" 버튼으로 사진을 넣은 뒤, 이 안내 글은 지우세요}}</p><figcaption>{{▲ 행사 포스터 (2026. 12.)}}</figcaption></figure>' +
'<div class="art-note">※ 붙임: {{[붙임1] 행사 안내문_20261210.pdf}}<br>· {{일정과 내용은 주최 측 사정에 따라 바뀔 수 있습니다.}}<br>· 문의: KELI 사무국 033-248-3242 / contact@keliedu.org</div>' },

  { id: 'general', group: '소식·공지', name: '일반 안내', desc: '자료 공개 · 서비스 변경 · 운영 안내처럼 날짜·장소가 없는 공지',
    html:
'<p class="art-lead">{{첫 문장에 핵심을 씁니다. 예: HAI Ecosystems 서비스 소개 자료를 공개합니다.}}</p>' +
'<p>안녕하십니까. 한림대학교 AI교육혁신원 KELI 사무국입니다.</p>' +
'<p>{{안내 내용을 두세 문단으로 씁니다. 배경 → 내용 → 활용 방법 순서가 읽기 쉽습니다.}}</p>' +
'<h2 class="art-h">{{주요 내용}}</h2>' +
'<ul class="art-ul"><li>{{첫 번째 항목}}</li><li>{{두 번째 항목}}</li><li>{{세 번째 항목}}</li></ul>' +
'<h2 class="art-h">{{이용 방법}}</h2>' +
'<p>{{어디서 어떻게 보거나 신청하는지 씁니다. 첨부파일이 있으면 "아래 첨부파일을 내려받아 주세요"라고 안내합니다.}}</p>' +
'<div class="art-note">※ 붙임: {{[붙임1] 자료명_20261103.pdf}}<br>· 문의: KELI 사무국 033-248-3242 / contact@keliedu.org</div>' },

  { id: 'recruit', group: '소식·공지', name: '모집 공고', desc: '참여 대학·기업 · 실증 교과목 · 앰배서더 등 모집',
    html:
'<dl class="art-kv"><dt>모집 대상</dt><dd>{{2027학년도 1학기 HAI Ecosystems 실증 수업을 운영할 교과목 담당 교수}}</dd><dt>모집 기간</dt><dd>{{2026. 11. 10.(월) – 11. 28.(금)}}</dd><dt>모집 규모</dt><dd>{{10개 교과목 내외}}</dd><dt>신청 방법</dt><dd>{{신청서 작성 후 이메일 제출}}</dd><dt>문의</dt><dd>KELI 사무국 033-248-3242 / contact@keliedu.org</dd></dl>' +
'<p class="art-lead">{{무엇을 위해 누구를 모집하는지 한 줄로 씁니다.}}</p>' +
'<p>{{모집 배경과 취지를 두세 문장으로 씁니다.}}</p>' +
'<h2 class="art-h">지원 자격</h2>' +
'<ul class="art-ul"><li>{{자격 1}}</li><li>{{자격 2}}</li></ul>' +
'<h2 class="art-h">지원 내용</h2>' +
'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody><tr><td>{{서비스 이용}}</td><td>{{한 학기 무상 이용 · 계정 발급}}</td></tr><tr><td>{{운영 지원}}</td><td>{{사무국 시연 · 매뉴얼 · 교수자 워크숍}}</td></tr><tr><td>{{성과 환류}}</td><td>{{학습 데이터 분석 보고서 제공}}</td></tr></tbody></table></div>' +
'<h2 class="art-h">일정</h2>' +
'<ul class="art-ul"><li>{{접수: 11. 10. – 11. 28.}}</li><li>{{선정 발표: 12. 5.}}</li><li>{{운영: 2027. 3. – 6.}}</li></ul>' +
'<p><a class="art-btn" href="{{https://forms.gle/…}}" target="_blank" rel="noopener">신청서 바로가기</a></p>' +
'<div class="art-note">※ 붙임: {{[붙임1] 모집 공고문_20261110.hwp}}<br>· {{심사 기준과 결과 통보 방법을 씁니다.}}<br>· 문의: KELI 사무국 033-248-3242 / contact@keliedu.org</div>' },

  { id: 'press', group: '소식·공지', name: '보도 요약', desc: '언론 보도를 요약해 올릴 때(전문 전재 금지, 요약 3~5문단 + 원문 링크)',
    html:
'<dl class="art-kv"><dt>매체</dt><dd>{{한국대학신문}}</dd><dt>보도일</dt><dd>{{2026. 10. 20.(화)}}</dd><dt>관련 행사</dt><dd>{{2026 KELI 국제 심포지엄 및 데모데이}}</dd><dt>원문</dt><dd><a href="{{https://원문 주소}}" target="_blank" rel="noopener">기사 원문 보기</a></dd></dl>' +
'<p class="art-lead">{{리드 문단: 기사의 핵심을 한두 문장으로 요약합니다.}}</p>' +
'<p>{{요약 문단 1}}</p><p>{{요약 문단 2}}</p><p>{{요약 문단 3}}</p>' +
'<blockquote class="art-quote">“{{인용할 발언이 있을 때만 씁니다.}}”<cite>— {{이름 · 직위}}</cite></blockquote>' +
'<figure class="art-fig"><p class="ph">{{여기에 커서를 두고 위의 "이미지" 버튼으로 사진을 넣은 뒤, 이 안내 글은 지우세요}}</p><figcaption>{{▲ 사진 설명 (사진: KELI 사무국)}}</figcaption></figure>' +
'<p><a class="art-btn" href="{{https://원문 주소}}" target="_blank" rel="noopener">{{한국대학신문}} 기사 원문 보기</a></p>' +
'<div class="art-note">※ 본 게시물은 {{매체명}} 보도 내용을 요약한 것으로, 전문은 원문 링크에서 확인하실 수 있습니다.<br>· 문의: KELI 사무국 033-248-3242 / contact@keliedu.org</div>' },

  { id: 'archive', group: '아카이브', name: '자료 소개', desc: '보고서 · 매뉴얼 · 가이드북처럼 첨부 자료를 설명하는 글',
    html:
'<div class="art-sum"><span class="k">핵심 요약</span><ul class="art-ul"><li>{{이 자료가 무엇인지 한 줄}}</li><li>{{누가 보면 좋은지 한 줄}}</li><li>{{가장 중요한 결과나 내용 한 줄}}</li></ul></div>' +
'<dl class="art-kv"><dt>발행</dt><dd>{{2026. 10. · KELI 사무국}}</dd><dt>저자</dt><dd>{{이름 (소속)}}</dd><dt>분량</dt><dd>{{48쪽 · PDF}}</dd><dt>대상</dt><dd>{{대학 교수자 · 교육혁신 담당자}}</dd></dl>' +
'<h2 class="art-h">자료 소개</h2>' +
'<p>{{이 자료를 왜 만들었고 무엇을 담았는지 두세 문단으로 씁니다.}}</p>' +
'<h2 class="art-h">구성</h2>' +
'<ol class="art-ol"><li>{{1장 제목}}</li><li>{{2장 제목}}</li><li>{{3장 제목}}</li><li>{{4장 제목}}</li></ol>' +
'<h2 class="art-h">활용 방법</h2>' +
'<ul class="art-ul"><li>{{예: 수업 설계 단계에서 2장의 체크리스트를 사용}}</li><li>{{예: 도입 검토 시 4장의 비교표 참고}}</li></ul>' +
'<div class="art-note">※ 자료 파일은 아래 "자료 파일"에서 내려받을 수 있습니다.<br>· {{인용 시 출처: KELI 사무국(2026). 자료명.}}<br>· 문의: KELI 사무국 033-248-3242 / contact@keliedu.org</div>' },

  { id: 'case', group: '아카이브', name: '실증 사례', desc: 'AI 활용 수업 사례집 한 편. 교과목 · 교수 · 적용 방법 · 결과',
    html:
'<dl class="art-kv"><dt>교과목</dt><dd>{{C 프로그래밍 (전공 기초, 3학점)}}</dd><dt>교수</dt><dd>{{이름 교수 (소속 학과)}}</dd><dt>대학</dt><dd>{{한림대학교}}</dd><dt>학기</dt><dd>{{2026학년도 1학기 · 수강생 {{42}}명}}</dd><dt>적용 서비스</dt><dd>{{HAI-Coder · HAI-Forum}}</dd></dl>' +
'<p class="art-lead">{{이 수업에서 AI 서비스를 어떻게 썼고 무엇이 달라졌는지 한두 문장으로 요약합니다.}}</p>' +
'<h2 class="art-h">수업 개요</h2>' +
'<p>{{수업 목표와 기존 운영 방식, 어려웠던 점을 씁니다.}}</p>' +
'<h2 class="art-h">적용 방법</h2>' +
'<ol class="art-ol"><li><strong>{{설계}}</strong> — {{예: 주차별 실습 문제를 HAI-Coder 문제은행에서 구성}}</li><li><strong>{{수업·상호작용}}</strong> — {{예: HAI-Forum 퀴즈로 매주 이해도 확인}}</li><li><strong>{{실습·학습}}</strong> — {{예: 오답 노트와 학습 경로 추천을 과제에 연결}}</li><li><strong>{{평가·분석}}</strong> — {{예: 학습 대시보드로 위험 학생 조기 상담}}</li></ol>' +
'<h2 class="art-h">결과</h2>' +
'<div class="tbl-wrap"><table class="tbl"><thead><tr><th>항목</th><th>적용 전</th><th>적용 후</th></tr></thead><tbody><tr><td>{{과제 제출률}}</td><td>{{78%}}</td><td>{{93%}}</td></tr><tr><td>{{중간고사 평균}}</td><td>{{71점}}</td><td>{{79점}}</td></tr><tr><td>{{수업 만족도}}</td><td>{{4.1}}</td><td>{{4.6}}</td></tr></tbody></table></div>' +
'<blockquote class="art-quote">“{{교수자 한마디. 예: 학생마다 다른 오류를 AI가 먼저 짚어 주니 수업 시간에 설명보다 토론에 집중할 수 있었습니다.}}”<cite>— {{이름 교수}}</cite></blockquote>' +
'<figure class="art-fig"><p class="ph">{{여기에 커서를 두고 위의 "이미지" 버튼으로 사진을 넣은 뒤, 이 안내 글은 지우세요}}</p><figcaption>{{▲ 수업 장면 또는 서비스 화면}}</figcaption></figure>' +
'<div class="art-note">※ 자료 파일(사례집 PDF)은 아래 "자료 파일"에서 내려받을 수 있습니다.<br>· {{수업 운영 기간: 2026. 3. – 6.}}<br>· 문의: KELI 사무국 033-248-3242 / contact@keliedu.org</div>' }
];
