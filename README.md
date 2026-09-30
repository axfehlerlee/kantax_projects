# KANT AX Projects

KANT AX 트랙에서 진행한 학습 과제와 프로젝트를 폴더별로 정리한 저장소입니다.

## 프로젝트 목록

| 폴더 | 주요 내용 | 실행 방법 |
| --- | --- | --- |
| [`python_final_project`](./python_final_project/) | Python 클래스와 모듈을 활용한 도서 관리 시스템 | Python 3.13 이상에서 `python3 main.py` |
| [`final_assignment`](./final_assignment/) | 당뇨병 데이터를 사용한 머신러닝 최종 과제 | Jupyter에서 노트북 실행 |
| [`shopingmall_backend`](./shopingmall_backend/) | Supabase 기반 회원·상품·주문 CRUD와 RLS 정책 | 환경변수 설정 후 Jupyter에서 노트북 실행 |
| [`sparta_mockup`](./sparta_mockup/) | HTML·CSS로 구현한 스파르타 커뮤니티 정적 목업 | `커뮤니티.html`을 브라우저 또는 Live Server로 실행 |

## Python 도서 관리 시스템

경로: [`python_final_project`](./python_final_project/)

- `main.py`: 메뉴 기반 프로그램 실행 진입점
- `library_system/base_book.py`: 공통 도서 클래스
- `library_system/specialized_books.py`: 도서 유형별 클래스
- `utils/help.py`: 입력과 실행 보조 기능
- `pyproject.toml`, `uv.lock`: Python 버전과 프로젝트 환경 정보

```bash
cd python_final_project
python3 main.py
```

도서 등록·조회·검색·대여·반납·종료 흐름을 점검한 프로젝트입니다.

## 머신러닝 최종 과제

경로: [`final_assignment`](./final_assignment/)

- `머신러닝_최종과제_AX_jungeun.ipynb`: 분석과 모델 학습 노트북
- `diabetes.csv`: 노트북에서 사용하는 데이터

노트북과 CSV 파일을 같은 폴더에 둔 상태에서 Jupyter로 실행합니다.
현재 원본 노트북의 기대 CSV 체크섬과 동봉된 CSV의 체크섬이 달라,
해당 검증 셀에서 실행이 중단될 수 있습니다. 과제 데이터 확인이 필요하며
전체 노트북 실행 완료 상태는 확인되지 않았습니다.

## Shopping Mall Backend

경로: [`shopingmall_backend`](./shopingmall_backend/)

- `users.ipynb`: 회원 정보 CRUD
- `products.ipynb`: 상품 CRUD
- `orders.ipynb`: 주문 CRUD
- `policy.sql`: 주문 테이블의 Supabase RLS 정책
- `supabase_client.py`: 공통 Supabase 클라이언트 생성
- `supabase-schema-5조백앤드.png`: 테이블 관계도
- `.env.example`: 로컬 환경변수 예시

```bash
cd shopingmall_backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env`에는 Supabase Project URL과 publishable key를 입력해야 합니다.
실제 `.env`, 로그인 정보, secret 및 `service_role` 키는 저장소에 포함하지 않습니다.
Supabase 실제 연결과 전체 CRUD 실행 검증은 아직 필요합니다.

자세한 설정은 [`shopingmall_backend/README.md`](./shopingmall_backend/README.md)를 확인하세요.

## Sparta Community Mockup

경로: [`sparta_mockup`](./sparta_mockup/)

- `커뮤니티.html`: 커뮤니티 화면의 정적 HTML
- `style.css`: 레이아웃과 화면 스타일
- `images/`: 로고, 아이콘, 예시 이미지

JavaScript 동작이나 서버 기능이 없는 정적 목업입니다. `커뮤니티.html`을 직접 열거나
VS Code Live Server로 실행할 수 있습니다. Pretendard 글꼴은 외부 CDN을 사용하므로
동일한 글꼴 표시에는 인터넷 연결이 필요합니다.

## 공개 저장소 주의사항

- API 키, 비밀번호, 개인 데이터와 `.env` 파일을 커밋하지 않습니다.
- Jupyter Notebook을 공유하기 전에 개인정보가 포함된 실행 결과를 제거합니다.
- 정적 목업의 화면 확인과 백엔드의 실제 연결·CRUD 검증은 별도로 수행합니다.
