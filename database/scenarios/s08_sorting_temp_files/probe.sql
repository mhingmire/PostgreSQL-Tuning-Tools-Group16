-- S08 probe.sql: Large sort and window operations triggering external merge Disk + temp files
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT
    order_id,
    customer_id,
    order_status,
    total_amount,
    notes
FROM orders
ORDER BY total_amount DESC, order_date DESC, notes
LIMIT 500 OFFSET 100000;

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT
    customer_id,
    order_id,
    total_amount,
    ROW_NUMBER() OVER (PARTITION BY shipping_region ORDER BY total_amount DESC, order_id) AS region_rank
FROM orders
WHERE order_date >= TIMESTAMPTZ '2024-06-01 00:00:00+00'
ORDER BY region_rank
LIMIT 200;

SELECT
    datname,
    temp_files,
    pg_size_pretty(temp_bytes) AS temp_bytes_pretty
FROM pg_stat_database
WHERE datname = current_database();
