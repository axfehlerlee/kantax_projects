import { redirect } from 'next/navigation';
import { logout } from './actions';
import { Suspense } from 'react';
import { TodoCompletion } from './components/TodoCompletion';
import { TodoDelete } from './components/TodoDelete';
import { TodoInput } from './components/TodoInput';
import { createClient } from '@/utils/supabase/server';

async function TodoList() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) redirect('/login');

  const { data, error } = await supabase
    .from('todos')
    .select('id, title, is_completed')
    .order('created_at', { ascending: false });

  if (error) {
    console.error('할 일 목록 조회 실패:', error.code);
    return <p role="alert">할 일 목록을 불러오지 못했어요.</p>;
  }

  return (
    <>
      <p>{user.email}</p>
      <form action={logout}><button type="submit" className="underline">로그아웃</button></form>
      <TodoInput />
      {data.length === 0 && <p>표시할 할 일이 없어요.</p>}
      <ul className="space-y-2">
        {data.map((todo) => (
          <li key={todo.id} className="rounded-lg border p-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <TodoCompletion id={todo.id} title={todo.title} completed={todo.is_completed} />
                <TodoDelete id={todo.id} title={todo.title} />
              </div>
          </li>
        ))}
      </ul>
    </>
  );
}

export default function HomePage() {
  return (
    <main className="mx-auto max-w-lg space-y-4 p-6">
      <h1 className="text-2xl font-bold">할 일 목록</h1>
      <Suspense fallback={<p>할 일을 불러오는 중이에요.</p>}>
        <TodoList />
      </Suspense>
    </main>
  );
}
