-- S03 restore.sql: Drop unused indexes and restore clean baseline
DROP INDEX IF EXISTS idx_orders_payment_method_unused;
DROP INDEX IF EXISTS idx_orders_region_priority_unused;
DROP INDEX IF EXISTS idx_customers_phone_unused;
ANALYZE customers;
ANALYZE orders;
