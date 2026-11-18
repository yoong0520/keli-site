# 체험관 「직접 해 보기」 원고

- `spec.py` · `spec2.py`: 서비스별 매뉴얼 쪽 번호, 단계 제목·설명, 화면 잘라낼 위치
- `hot.py`: 단계별 미션 문구(`do`), 눌러야 하는 위치(`hot`, 완성 그림 기준 비율), 입력 예시(`type`), 고르기 미션(`q`)
- `build2.py`: 위 원고와 매뉴얼 쪽 그림(Actions `Manual pages (one-off)` 아티팩트)으로 `media/walk/`와 `content/walkthroughs.json`을 만든다

매뉴얼 쪽 그림은 저장소에 두지 않는다. 다시 만들 때는 Actions에서 `manual-pages` 아티팩트를 내려받아 `build2.py`의 `HI`/`MP` 경로에 풀어 둔다.
