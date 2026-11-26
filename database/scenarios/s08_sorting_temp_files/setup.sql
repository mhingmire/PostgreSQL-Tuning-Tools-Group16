-- S08 setup.sql: Force disk-based external sorting and temporary file generation
ALTER SYSTEM SET work_mem = '256kB';
SELECT pg_reload_conf();
SELECT pg_stat_reset();
SELECT pg_stat_statements_reset();
