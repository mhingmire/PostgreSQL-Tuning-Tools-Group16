-- S08 restore.sql: Reset work_mem back to postgresql.conf baseline
ALTER SYSTEM RESET work_mem;
SELECT pg_reload_conf();
