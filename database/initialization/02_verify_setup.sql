-- 02_verify_setup.sql
-- Verifies PostgreSQL version, extensions, logging settings, I/O timing, and row counts.

SELECT version() AS postgres_version;

SELECT
    extname,
    extversion
FROM pg_extension
WHERE extname IN ('pg_stat_statements', 'pgstattuple', 'pg_buffercache')
ORDER BY extname;

SELECT
    name,
    setting,
    unit,
    source
FROM pg_settings
WHERE name IN (
    'shared_preload_libraries',
    'track_io_timing',
    'logging_collector',
    'log_directory',
    'log_line_prefix',
    'log_min_duration_statement',
    'log_checkpoints',
    'log_lock_waits',
    'log_temp_files',
    'shared_buffers',
    'work_mem',
    'effective_cache_size',
    'random_page_cost'
)
ORDER BY name;

SELECT
    relname AS table_name,
    n_live_tup AS estimated_rows,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_stat_user_tables
ORDER BY relname;
