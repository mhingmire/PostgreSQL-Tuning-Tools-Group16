-- S02 setup.sql: Duplicate and redundant indexes on orders(customer_id)
CREATE INDEX IF NOT EXISTS idx_orders_customer_dup_a ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_dup_b ON orders (customer_id);
ANALYZE orders;
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
