-- S04 restore.sql: Re-enable autovacuum and reclaim bloated space via VACUUM FULL ANALYZE
ALTER TABLE orders RESET (autovacuum_enabled);
VACUUM FULL ANALYZE orders;
