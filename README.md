# KANT AX Projects

KANT AX 트랙에서 학습한 Python, 프론트엔드, 백엔드, 데이터 분석 및 AI 개발 과제를 정리한 저장소입니다.

단순한 기능 구현을 넘어 **설계 → 구현 → 검증 → 개선** 과정을 기록합니다.

## Tech Stack

### Languages
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-336791?style=for-the-badge)

### Frontend
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![Jinja2](https://img.shields.io/badge/Jinja2-B41717?style=for-the-badge&logo=jinja&logoColor=white)

### Backend & Database
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-3FCF8E?style=for-the-badge&logo=supabase&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)

### Data & AI
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikitlearn&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)

### Tools & Infrastructure
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)
![VS Code](https://img.shields.io/badge/VS_Code-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white)
![uv](https://img.shields.io/badge/uv-DE5FE9?style=for-the-badge&logo=uv&logoColor=white)

## 프로젝트 목록

| 프로젝트 | 기술 스택 | 주요 구현 |
|---|---|---|
| [Board API Assignment](./board_api_assignment/) | FastAPI, Python, PostgreSQL, SQLAlchemy, JWT, Jinja2 | DDD 기반 게시판 API 및 웹 UI |
| [React / Next Application](./react_next_application/) | React, Next.js, TypeScript | 프론트엔드 응용 과제 |
| [TypeScript Advanced](./typescript_advanced/) | TypeScript | 타입스크립트 심화 학습 |
| [Shopping Mall Backend](./shopingmall_backend/) | Python, Supabase, SQL | 회원·상품·주문 CRUD 및 RLS |
| [Todo List](./todolist/) | HTML, CSS, JavaScript | 할 일 관리 및 localStorage |
| [Sparta Community Mockup](./sparta_mockup/) | HTML, CSS | 커뮤니티 정적 웹페이지 |
| [Python Final Project](./python_final_project/) | Python | 객체지향 도서 관리 시스템 |
| [Machine Learning Assignment](./final_assignment/) | Python, Jupyter | 당뇨병 데이터 분석 및 머신러닝 |

---

## 주요 프로젝트 — FastAPI Board API

**DDD 4계층 아키텍처를 적용한 게시판 백엔드와 Jinja2 웹 UI**

### 기술 구성

- **Backend:** FastAPI, Python
- **Database:** PostgreSQL, SQLAlchemy
- **Authentication:** JWT
- **Frontend:** Jinja2, HTML, CSS, JavaScript
- **Design:** AsyncTicket 프로젝트의 CSS 디자인 재사용
- **Architecture:** Domain / Application / Infrastructure / Presentation

### 주요 기능

- 회원가입 및 로그인·로그아웃
- JWT 기반 인증과 역할별 접근 제어
- 게시판 생성 및 조회
- 회원·비회원 게시글 CRUD
- 게시글 댓글 CRUD
- 관리자·회원·비회원 권한 분리
- 예외 처리 및 입력값 검증

### Jinja2 웹 UI

AsyncTicket 프로젝트의 디자인 요소를 재사용하여 게시판을 브라우저에서 확인할 수 있도록 구성했습니다.

- 게시판 목록
- 게시글 목록
- 게시글 상세 및 댓글 조회
- 게시글 검색 및 빈 결과 화면
- 모바일 반응형 레이아웃

**구현 상태:** 로컬 환경에서 조회 UI와 실제 PostgreSQL 데이터 연결을 검증했습니다. 로그인·글쓰기·수정·삭제 웹 UI는 후속 구현 범위입니다.

**배포** · [게시판 열기](https://43.202.122.94/boards)

---

## 개발 과정에서 중요하게 다룬 내용

### 1. 아키텍처 설계

DDD 계층별 책임을 분리하고, 의존성 주입을 통해 API 요청과 비즈니스 로직을 연결했습니다.

### 2. 데이터베이스 무결성

ORM 모델과 실제 PostgreSQL 스키마를 비교하고, 기존 데이터를 보존하면서 오류를 점검했습니다.

### 3. 인증과 보안

JWT 비밀키를 환경변수로 관리하고, 회원·비회원의 권한과 비밀번호 검증을 분리했습니다.

### 4. 테스트와 검증

Swagger 기반 API 테스트, 오류·권한 검증, 회귀 테스트 및 Jinja2 화면 확인을 진행했습니다. 로컬에서 확인한 결과와 새 환경에서 아직 검증하지 않은 항목은 구분합니다.

---

## 개발 및 제출 원칙

- API 키, JWT 비밀키, 비밀번호 및 `.env` 파일을 공개하지 않습니다.
- 기존 프로젝트와 데이터베이스를 임의로 변경하지 않습니다.
- 구현 완료와 테스트 완료를 구분하여 기록합니다.
- 팀·튜터 저장소는 허가된 범위에서만 사용합니다.
- GitHub에는 실행에 필요한 소스와 문서를 중심으로 정리합니다.

---

**KANT AX Track | Learning by Building**

기술을 학습하고 실제 프로젝트에 적용하면서, 설계와 검증 과정을 함께 기록합니다.
