-- S03 setup.sql: Unused indexes on low-utility or unqueried columns
CREATE INDEX IF NOT EXISTS idx_orders_payment_method_unused ON orders (payment_method);
CREATE INDEX IF NOT EXISTS idx_orders_region_priority_unused ON orders (shipping_region, priority_flag);
CREATE INDEX IF NOT EXISTS idx_customers_phone_unused ON customers (phone);
ANALYZE customers;
ANALYZE orders;
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
