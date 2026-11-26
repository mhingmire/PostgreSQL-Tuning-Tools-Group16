-- S07 restore.sql: Reset work_mem and remove temporary optimization indexes
ALTER SYSTEM RESET work_mem;
SELECT pg_reload_conf();
DROP INDEX IF EXISTS idx_customers_segment_region;
DROP INDEX IF EXISTS idx_orders_status_customer;
ANALYZE customers;
ANALYZE orders;
