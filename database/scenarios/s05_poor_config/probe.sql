-- S05 probe.sql: Verify degraded settings and run mixed planner/sort probe
SELECT name, setting, unit, source
FROM pg_settings
WHERE name IN (
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'random_page_cost',
    'max_wal_size',
    'checkpoint_timeout'
)
ORDER BY name;

EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT c.region, o.order_status, COUNT(*) AS cnt, SUM(o.total_amount) AS revenue
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.region, o.order_status
ORDER BY revenue DESC;
