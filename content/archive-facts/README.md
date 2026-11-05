# 아카이브 본문 사실 파일

- `<글 id>.json`: 첨부 PDF에서 뽑은 사실(수업 정보 · 운영 · 결과 · 교수자 소감 / 보고서 목적 · 자료 · 결과 · 시사점 · 구성). 문서에 없는 것은 비워 둔다.
- 본문은 `python3 gen/curate_cases.py content/archive-facts && python3 gen/compose_archive.py content/archive-facts` 로 다시 조립한다(사례 → "실증 사례" 서식, 보고서 → "자료 소개" 서식). 조립 결과는 content/archive.json 의 body 에 들어간다.
- 관리자 화면에서 본문을 직접 고친 뒤에는 이 조립을 다시 돌리지 않는다(덮어쓰므로). 다시 돌리려면 고친 내용을 JSON 에 먼저 반영한다.
- o63(데이터로 소통하기): 첨부 PDF 가 표지만 이은정 교수 문서이고 3쪽부터는 C 프로그래밍(김진환) 문서와 동일해 본문을 채우지 못함. 원본 PDF 교체 뒤 사실 파일을 채울 것.
