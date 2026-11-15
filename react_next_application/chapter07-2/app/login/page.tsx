'use client';

import { useActionState } from 'react';
import { login, signup } from '../actions';

export default function LoginPage() {
  const [message, action, pending] = useActionState(login, '');
  const [signupMessage, signupAction, signingUp] = useActionState(signup, '');
  return (
    <main className="mx-auto max-w-md space-y-4 p-6">
      <h1 className="text-2xl font-bold">할 일 앱 로그인</h1>
      <form action={action} className="space-y-3">
        <label className="block">이메일
          <input name="email" type="email" autoComplete="username" required
            className="block w-full rounded border px-3 py-2" />
        </label>
        <label className="block">비밀번호
          <input name="password" type="password" autoComplete="current-password" required
            className="block w-full rounded border px-3 py-2" />
        </label>
        <button disabled={pending || signingUp} className="rounded bg-blue-700 px-4 py-2 text-white">
          {pending ? '로그인 중' : '로그인'}
        </button>
        <button type="submit" formAction={signupAction} disabled={pending || signingUp}
          className="ml-2 rounded border px-4 py-2">
          {signingUp ? '가입 중' : '회원가입'}
        </button>
        {signupMessage && <p role="status">{signupMessage}</p>}
        {message && <p role="status">{message}</p>}
      </form>
    </main>
  );
}
