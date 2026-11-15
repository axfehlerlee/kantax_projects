'use client';

import { useActionState } from 'react';
import { deleteTodo } from '../actions';

export function TodoDelete({ id, title }: { id: number; title: string }) {
  const [message, action, pending] = useActionState(deleteTodo, '');

  return (
    <form action={action} onSubmit={(event) => {
      if (!window.confirm(`「${title}」을 삭제할까요?`)) event.preventDefault();
    }}>
      <input type="hidden" name="id" value={id} />
      <button type="submit" disabled={pending} className="text-sm text-red-600 underline">
        {pending ? '삭제 중' : '삭제'}
      </button>
      {message && <p role="status">{message}</p>}
    </form>
  );
}
