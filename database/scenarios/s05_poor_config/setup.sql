-- S05 setup.sql: Apply intentionally suboptimal configuration settings via ALTER SYSTEM
ALTER SYSTEM SET work_mem = '256kB';
ALTER SYSTEM SET maintenance_work_mem = '4MB';
ALTER SYSTEM SET effective_cache_size = '64MB';
ALTER SYSTEM SET random_page_cost = 4.0;
ALTER SYSTEM SET max_wal_size = '96MB';
ALTER SYSTEM SET checkpoint_timeout = '1min';
SELECT pg_reload_conf();
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
