begin;

alter table public.todos
  add column if not exists user_id uuid references auth.users (id);

alter table public.todos alter column user_id set default auth.uid();

create index if not exists todos_user_id_idx on public.todos (user_id);

grant select, insert on public.todos to authenticated;

drop policy if exists todos_select_own on public.todos;
create policy todos_select_own on public.todos for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists todos_insert_own on public.todos;
create policy todos_insert_own on public.todos for insert to authenticated
  with check ((select auth.uid()) = user_id);

commit;
