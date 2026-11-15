'use client';

import { useActionState } from 'react';
import { updateTodoCompletion } from '../actions';

type TodoCompletionProps = {
  id: number;
  title: string;
  completed: boolean;
};

export function TodoCompletion({ id, title, completed }: TodoCompletionProps) {
  const [message, action, pending] = useActionState(updateTodoCompletion, '');

  return (
    <form action={action}>
      <input type="hidden" name="id" value={id} />
      <input type="hidden" name="completed" value={String(!completed)} />
      <label className="flex items-center gap-2">
        <input type="checkbox" checked={completed} disabled={pending}
          onChange={(event) => event.currentTarget.form?.requestSubmit()} />
        <span>{title} · {pending ? '저장 중' : completed ? '완료' : '진행 중'}</span>
      </label>
      {message && <p role="status">{message}</p>}
    </form>
  );
}
