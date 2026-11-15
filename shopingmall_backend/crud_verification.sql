\set ON_ERROR_STOP on
BEGIN;

CREATE SCHEMA crud_verification;
SET LOCAL search_path TO crud_verification;
CREATE TABLE test_auth_users (id uuid PRIMARY KEY);
CREATE TABLE user_details (
    id uuid PRIMARY KEY REFERENCES test_auth_users(id),
    type text NOT NULL,
    zipcode text NOT NULL,
    deleted_at timestamptz
);
CREATE TABLE product (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    price integer NOT NULL,
    seller_id uuid REFERENCES test_auth_users(id),
    deleted_at timestamptz
);
CREATE TABLE orders (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_no text UNIQUE NOT NULL,
    user_id uuid REFERENCES test_auth_users(id),
    total_price integer NOT NULL,
    deleted_at timestamptz
);
CREATE TABLE order_items (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id uuid REFERENCES orders(id),
    product_id uuid REFERENCES product(id),
    quantity integer NOT NULL
);

INSERT INTO test_auth_users VALUES
    ('00000000-0000-4000-8000-000000000001'),
    ('00000000-0000-4000-8000-000000000002');

\echo 'CREATE | 테스트 회원, 상품, 주문 추가'
INSERT INTO user_details (id, type, zipcode)
VALUES ('00000000-0000-4000-8000-000000000001', 'BUYER', '00001')
RETURNING type, zipcode;
INSERT INTO product (name, price, seller_id)
VALUES ('테스트 노트', 12000, '00000000-0000-4000-8000-000000000002')
RETURNING id AS product_id \gset
SELECT name, price FROM product WHERE id = :'product_id';
INSERT INTO orders (order_no, user_id, total_price)
VALUES ('TEST-001', '00000000-0000-4000-8000-000000000001', 24000)
RETURNING id AS order_id \gset
INSERT INTO order_items (order_id, product_id, quantity)
VALUES (:'order_id', :'product_id', 2) RETURNING quantity;

\echo 'READ | 회원·상품과 연결된 주문 조회'
SELECT o.order_no, u.type, p.name, i.quantity, o.total_price
FROM orders o
JOIN user_details u ON u.id = o.user_id
JOIN order_items i ON i.order_id = o.id
JOIN product p ON p.id = i.product_id
WHERE o.id = :'order_id';

\echo 'UPDATE | 회원 우편번호, 상품 가격, 주문 금액 변경'
UPDATE user_details SET zipcode = '00002'
WHERE id = '00000000-0000-4000-8000-000000000001' RETURNING zipcode;
UPDATE product SET price = 15000 WHERE id = :'product_id' RETURNING name, price;
UPDATE orders SET total_price = 30000 WHERE id = :'order_id' RETURNING order_no, total_price;

\echo 'DELETE | 소프트 삭제 후 활성 목록에서 제외'
UPDATE orders SET deleted_at = now() WHERE id = :'order_id';
UPDATE product SET deleted_at = now() WHERE id = :'product_id';
UPDATE user_details SET deleted_at = now() WHERE id = '00000000-0000-4000-8000-000000000001';
SELECT
    (SELECT count(*) FROM user_details WHERE deleted_at IS NULL) AS active_users,
    (SELECT count(*) FROM product WHERE deleted_at IS NULL) AS active_products,
    (SELECT count(*) FROM orders WHERE deleted_at IS NULL) AS active_orders;
ROLLBACK;
SELECT to_regnamespace('crud_verification') IS NULL AS rolled_back;
