-- S02 probe.sql: Demonstrate write overhead and inspect duplicate index metadata
SELECT
    i.indexrelid::regclass AS index_name,
    pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
    pg_get_indexdef(i.indexrelid) AS index_definition
FROM pg_index i
WHERE i.indrelid = 'orders'::regclass
ORDER BY index_name;

BEGIN;
INSERT INTO orders (customer_id, order_status, order_date, total_amount, shipping_region, payment_method, priority_flag, notes)
SELECT
    1 + (g % 20000),
    'PROCESSING',
    NOW(),
    149.99,
    'NORTH',
    'CARD',
    FALSE,
    'S02 duplicate index write overhead probe'
FROM generate_series(1, 2000) AS g;
ROLLBACK;
