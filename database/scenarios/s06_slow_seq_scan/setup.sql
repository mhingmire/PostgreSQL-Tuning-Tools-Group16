-- S06 setup.sql: Ensure no expression indexes exist so non-SARGable queries trigger Seq Scan
DROP INDEX IF EXISTS idx_customers_lower_email;
DROP INDEX IF EXISTS idx_orders_year_region;
ANALYZE customers;
ANALYZE orders;
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
