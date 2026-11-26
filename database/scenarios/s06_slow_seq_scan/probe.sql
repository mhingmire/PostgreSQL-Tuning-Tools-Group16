-- S06 probe.sql: Non-SARGable predicates forcing sequential scans on indexed/large tables
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT customer_id, full_name, email, segment
FROM customers
WHERE LOWER(email) = 'customer12345@tuninglab-demo.example';

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE EXTRACT(YEAR FROM order_date) = 2024
  AND shipping_region = 'WEST'
ORDER BY total_amount DESC
LIMIT 50;
