-- 01_extensions.sql
-- Enables core observability and diagnostic extensions for PostgreSQL 17.
-- Executed automatically during container initialization and safe to re-run.

CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgstattuple;
CREATE EXTENSION IF NOT EXISTS pg_buffercache;

COMMENT ON EXTENSION pg_stat_statements IS 'Tracks planning and execution statistics for all SQL statements.';
COMMENT ON EXTENSION pgstattuple IS 'Provides tuple-level statistics to quantify table and index bloat.';
COMMENT ON EXTENSION pg_buffercache IS 'Inspects shared buffer cache usage in real time.';
