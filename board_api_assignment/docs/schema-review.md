# DB 스키마 검증 · 2026-11-15

기존 PostgreSQL은 READ ONLY로 조회했고 변경하지 않았습니다. 데이터 없는 DDL을 별도 PostgreSQL 17의 테스트 스키마에 복제해 ORM 신규 스키마와 같은 회귀 10개를 통과했습니다. 테스트 중 스키마 덤프의 search_path 초기화를 보정했으며 애플리케이션 수정은 없었습니다.

## 확인된 차이

| 항목 | ORM | 기존 DB | 판단 |
| --- | --- | --- | --- |
| boards.id / posts.board_id | VARCHAR(30) | VARCHAR(40) | 현재 ID 상한 30에서는 충돌 없음. 축소 불필요 |
| boards.board_name | VARCHAR(100) | VARCHAR(65) | API 상한 50은 통과. 서비스를 직접 호출해 66~100자를 저장하면 위험 |
| boards.edit_role | VARCHAR(20) | VARCHAR(30) | 역할 문자열에는 영향 없음 |
| boards.is_active | 매핑 없음 | NOT NULL DEFAULT true | INSERT 누락을 기본값이 처리. 활성 판정은 deleted_at |
| posts.category | 매핑 없음 | nullable VARCHAR(60) | API 미사용, 기존 값 보존 |
| posts.author_id / (id, deleted_at) 인덱스 | 선언됨 | 없음 | 정확성보다 조회 성능 위험 |
| posts.board_id FK 삭제 정책 | NO ACTION | CASCADE | 소프트 삭제에는 영향 없음. 하드 삭제 정책은 추후 통일 |
| DB 기본값 | Python default 중심 | 권한·페이지 크기·작성자 이름 일부 기본값 추가 | ORM 저장에서 값을 제공하며 기존 기본값 유지 가능 |

users.email은 UNIQUE 제약 명칭이 아니라 UNIQUE 인덱스로 중복을 막습니다. 기본키·FK·NULL 허용 여부·시각 컬럼을 확인했고 누락된 ORM 컬럼은 없습니다. created_at·modified_at·deleted_at 및 token_blacklist.expired_at은 TIMESTAMP WITH TIME ZONE입니다. ID의 nextval 기본값은 PostgreSQL SERIAL 자동 증가이며 오류 차이로 보지 않습니다. 시각 생성·수정은 ORM Python default/onupdate이며 DB 자동 갱신 트리거를 전제하지 않습니다.

## 최소 마이그레이션 초안 — 실행하지 않음

즉시 기존 데이터 삭제나 테이블 재생성은 필요하지 않습니다. 우선 검토할 변경은 안전한 길이 확장과 누락 인덱스입니다. 적용 시 운영 잠금·트랜잭션 정책을 따로 검토합니다.

```sql
ALTER TABLE public.boards ALTER COLUMN board_name TYPE VARCHAR(100);
CREATE INDEX IF NOT EXISTS ix_posts_author_id ON public.posts (author_id);
CREATE INDEX IF NOT EXISTS ix_posts_id_deleted_at ON public.posts (id, deleted_at);
```

FK 삭제 정책 변경, 레거시 컬럼 제거·길이 축소는 이번 최소안에서 제외합니다. Alembic 등 마이그레이션 도구는 현재 없습니다.

## 테이블별 실제 구조

### users

| 컬럼 | 실제 타입 | NULL 허용 | DB 기본값 |
| --- | --- | --- | --- |
| id | UUID | False | 없음 |
| email | VARCHAR(255) | False | 없음 |
| name | VARCHAR(50) | False | 없음 |
| password_hash | VARCHAR(255) | False | 없음 |
| role | VARCHAR(20) | False | 없음 |
| resign | BOOLEAN | False | 없음 |
| created_at | TIMESTAMP WITH TIME ZONE | False | 없음 |
| modified_at | TIMESTAMP WITH TIME ZONE | True | 없음 |
| deleted_at | TIMESTAMP WITH TIME ZONE | True | 없음 |

- PK: id
- INDEX: ix_users_email (email), unique=True

### token_blacklist

| 컬럼 | 실제 타입 | NULL 허용 | DB 기본값 |
| --- | --- | --- | --- |
| jti | VARCHAR(36) | False | 없음 |
| expired_at | TIMESTAMP WITH TIME ZONE | False | 없음 |

- PK: jti
- INDEX: ix_token_blacklist_expired_at (expired_at), unique=False
- INDEX: ix_token_blacklist_jti (jti), unique=False

### boards

| 컬럼 | 실제 타입 | NULL 허용 | DB 기본값 |
| --- | --- | --- | --- |
| id | VARCHAR(40) | False | 없음 |
| board_name | VARCHAR(65) | False | 없음 |
| edit_role | VARCHAR(30) | False | 없음 |
| is_active | BOOLEAN | False | true |
| created_at | TIMESTAMP WITH TIME ZONE | False | 없음 |
| modified_at | TIMESTAMP WITH TIME ZONE | True | 없음 |
| deleted_at | TIMESTAMP WITH TIME ZONE | True | 없음 |
| page_size | INTEGER | False | 20 |
| view_role | VARCHAR(20) | False | 'ALL'::character varying |
| list_role | VARCHAR(20) | False | 'ALL'::character varying |
| comment_list_role | VARCHAR(20) | False | 'ALL'::character varying |
| comment_edit_role | VARCHAR(20) | False | 'ALL'::character varying |

- PK: id

### posts

| 컬럼 | 실제 타입 | NULL 허용 | DB 기본값 |
| --- | --- | --- | --- |
| id | BIGINT | False | nextval('posts_id_seq'::regclass) |
| category | VARCHAR(60) | True | 없음 |
| title | VARCHAR(255) | False | 없음 |
| content | TEXT | False | 없음 |
| created_at | TIMESTAMP WITH TIME ZONE | False | 없음 |
| modified_at | TIMESTAMP WITH TIME ZONE | True | 없음 |
| deleted_at | TIMESTAMP WITH TIME ZONE | True | 없음 |
| board_id | VARCHAR(40) | False | 없음 |
| author_name | VARCHAR(50) | False | '익명'::character varying |
| author_id | UUID | True | 없음 |
| guest_password | VARCHAR(65) | True | 없음 |

- PK: id
- FK: author_id → users(id), {'ondelete': 'SET NULL'}
- FK: board_id → boards(id), {'ondelete': 'CASCADE'}
- INDEX: ix_posts_board_id (board_id), unique=False
- INDEX: ix_posts_category (category), unique=False

### comments

| 컬럼 | 실제 타입 | NULL 허용 | DB 기본값 |
| --- | --- | --- | --- |
| id | BIGINT | False | nextval('comments_id_seq'::regclass) |
| post_id | BIGINT | False | 없음 |
| content | TEXT | False | 없음 |
| author_name | VARCHAR(50) | False | 없음 |
| author_id | UUID | True | 없음 |
| guest_password | VARCHAR(65) | True | 없음 |
| created_at | TIMESTAMP WITH TIME ZONE | False | 없음 |
| modified_at | TIMESTAMP WITH TIME ZONE | True | 없음 |
| deleted_at | TIMESTAMP WITH TIME ZONE | True | 없음 |

- PK: id
- FK: author_id → users(id), {'ondelete': 'SET NULL'}
- FK: post_id → posts(id), {'ondelete': 'NO ACTION'}
- INDEX: ix_comments_post_id_deleted_at (post_id, deleted_at), unique=False
