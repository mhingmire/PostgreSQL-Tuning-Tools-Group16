-- 01_apply_optimizations.sql
-- Applies validated optimizations corresponding to scenarios S01-S08
-- for controlled before-and-after benchmark measurement.

-- 1. S01 / Q1 & Q2 remediation: composite & partial/covering indexes for frequent order filters
CREATE INDEX IF NOT EXISTS idx_orders_status_date
    ON orders (order_status, order_date DESC);

CREATE INDEX IF NOT EXISTS idx_orders_cancelled_priority
    ON orders (order_status, priority_flag)
    INCLUDE (total_amount)
    WHERE order_status = 'CANCELLED';

-- 2. S06 remediation: expression index if legacy non-SARGable LOWER(email) queries cannot be rewritten
CREATE INDEX IF NOT EXISTS idx_customers_lower_email
    ON customers (LOWER(email));

-- 3. S07 remediation: composite join & filter support
CREATE INDEX IF NOT EXISTS idx_customers_segment_region
    ON customers (segment, region)
    INCLUDE (customer_id, full_name);

CREATE INDEX IF NOT EXISTS idx_orders_region_amount
    ON orders (shipping_region, total_amount DESC, order_date DESC);

-- 4. S05 / S08 remediation: balanced memory & planner settings
ALTER SYSTEM SET work_mem = '32MB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET effective_cache_size = '1536MB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET max_wal_size = '2GB';
ALTER SYSTEM SET checkpoint_timeout = '10min';
SELECT pg_reload_conf();

-- 5. S04 remediation: ensure healthy statistics & zero dead-tuple bloat
ALTER TABLE orders RESET (autovacuum_enabled);
VACUUM ANALYZE customers;
VACUUM ANALYZE orders;
