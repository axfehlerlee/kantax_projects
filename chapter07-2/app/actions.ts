'use server';

import { revalidatePath } from 'next/cache';
import { redirect } from 'next/navigation';
import { createClient } from '@/utils/supabase/server';

export async function addTodo(_previousMessage: string, formData: FormData) {
  const title = formData.get('title');
  if (typeof title !== 'string' || !title.trim() || title.trim().length > 200) {
    return '할 일을 1~200자로 입력해 주세요.';
  }

  const supabase = await createClient();
  const { error } = await supabase.from('todos').insert({ title: title.trim() });
  if (error) {
    if (error.code === '42501') {
      return '현재 세션에는 할 일을 저장할 권한이 없어요.';
    }
    console.error('할 일 저장 실패:', error.code);
    return '할 일을 저장하지 못했어요.';
  }

  revalidatePath('/');
  return '할 일을 추가했어요.';
}

export async function login(_previousMessage: string, formData: FormData) {
  const email = formData.get('email');
  const password = formData.get('password');
  if (typeof email !== 'string' || typeof password !== 'string' || !email.trim() || !password) {
    return '이메일과 비밀번호를 입력해 주세요.';
  }

  const supabase = await createClient();
  const { error } = await supabase.auth.signInWithPassword({ email: email.trim(), password });
  if (error) return '로그인하지 못했어요. 이메일과 비밀번호를 확인해 주세요.';

  revalidatePath('/');
  redirect('/');
}

export async function logout() {
  const supabase = await createClient();
  const { error } = await supabase.auth.signOut({ scope: 'local' });
  if (error) throw new Error('로그아웃하지 못했어요.');
  revalidatePath('/');
  redirect('/login');
}

export async function updateTodoCompletion(_previousMessage: string, formData: FormData) {
  const id = formData.get('id');
  const completed = formData.get('completed');
  if (typeof id !== 'string' || !/^[1-9]\d*$/.test(id)
      || (completed !== 'true' && completed !== 'false')) {
    return '수정할 할 일 또는 완료 상태가 올바르지 않아요.';
  }

  const supabase = await createClient();
  const { data, error } = await supabase
    .from('todos')
    .update({ is_completed: completed === 'true' })
    .eq('id', id)
    .select('id')
    .maybeSingle();

  if (error || !data) return '완료 상태를 저장하지 못했어요.';
  revalidatePath('/');
  return '';
}

export async function deleteTodo(_previousMessage: string, formData: FormData) {
  const id = formData.get('id');
  if (typeof id !== 'string' || !/^[1-9]\d*$/.test(id)) {
    return '삭제할 할 일이 올바르지 않아요.';
  }

  const supabase = await createClient();
  const { data, error } = await supabase
    .from('todos')
    .delete()
    .eq('id', id)
    .select('id')
    .maybeSingle();

  if (error || !data) return '할 일을 삭제하지 못했어요.';
  revalidatePath('/');
  return '';
}

export async function signup(_previousMessage: string, formData: FormData) {
  const email = formData.get('email');
  const password = formData.get('password');
  if (typeof email !== 'string' || !email.trim()
      || typeof password !== 'string' || password.length < 6) {
    return '이메일과 6자 이상의 비밀번호를 입력해 주세요.';
  }

  const siteUrl = process.env.APP_URL ?? 'http://localhost:3000';
  const supabase = await createClient();
  const { data, error } = await supabase.auth.signUp({
    email: email.trim(),
    password,
    options: { emailRedirectTo: new URL('/auth/callback', siteUrl).toString() },
  });

  if (error) return '회원가입을 완료하지 못했어요. 입력값을 확인하고 다시 시도해 주세요.';
  if (data.session) {
    revalidatePath('/');
    redirect('/');
  }
  return '받은 편지함에 인증 메일이 도착하면, 가입에 사용한 브라우저에서 링크를 열어 주세요.';
}
