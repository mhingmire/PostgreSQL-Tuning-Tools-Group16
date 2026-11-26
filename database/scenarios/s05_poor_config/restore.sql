-- S05 restore.sql: Reset ALTER SYSTEM overrides back to postgresql.conf baseline
ALTER SYSTEM RESET work_mem;
ALTER SYSTEM RESET maintenance_work_mem;
ALTER SYSTEM RESET effective_cache_size;
ALTER SYSTEM RESET random_page_cost;
ALTER SYSTEM RESET max_wal_size;
ALTER SYSTEM RESET checkpoint_timeout;
SELECT pg_reload_conf();
