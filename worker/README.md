# KELI 관리자 서버 설치 안내 (Cloudflare, 약 20분)

이 폴더의 `keli-admin.js` 한 파일을 Cloudflare 에 올리면 관리자 화면(https://keli-aied.org/admin.html)이 이렇게 바뀝니다.

- 직원은 GitHub 토큰 없이 아이디·비밀번호로 들어옵니다. 계정은 관리자가 "사이트 설정 → 사용자" 메뉴에서 만듭니다.
- 글 저장(커밋)과 배포는 사무국이 서버에 한 번 넣어 둔 GitHub 토큰으로 서버가 대신 처리합니다(직원에게 토큰을 나눠 줄 일이 없음).
- 파일 창고(R2)를 붙이면 첨부파일 용량 제한(100MB)이 없어집니다. 50MB 조각으로 나눠 올리므로 1GB 영상도 됩니다.

비용: Workers 무료(하루 10만 요청) · R2 무료 한도(저장 10GB, 내려받기 무제한) 안이면 0원. 단, R2 는 **결제 수단(카드) 등록이 있어야 켜집니다**. 카드 등록 전에는 1~4단계만 하면 로그인 서버로 쓸 수 있고(첨부는 종전처럼 GitHub 100MB), 나중에 5단계만 추가하면 됩니다.

## 1. Cloudflare 가입
1. https://dash.cloudflare.com/sign-up 에서 사무국 메일(contact@keliedu.org)로 가입 → 메일 인증.
2. 왼쪽 메뉴 "Workers & Pages"(또는 "Compute (Workers)") → 처음이면 워커 하위 도메인 이름을 정하라고 함 → `keli` 처럼 짧게. (서버 주소가 `https://keli-admin.keli.workers.dev` 꼴이 됩니다)

## 2. 워커 만들고 코드 붙여 넣기
1. Workers & Pages → "Create" → "Create Worker"(Hello World) → 이름 `keli-admin` → "Deploy".
2. "Edit code"(코드 편집) → 왼쪽 파일 `worker.js` 내용을 모두 지우고, 이 폴더의 `keli-admin.js` 내용을 통째로 붙여 넣기 → 오른쪽 위 "Deploy".
   - 코드 보기: https://github.com/yoong0520/keli-site/blob/main/worker/keli-admin.js → "Raw" → 전체 선택 → 복사.

## 3. 변수·비밀 넣기 (워커 → Settings → Variables and Secrets → "+ Add")
| 이름 | 종류 | 값 |
|---|---|---|
| `REPO` | Text | `yoong0520/keli-site` |
| `ALLOW_ORIGINS` | Text | `https://keli-aied.org,https://www.keli-aied.org` |
| `GITHUB_TOKEN` | **Secret** | GitHub Fine-grained 토큰(저장소 keli-site, Contents·Actions 읽고 쓰기). 관리자 사용법 문서의 "열쇠 만드는 순서"대로 하나 새로 만들어 넣기(이름: KELI 서버) |
| `SESSION_SECRET` | **Secret** | 아무 긴 무작위 문자열(예: 비밀번호 생성기로 40자). 로그인 유지용 서명 열쇠 |
| `SETUP_KEY` | **Secret** | 첫 관리자 계정을 만들 때 한 번 쓸 비밀 문자열(예: 20자). 만든 뒤에는 지워도 됨 |

저장 뒤 "Deploy"가 다시 필요하다고 나오면 누릅니다.

## 4. 계정 저장소 연결 (둘 중 하나 — R2 가 아직 없으면 KV)
- KV(카드 없이 가능): 왼쪽 메뉴 "Storage & Databases → KV" → "Create a namespace" → 이름 `keli-auth` → 만들기. 다시 워커 → Settings → Bindings → "+ Add" → "KV namespace" → Variable name `KV`, Namespace `keli-auth` → Deploy.
- R2 를 쓸 거면 5단계의 `FILES` 바인딩만 있어도 됩니다(계정 목록도 R2 에 저장).

## 5. 파일 창고 R2 (첨부 용량 제한 해제 — 카드 등록 필요)
1. 왼쪽 메뉴 "R2 Object Storage" → "Enable R2"(결제 수단 등록) → "Create bucket" → 이름 `keli-files` → 위치 Automatic(또는 Asia-Pacific) → Create.
2. 워커 → Settings → Bindings → "+ Add" → "R2 bucket" → Variable name `FILES`, Bucket `keli-files` → Deploy.

## 6. 관리자 화면에 서버 주소 알리기 + 첫 관리자 만들기
1. 워커 화면 위쪽의 주소(예: `https://keli-admin.keli.workers.dev`)를 복사.
2. https://keli-aied.org/admin.html → 아래 "관리자 서버 주소 바꾸기(이 브라우저에만)" 펼치기 → 주소 붙여 넣고 "적용" → 화면이 아이디·비밀번호 칸으로 바뀜.
3. 그 아래 "첫 관리자 계정 만들기"에 아이디(예: keli) · 이름 · 비밀번호(8자 이상) · 설정 열쇠(3단계의 `SETUP_KEY`) → "관리자 만들기" → 바로 로그인됨.
4. 사이트 설정 → "관리자 서버 주소"에 같은 주소를 넣고 "저장하고 게시" → 다음 배포부터 모든 사람의 관리자 화면이 아이디·비밀번호 로그인으로 열립니다.
5. 사이트 설정 → "사용자(직원 계정)"에서 직원 계정을 만들어 아이디·비밀번호를 각자에게 알려 줍니다(권한: 편집자 = 글 쓰기·고치기, 관리자 = 사용자 관리까지).

## 확인 · 문제 해결
- 서버 주소를 브라우저에서 열면 `{"ok":true,"service":"KELI admin server","setup":true}` 가 보여야 합니다(`setup:true` = 아직 관리자 없음).
- "관리자 서버에 연결하지 못했습니다": 주소 오타, 또는 3단계 `ALLOW_ORIGINS` 에 `https://keli-aied.org` 가 없음.
- "서버에 GITHUB_TOKEN 비밀 변수가 없습니다": 3단계 비밀 변수 누락 → 넣고 Deploy.
- "저장소 바인딩(FILES 또는 KV)이 없습니다": 4단계 또는 5단계 바인딩 누락.
- 로그인 5회 실패 → 15분 잠금. 비밀번호를 잊으면 관리자가 "비밀번호 재설정".
- 토큰을 바꿨다면 `GITHUB_TOKEN` 값만 교체 → Deploy. 직원 쪽은 아무것도 안 해도 됩니다.
- 되돌리기: 사이트 설정에서 서버 주소를 비우고 저장하면 GitHub 토큰 로그인으로 돌아갑니다.

## 파일 구성
- `keli-admin.js` 워커 본체(이 파일만 Cloudflare 에 올림)
- `test_worker.mjs` Node 로 돌리는 검사(`node worker/test_worker.mjs`), `serve 8787` 로 로컬 서버 흉내
- 관리자 화면 쪽 코드는 `gen/admin.js`(서버가 있으면 자동으로 아이디·비밀번호 모드)
