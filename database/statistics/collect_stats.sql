-- collect_stats.sql
-- Collects a comprehensive snapshot of PostgreSQL performance statistics:
--   1. Top statements from pg_stat_statements
--   2. Database-level cache hit ratio, temp files, deadlocks, checkpoints
--   3. Table-level sequential vs index scans and dead tuples
--   4. Index usage and potential unused/duplicate indexes

\echo '=== 1. DATABASE-LEVEL STATISTICS ==='
SELECT
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS cache_hit_ratio_pct,
    temp_files,
    pg_size_pretty(temp_bytes) AS temp_bytes_pretty,
    deadlocks,
    blk_read_time,
    blk_write_time
FROM pg_stat_database
WHERE datname = current_database();

\echo '=== 2. BGWRITER & CHECKPOINTER STATISTICS ==='
SELECT
    num_timed,
    num_requested,
    write_time,
    sync_time,
    buffers_written
FROM pg_stat_checkpointer;

\echo '=== 3. TABLE SCAN & BLOAT STATISTICS ==='
SELECT
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_live_tup,
    n_dead_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_pct,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

\echo '=== 4. INDEX USAGE STATISTICS ==='
SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC, pg_relation_size(indexrelid) DESC;

\echo '=== 5. TOP 15 QUERIES BY TOTAL EXECUTION TIME (pg_stat_statements) ==='
SELECT
    queryid,
    calls,
    ROUND(total_exec_time::NUMERIC, 2) AS total_ms,
    ROUND(mean_exec_time::NUMERIC, 2) AS mean_ms,
    ROUND(stddev_exec_time::NUMERIC, 2) AS stddev_ms,
    rows,
    shared_blks_hit,
    shared_blks_read,
    temp_blks_written,
    LEFT(REGEXP_REPLACE(query, '\s+', ' ', 'g'), 100) AS query_snippet
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY total_exec_time DESC
LIMIT 15;
