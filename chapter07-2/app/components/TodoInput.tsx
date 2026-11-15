'use client';

import { useActionState } from 'react';
import { addTodo } from '../actions';

export function TodoInput() {
  const [message, formAction, isPending] = useActionState(addTodo, '');

  return (
    <form action={formAction} className="space-y-2">
      <label htmlFor="todo-title" className="block font-medium">새 할 일</label>
      <div className="flex gap-2">
        <input id="todo-title" name="title" required maxLength={200}
          placeholder="할 일을 입력하세요" className="min-w-0 flex-1 rounded border px-3 py-2" />
        <button type="submit" disabled={isPending}
          className="rounded bg-blue-700 px-4 py-2 text-white disabled:opacity-50">
          {isPending ? '저장 중' : '추가'}
        </button>
      </div>
      {message && <p role="status">{message}</p>}
    </form>
  );
}
