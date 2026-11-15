begin;

grant update (is_completed) on public.todos to authenticated;

drop policy if exists todos_update_own on public.todos;
create policy todos_update_own on public.todos for update to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

commit;
