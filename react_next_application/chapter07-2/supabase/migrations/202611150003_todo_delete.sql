begin;

grant delete on public.todos to authenticated;

drop policy if exists todos_delete_own on public.todos;
create policy todos_delete_own on public.todos for delete to authenticated
  using ((select auth.uid()) = user_id);

commit;
