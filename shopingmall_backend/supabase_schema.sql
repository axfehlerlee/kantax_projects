begin;

create table public.user_details (
    id uuid primary key references auth.users(id),
    type text not null check (type in ('BUYER', 'SELLER')),
    cellphone text not null,
    zipcode text not null,
    address text not null,
    address_sub text not null,
    created_at timestamptz not null default now(),
    modified_at timestamptz,
    deleted_at timestamptz
);

create table public.product (
    id uuid primary key default gen_random_uuid(),
    name text not null,
    price integer not null check (price >= 0),
    seller_id uuid not null default auth.uid() references auth.users(id),
    created_at timestamptz not null default now(),
    modified_at timestamptz,
    deleted_at timestamptz
);

create table public.orders (
    id uuid primary key default gen_random_uuid(),
    order_no text not null unique,
    order_name text not null,
    order_email text not null,
    order_phone text not null,
    receiver_name text not null,
    receiver_phone text not null,
    zipcode text not null,
    address text not null,
    address_sub text not null,
    deliver_memo text,
    total_price integer not null check (total_price >= 0),
    order_status text not null default 'PENDING',
    user_id uuid not null default auth.uid() references auth.users(id),
    created_at timestamptz not null default now(),
    modified_at timestamptz,
    deleted_at timestamptz
);

create table public.order_items (
    id uuid primary key default gen_random_uuid(),
    order_id uuid not null references public.orders(id),
    product_id uuid not null references public.product(id),
    item_name text not null,
    item_price integer not null check (item_price >= 0),
    quantity integer not null check (quantity > 0),
    created_at timestamptz not null default now(),
    modified_at timestamptz,
    deleted_at timestamptz
);

create index on public.product (seller_id);
create index on public.orders (user_id);
create index on public.order_items (order_id);
create index on public.order_items (product_id);

alter table public.user_details enable row level security;
alter table public.product enable row level security;
alter table public.orders enable row level security;
alter table public.order_items enable row level security;

revoke all on public.user_details, public.product, public.orders, public.order_items from public, anon, authenticated;
grant select, insert, update on public.user_details, public.product, public.orders, public.order_items to authenticated;

create policy profile_owner on public.user_details for all to authenticated
    using (id = (select auth.uid()))
    with check (id = (select auth.uid()));

create policy product_read on public.product for select to authenticated
    using (deleted_at is null or seller_id = (select auth.uid()));
create policy seller_insert on public.product for insert to authenticated
    with check (
        seller_id = (select auth.uid())
        and exists (select 1 from public.user_details where id = (select auth.uid()) and type = 'SELLER' and deleted_at is null)
    );
create policy seller_update on public.product for update to authenticated
    using (seller_id = (select auth.uid()))
    with check (seller_id = (select auth.uid()));

create policy orders_owner on public.orders for all to authenticated
    using (user_id = (select auth.uid()))
    with check (
        user_id = (select auth.uid())
        and exists (select 1 from public.user_details where id = (select auth.uid()) and type = 'BUYER' and deleted_at is null)
    );

create policy items_order_owner on public.order_items for all to authenticated
    using (exists (select 1 from public.orders where orders.id = order_items.order_id and orders.user_id = (select auth.uid())))
    with check (exists (select 1 from public.orders where orders.id = order_items.order_id and orders.user_id = (select auth.uid()) and orders.deleted_at is null));

commit;

select tablename, rowsecurity from pg_tables
where schemaname = 'public' and tablename in ('user_details', 'product', 'orders', 'order_items')
order by tablename;
