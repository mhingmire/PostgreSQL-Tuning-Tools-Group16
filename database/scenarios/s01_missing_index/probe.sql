-- S01 probe.sql: Selective queries on unindexed order_status and order_date
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT order_id, customer_id, order_date, total_amount, shipping_region
FROM orders
WHERE order_status = 'RETURNED'
  AND order_date >= TIMESTAMPTZ '2025-01-01 00:00:00+00'
ORDER BY order_date DESC
LIMIT 100;

SELECT COUNT(*), SUM(total_amount)
FROM orders
WHERE order_status = 'CANCELLED'
  AND priority_flag = TRUE;

SELECT order_id, customer_id, total_amount
FROM orders
WHERE order_status = 'PENDING'
  AND order_date BETWEEN TIMESTAMPTZ '2024-06-01 00:00:00+00' AND TIMESTAMPTZ '2024-07-01 00:00:00+00';
