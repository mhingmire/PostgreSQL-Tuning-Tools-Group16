# System Architecture

## 1. Environment Topology
All four tuning tools evaluate the exact same containerized PostgreSQL 17 instance (`tuning_lab_pg17`):

- **Database Engine:** `postgres:17` via `docker-compose.yml`
- **Database & Role:** `tuning_lab` owned/accessed by `projectuser` (credentials loaded via `.env`)
- **Persistent Volumes:**
  - `pgdata` -> `/var/lib/postgresql/data` (includes `/var/lib/postgresql/data/pgdata/log` for pgBadger ingestion via `tools/pgBadger/collect_logs.py`)
- **Observability Configuration (`database/initialization/postgresql.conf`):**
  - `pg_stat_statements` (`shared_preload_libraries`, `track = all`)
  - `pgstattuple` and `pg_buffercache`
  - `track_io_timing = on`
  - `logging_collector = on`, `log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '`
  - `log_checkpoints = on`, `log_lock_waits = on`, `log_temp_files = 0`

## 2. Tool Integration Paths
1. **pgBadger:** Offline parsing of logs copied from `pglogs` (`tools/pgBadger/collect_logs.py`).
2. **pgMustard:** Manual web submission of JSON execution plans exported via `tools/pgMustard/export_explain_plans.py`.
3. **dbForge Studio for PostgreSQL:** Direct TCP connection to `localhost:5432` from Windows desktop.
4. **postgresqltuner:** Direct TCP SQL catalog audit (`tools/postgresqltuner/run_postgresqltuner.py`).
