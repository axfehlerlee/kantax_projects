# KANT FastAPI 게시판

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)
![uv](https://img.shields.io/badge/uv-DE5FE9?style=flat-square&logo=uv&logoColor=white)
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=flat-square&logo=jinja&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white)
![bcrypt](https://img.shields.io/badge/bcrypt-555555?style=flat-square)
![Uvicorn](https://img.shields.io/badge/Uvicorn-4051B5?style=flat-square)
![asyncpg](https://img.shields.io/badge/asyncpg-4169E1?style=flat-square)
![python-dotenv](https://img.shields.io/badge/python-dotenv-555555?style=flat-square)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-663399?style=flat-square&logo=css&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)

회원·비회원 게시글/댓글 CRUD와 관리자 게시판 관리 기능을 갖춘 과제입니다.
Python 3.13+, FastAPI, PostgreSQL, SQLAlchemy Async, JWT, bcrypt, uv, Jinja2를 사용합니다.

## 실행 방법

```bash
git clone https://github.com/axfehlerlee/kantax_projects.git
cd kantax_projects/board_api_assignment
uv sync --locked
# 기존 .env의 DATABASE_URL, JWT_SECRET_KEY 설정을 확인한 뒤 실행
uv run uvicorn main:app --app-dir src --reload --env-file .env
```

- 게시판: http://127.0.0.1:8000/boards
- 관리자 화면: http://127.0.0.1:8000/manage/boards
- Swagger: http://127.0.0.1:8000/docs
- 서버 확인: http://127.0.0.1:8000/health

`.env`에 `DATABASE_URL`(PostgreSQL asyncpg 연결 URL), `JWT_SECRET_KEY`(UTF-8 최소 64바이트)를 설정합니다. 기존 키는 재사용하고 `.env`는 Git에서 제외하며 권한을 `600`으로 유지합니다. `SQL_ECHO=False`를 사용합니다. 비밀키가 없거나 짧으면 서버 시작이 실패합니다.

PostgreSQL과 `users`, `token_blacklist`, `boards`, `posts`, `comments` 테이블이 먼저 준비돼 있어야 합니다. 서버가 테이블을 자동 생성하거나 기존 스키마를 마이그레이션하지는 않습니다. 기존 과제 DB와 `qna`, `freetalk` 데이터를 그대로 사용하며 초기화하지 않습니다. 새 환경은 별도의 빈 DB에 ORM 모델을 등록한 뒤 `Base.metadata.create_all()`로 준비해야 합니다.

## 로그인 및 관리자 계정

상단 **로그인**에서 이메일과 비밀번호를 입력합니다. 회원가입으로 만든 계정은 `USER`이며 관리자 승격 API는 없습니다.

| 항목 | 내용 |
| --- | --- |
| 관리자 아이디 | `boardtest001@example.com` — 기존 과제에서 ADMIN으로 지정한 계정 |
| 관리자 비밀번호 | **미확인 · 기존에 설정한 비밀번호 사용** |

비밀번호 원문은 코드나 DB 해시에서 복원할 수 없어 임의의 값을 기재하지 않았습니다. 위 계정은 기존 과제 DB용이며 새 DB에 자동 생성되지 않습니다.

Swagger에서는 `/v1/auth/login` 응답의 `access_token`을 **Authorize**에 입력합니다. 웹 UI 로그인은 현재 탭에 JWT를 저장하고 로그아웃 시 서버에서 토큰을 무효화합니다.

## 권한 범위

| 기능 | 비회원 | 일반 회원 | 관리자 |
| --- | --- | --- | --- |
| 게시판·글·댓글 조회 | `ALL` 권한만 | `ALL`·`USER` 권한 | 모든 권한 등급 |
| 글·댓글 작성 | `ALL`에서 이름·비밀번호 입력 | 허용된 게시판에 회원으로 작성 | 모든 활성 게시판에 작성 |
| 글·댓글 수정·삭제 | 허용된 게시판에서 비회원 작성 비밀번호 확인 | 허용된 게시판에서 본인 글·댓글 버튼 표시 | 타인·비회원 글·댓글도 관리, 비회원 비밀번호 불필요 |
| 게시판 생성·설정 수정·삭제 | 불가 | 불가 | 가능 |
| 계정 화면 | 숨김 | 본인 비밀번호 변경 | 본인 비밀번호 변경 |

게시판별로 목록·상세·글쓰기·댓글 조회·댓글 작성 권한을 각각 설정합니다. UI는 권한 밖의 메뉴·게시판·버튼을 숨기며, 계정·관리 화면의 직접 접근도 제한합니다. **서버가 실제 권한과 비회원 비밀번호를 별도로 검사합니다.** 일반 회원도 기존 API 정책상 비회원 비밀번호를 알면 비회원 콘텐츠를 관리할 수 있으나 UI에서는 해당 버튼을 숨깁니다.

게시판 삭제는 소프트 삭제이며 삭제된 ID는 재사용할 수 없습니다. 관리자도 삭제 복구·관리자 승격·회원 탈퇴 기능은 제공받지 않습니다. 현재 비밀번호 변경 API는 기존 비밀번호를 검증하며 JWT 기반 본인 ID 검사는 향후 보완 항목입니다.

## 화면과 코드 구조

- 게시판 선택 → 게시글 목록 → 상세·댓글. 목록 맨 아래 중앙의 **글쓰기**로 작성합니다.
- 검색 6종과 페이지 크기 선택을 지원합니다. 비회원 신규 비밀번호는 6자 이상이며 bcrypt 입력은 UTF-8 72바이트 이하입니다.
- `src/user`, `src/auth`, `src/board`: `presentation → application → domain`, `infrastructure`의 DDD 4계층.
- `src/wiring`: 의존성 연결 / `src/shared`: DB·공통 예외 / `templates`, `static`: Jinja2 UI.
- 디자인은 AsyncTicket의 색상·버튼·테이블·반응형 CSS를 재사용했습니다. 원본 프로젝트는 수정하지 않았습니다.

## 검증과 남은 항목

분리된 메모리 SQLite 환경에서 API 회귀 42개, 이후 권한 관련 API 19개 및 UI 이벤트·권한 표시 검사가 통과했습니다. 테스트 수는 별도 실행 결과로 중복을 포함합니다. 임시 테스트는 저장소에 포함돼 있지 않습니다. 전체 브라우저 E2E와 실제 PostgreSQL 쓰기 회귀는 미검증입니다.

기존 DB에는 ORM과 다른 일부 VARCHAR 길이·인덱스·FK 삭제 정책과 미사용 `boards.is_active`, `posts.category`가 남아 있습니다. 현재 HTTP 입력 범위에서는 길이 충돌이 없지만 제출·배포 환경의 스키마 정합성은 별도 확인이 필요합니다. 마이그레이션·저장소 테스트·CI 및 로그인 시도 제한은 향후 개선 사항입니다.
