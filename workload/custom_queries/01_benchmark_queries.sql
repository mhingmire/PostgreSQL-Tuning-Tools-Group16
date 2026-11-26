-- 01_benchmark_queries.sql
-- Standardized set of diagnostic & performance benchmark queries (Q1-Q6)
-- executed identically before and after optimizations.

-- Q1: Selective order_status + date range lookup (tests S01)
SELECT order_id, customer_id, order_date, total_amount
FROM orders
WHERE order_status = 'RETURNED'
  AND order_date >= TIMESTAMPTZ '2025-01-01 00:00:00+00'
ORDER BY order_date DESC
LIMIT 100;

-- Q2: Filtered count & sum for priority cancelled orders (tests S01)
SELECT COUNT(*) AS cancelled_priority_cnt, COALESCE(SUM(total_amount), 0) AS cancelled_total
FROM orders
WHERE order_status = 'CANCELLED'
  AND priority_flag = TRUE;

-- Q3: Customer-orders join aggregation by region and segment (tests S07)
SELECT c.region, c.segment, COUNT(o.order_id) AS orders_cnt, ROUND(AVG(o.total_amount), 2) AS avg_order
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_date >= TIMESTAMPTZ '2024-07-01 00:00:00+00'
GROUP BY c.region, c.segment
ORDER BY orders_cnt DESC;

-- Q4: Exact customer email lookup (SARGable baseline vs non-SARGable S06)
SELECT customer_id, full_name, email, segment
FROM customers
WHERE email = 'customer12345@tuninglab-demo.example';

-- Q5: Large analytical sort across orders (tests S08 work_mem / temp files)
SELECT order_id, customer_id, total_amount, order_date
FROM orders
WHERE shipping_region = 'NORTH'
ORDER BY total_amount DESC, order_date DESC
LIMIT 250;

-- Q6: Multi-table VIP top-spenders join
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS order_cnt, SUM(o.total_amount) AS lifetime_spend
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.segment = 'VIP'
  AND o.order_status = 'DELIVERED'
GROUP BY c.customer_id, c.full_name
ORDER BY lifetime_spend DESC
LIMIT 25;
