-- S06 restore.sql: Clean up any expression indexes created during optimization
DROP INDEX IF EXISTS idx_customers_lower_email;
DROP INDEX IF EXISTS idx_orders_year_region;
ANALYZE customers;
ANALYZE orders;
