-- 01_generate_order_data.sql
-- Reproducible deterministic data generation:
--   - 20,000 rows in customers
--   - 500,000 rows in orders
-- Idempotent: truncates and re-seeds cleanly when executed.

BEGIN;

SELECT setseed(0.44119538);

TRUNCATE TABLE orders, customers RESTART IDENTITY CASCADE;

INSERT INTO customers (
    customer_id,
    customer_code,
    full_name,
    email,
    phone,
    region,
    segment,
    country,
    loyalty_points,
    is_active,
    created_at
)
SELECT
    g AS customer_id,
    'CUST-' || LPAD(g::TEXT, 6, '0') AS customer_code,
    (ARRAY['Alex', 'Jordan', 'Taylor', 'Morgan', 'Casey', 'Riley', 'Sam', 'Jamie', 'Avery', 'Quinn'])[1 + (g % 10)]
        || ' '
        || (ARRAY['Smith', 'Patel', 'Chen', 'Garcia', 'Williams', 'Brown', 'Singh', 'Miller', 'Wilson', 'Lopez'])[1 + ((g / 10)::INT % 10)]
        || ' ' || g::TEXT AS full_name,
    'customer' || g::TEXT || '@tuninglab-demo.example' AS email,
    '+1-555-' || LPAD(((100 + (g % 900)))::TEXT, 3, '0') || '-' || LPAD((1000 + (g % 9000))::TEXT, 4, '0') AS phone,
    (ARRAY['NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL'])[1 + (g % 5)] AS region,
    CASE
        WHEN random() < 0.55 THEN 'RETAIL'
        WHEN random() < 0.80 THEN 'WHOLESALE'
        WHEN random() < 0.94 THEN 'ENTERPRISE'
        ELSE 'VIP'
    END AS segment,
    (ARRAY['Canada', 'United States', 'United Kingdom', 'Germany', 'India'])[1 + (g % 5)] AS country,
    (random() * 5000)::INT AS loyalty_points,
    (random() > 0.05) AS is_active,
    TIMESTAMPTZ '2022-01-01 00:00:00+00' + (random() * INTERVAL '1095 days') AS created_at
FROM generate_series(1, 20000) AS g;

SELECT setval(pg_get_serial_sequence('customers', 'customer_id'), COALESCE((SELECT MAX(customer_id) FROM customers), 1));

INSERT INTO orders (
    order_id,
    customer_id,
    order_status,
    order_date,
    total_amount,
    shipping_region,
    payment_method,
    priority_flag,
    notes
)
SELECT
    g AS order_id,
    1 + floor(random() * 20000)::INT AS customer_id,
    CASE
        WHEN r_status < 0.65 THEN 'DELIVERED'
        WHEN r_status < 0.80 THEN 'SHIPPED'
        WHEN r_status < 0.90 THEN 'PROCESSING'
        WHEN r_status < 0.95 THEN 'PENDING'
        WHEN r_status < 0.98 THEN 'CANCELLED'
        ELSE 'RETURNED'
    END AS order_status,
    TIMESTAMPTZ '2023-01-01 00:00:00+00' + (random() * INTERVAL '900 days') AS order_date,
    ROUND((12.50 + (random() * 2487.50))::NUMERIC, 2) AS total_amount,
    (ARRAY['NORTH', 'SOUTH', 'EAST', 'WEST', 'CENTRAL'])[1 + (g % 5)] AS shipping_region,
    (ARRAY['CARD', 'WIRE', 'ACH', 'WALLET', 'COD'])[1 + ((g / 3)::INT % 5)] AS payment_method,
    (random() < 0.08) AS priority_flag,
    'Order #' || g::TEXT || ' fulfillment batch ' || (g % 250)::TEXT || ' standard logistics payload ' || REPEAT('x', 40 + (g % 60)) AS notes
FROM (
    SELECT g, random() AS r_status
    FROM generate_series(1, 500000) AS g
) AS src;

SELECT setval(pg_get_serial_sequence('orders', 'order_id'), COALESCE((SELECT MAX(order_id) FROM orders), 1));

COMMIT;

VACUUM ANALYZE customers;
VACUUM ANALYZE orders;

SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM customers
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM orders;
