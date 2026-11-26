-- S07 setup.sql: Constrain work_mem and remove composite helper indexes to expose join inefficiency
ALTER SYSTEM SET work_mem = '512kB';
SELECT pg_reload_conf();
DROP INDEX IF EXISTS idx_customers_segment_region;
DROP INDEX IF EXISTS idx_orders_status_customer;
ANALYZE customers;
ANALYZE orders;
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
