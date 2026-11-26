-- custom_order_oltp.sql
-- pgbench custom workload script targeting the order-management schema.
-- Exercises selective lookups, customer-order joins, status filters, and controlled inserts.

\set cid random(1, 20000)
\set amt random(15, 1500)

-- 1. Point lookup on customer + recent orders (uses idx_orders_customer_id)
SELECT c.customer_id, c.segment, COUNT(o.order_id) AS order_cnt, COALESCE(SUM(o.total_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE c.customer_id = :cid
GROUP BY c.customer_id, c.segment;

-- 2. Selective status + date filter (tests S01 missing index vs optimized composite index)
SELECT order_id, customer_id, total_amount
FROM orders
WHERE order_status = 'RETURNED'
  AND order_date >= TIMESTAMPTZ '2025-01-01 00:00:00+00'
ORDER BY order_date DESC
LIMIT 25;

-- 3. Controlled single-row update on customer loyalty points
UPDATE customers
SET loyalty_points = loyalty_points + 1
WHERE customer_id = :cid;
