create policy "orders policy select"
on orders
for select
to authenticated
using (
    exists (
        select 1
        from user_details
        where user_details.id = auth.uid()
          and user_details.type = 'BUYER'
    )
);

create policy "orders policy insert"
on orders
for insert
to authenticated
with check (
    exists (
        select 1
        from user_details
        where user_details.id = auth.uid()
          and user_details.type = 'BUYER'
    )
);

create policy "orders policy update"
on orders
for update
to authenticated
using (
    exists (
        select 1
        from user_details
        where user_details.id = auth.uid()
          and user_details.type = 'BUYER'
    )
)
with check (
    exists (
        select 1
        from user_details
        where user_details.id = auth.uid()
          and user_details.type = 'BUYER'
    )
);