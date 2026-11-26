-- S02 restore.sql: Remove duplicate indexes and restore clean baseline
DROP INDEX IF EXISTS idx_orders_customer_dup_a;
DROP INDEX IF EXISTS idx_orders_customer_dup_b;
ANALYZE orders;
