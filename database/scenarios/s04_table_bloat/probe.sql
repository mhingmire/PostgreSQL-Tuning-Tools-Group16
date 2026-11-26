-- S04 probe.sql: Inspect dead tuples, pgstattuple bloat metrics, and scan buffer reads
SELECT
    relname,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_pct,
    pg_size_pretty(pg_relation_size('orders')) AS heap_size,
    pg_size_pretty(pg_total_relation_size('orders')) AS total_size
FROM pg_stat_user_tables
WHERE relname = 'orders';

SELECT * FROM pgstattuple('orders');

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT COUNT(*), SUM(total_amount)
FROM orders
WHERE shipping_region = 'NORTH';
