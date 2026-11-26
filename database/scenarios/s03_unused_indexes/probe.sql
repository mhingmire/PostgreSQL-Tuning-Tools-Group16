-- S03 probe.sql: Workload never touches unused indexes; inspect idx_scan = 0
SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE c.customer_id BETWEEN 100 AND 250
GROUP BY c.customer_id, c.full_name;

SELECT
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE indexrelname LIKE '%_unused'
ORDER BY pg_relation_size(indexrelid) DESC;
