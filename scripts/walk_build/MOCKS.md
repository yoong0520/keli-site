# 체험관 「직접 해 보기」 — 직접 만든 화면(목업)으로 바꾸는 작업

- 엔진: `gen/gen2.py` 의 `WALK_JS`(미션·힌트·별점) + `gen/mocks.py`(화면 HTML, 공통 CSS `MK_CSS`, 요소 속성 규칙은 파일 맨 위 설명)
- 서비스마다 `gen/mocks.py` 에 `_slug()` 함수를 만들고 `MOCKS['slug']` 에 넣는다. 단계는 5개, 각 단계 `dict(title, text, do, ui, img)`.
- 화면 글자는 매뉴얼·소개자료 캡처(`media/walk/<slug>/N.jpg`)를 읽어 옮긴다(`tesseract -l kor+eng`). 캡처에 없는 결과물(생성 초안 등)은 「체험용 예시」로 표시한다.
- 확인: `python3 gen/gen2.py` 뒤 체험관에서 미션 5개가 모두 풀리는지, 휴대폰 너비에서 깨지지 않는지 본다.

## 진행

- [x] hai-docs
- [x] hai-tutor · hai-mate · hai-gpt · hai-mathtutor
- [ ] lxp · hai-forum · hai-fist · hai-lens · hai-way · hai-research
- [ ] hai-bdpi · hai-check · hai-lrs · hai-sync · hai-security · hai-pbl · hai-epilearn · hai-medlearn-x
