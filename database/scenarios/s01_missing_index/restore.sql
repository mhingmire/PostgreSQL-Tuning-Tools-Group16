-- S01 restore.sql: Restore clean baseline state
DROP INDEX IF EXISTS idx_orders_status_date;
ANALYZE orders;
