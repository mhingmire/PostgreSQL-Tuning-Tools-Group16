-- 02_revert_optimizations.sql
-- Reverses all optimizations from 01_apply_optimizations.sql to restore the exact clean baseline.

DROP INDEX IF EXISTS idx_orders_status_date;
DROP INDEX IF EXISTS idx_orders_cancelled_priority;
DROP INDEX IF EXISTS idx_customers_lower_email;
DROP INDEX IF EXISTS idx_customers_segment_region;
DROP INDEX IF EXISTS idx_orders_region_amount;

ALTER SYSTEM RESET work_mem;
ALTER SYSTEM RESET maintenance_work_mem;
ALTER SYSTEM RESET effective_cache_size;
ALTER SYSTEM RESET random_page_cost;
ALTER SYSTEM RESET max_wal_size;
ALTER SYSTEM RESET checkpoint_timeout;
SELECT pg_reload_conf();

ANALYZE customers;
ANALYZE orders;
