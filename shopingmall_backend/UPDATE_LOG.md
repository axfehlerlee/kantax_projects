# Update Log

## 2026-10-01 02:12 KST

- 사용자 요청: Supabase 연결 준비 및 GitHub 과제 공유 대응
- 변경 파일: `.env.example`, `.gitignore`, `requirements.txt`, `supabase_client.py`, `README.md`, `UPDATE_LOG.md`, `users.ipynb`, `products.ipynb`, `orders.ipynb`
- 변경 내용: publishable key 기반 공통 클라이언트와 노트북 연결 셀 추가
- 검증: Notebook 3개의 JSON 구조 정상, 출력 셀 0개, `supabase_client.py` Python 문법 정상, 실제 비밀값 미포함 확인
- 추가 검증: 프로젝트 전용 `.venv`에 `supabase 2.31.0`과 `python-dotenv 1.2.3` 설치, 연결 모듈 import 성공
- 남은 작업: 로컬 `.env`에 실제 프로젝트 값 입력, 로그인 및 CRUD 실행 검증
