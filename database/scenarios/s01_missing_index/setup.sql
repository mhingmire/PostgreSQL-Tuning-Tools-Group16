-- S01 setup.sql: Missing index on frequently filtered columns (order_status, order_date)
DROP INDEX IF EXISTS idx_orders_status_date;
ANALYZE orders;
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
