# Next.js 할 일 앱 · 7-2 / 7-3

**배포** · [할 일 앱 열기](https://kant-supabase-todo.vercel.app/)

Next.js App Router와 Supabase로 만든 개인 할 일 앱입니다. 할 일 추가·조회·완료 상태 변경·삭제, 이메일 회원가입과 로그인·로그아웃을 지원합니다.

## 로컬 실행

1. Supabase SQL Editor에서 [마이그레이션](./supabase/migrations/)을 파일명 순서대로 적용합니다.
2. 이 폴더에 `.env.local`을 만들고 Supabase 프로젝트의 URL과 Publishable key를 입력합니다.

   ```dotenv
   NEXT_PUBLIC_SUPABASE_URL=https://YOUR_PROJECT.supabase.co
   NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
   ```

3. 이메일 인증을 사용한다면 Supabase Authentication의 Redirect URLs에 `http://localhost:3000/auth/callback`을 등록합니다.
4. Node.js 22 환경에서 아래 명령을 실행하고 [로컬 앱](http://localhost:3000)을 엽니다.

   ```bash
   npm ci
   npm run dev
   ```

## 동작과 검증

- Next.js Proxy가 세션 쿠키를 동기화하고 비로그인 사용자를 로그인 화면으로 이동시킵니다.
- Server Actions가 할 일을 변경하고, PostgreSQL RLS는 로그인한 사용자에게 본인의 행만 조회·추가·수정·삭제할 수 있게 합니다.
- 회원가입 후 이메일 인증과 로그인, 할 일 CRUD, 새로고침 후 상태 유지, 두 계정 간 할 일 조회 분리를 실습에서 확인했습니다.
