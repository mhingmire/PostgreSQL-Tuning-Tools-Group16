-- S04 setup.sql: Introduce controlled table bloat via updates/deletes with autovacuum disabled
ALTER TABLE orders SET (autovacuum_enabled = false);

UPDATE orders
SET notes = notes || ' [bloat-pass-1]'
WHERE order_id <= 120000;

WITH deleted_rows AS (
    DELETE FROM orders
    WHERE order_id BETWEEN 120001 AND 160000
    RETURNING order_id, customer_id, order_status, order_date, total_amount, shipping_region, payment_method, priority_flag, notes
)
INSERT INTO orders (order_id, customer_id, order_status, order_date, total_amount, shipping_region, payment_method, priority_flag, notes)
SELECT order_id, customer_id, order_status, order_date, total_amount, shipping_region, payment_method, priority_flag, notes
FROM deleted_rows;

ANALYZE orders;
SELECT pg_stat_statements_reset();
