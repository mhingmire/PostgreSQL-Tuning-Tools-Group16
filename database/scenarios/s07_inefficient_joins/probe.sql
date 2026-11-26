-- S07 probe.sql: Inefficient type-casted join + large filtered hash join under low work_mem
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT
    c.customer_id,
    c.segment,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id::TEXT = o.customer_id::TEXT
WHERE c.segment = 'VIP'
  AND o.order_status = 'DELIVERED'
GROUP BY c.customer_id, c.segment
ORDER BY total_spent DESC
LIMIT 50;

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT
    c.region,
    o.payment_method,
    COUNT(*) AS order_cnt,
    AVG(o.total_amount) AS avg_amount
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_date >= TIMESTAMPTZ '2024-01-01 00:00:00+00'
GROUP BY c.region, o.payment_method
ORDER BY order_cnt DESC;
