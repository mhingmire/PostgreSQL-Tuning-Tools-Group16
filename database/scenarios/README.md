# Controlled Experimental Scenarios (`S01`–`S08`)

Each scenario in this directory isolates a single PostgreSQL performance anti-pattern so that **pgBadger**, **pgMustard**, **dbForge Studio for PostgreSQL**, and **postgresqltuner** can be evaluated fairly against an identical, reproducible ground truth.

> **Isolation Rule:** Run one scenario at a time (`setup.sql` -> `probe.sql` -> collect tool diagnostics -> `restore.sql`) so scenarios do not interfere with one another.

---

## Scenario Catalog

### S01 – Missing Index on Frequently Filtered Column
- **Scenario ID:** `S01`
- **Directory:** `database/scenarios/s01_missing_index/`
- **Intended Performance Problem:** Frequent selective queries filter `orders` by `order_status` and `order_date` (e.g., `order_status = 'RETURNED'` ~2% of rows, or `'CANCELLED'` with `priority_flag = TRUE` ~0.24% of rows) without a supporting composite index.
- **How It Is Created:** Baseline `orders` schema omits any index on `(order_status, order_date)`. `setup.sql` drops `idx_orders_status_date` if present and resets statistics.
- **Revealing PostgreSQL Statistics / Logs:**
  - `pg_stat_user_tables`: high `seq_scan` and `seq_tup_read` on `orders`
  - `pg_stat_statements`: high `mean_exec_time` and `shared_blks_read` / `shared_blks_hit`
  - `EXPLAIN (ANALYZE, BUFFERS)`: `Parallel Seq Scan on orders` with `Rows Removed by Filter`
  - PostgreSQL logs (`log_min_duration_statement = 0`): repeated slow `SELECT ... FROM orders WHERE order_status = ...`
- **Expected Diagnostic Evidence:** Tools should flag sequential scans on `orders`, identify the unindexed filter columns (`order_status`, `order_date`), and recommend a composite B-tree index.
- **How to Restore Original State:** Run `restore.sql` (drops `idx_orders_status_date` if created during optimization testing and runs `ANALYZE orders`).

### S02 – Duplicate Indexes
- **Scenario ID:** `S02`
- **Directory:** `database/scenarios/s02_duplicate_indexes/`
- **Intended Performance Problem:** Redundant identical and prefix-overlapping B-tree indexes on `orders(customer_id)` increase write amplification, storage footprint, and vacuum overhead without improving query plans.
- **How It Is Created:** `setup.sql` creates `idx_orders_customer_dup_a` on `orders(customer_id)` and `idx_orders_customer_dup_b` on `orders(customer_id)` alongside baseline `idx_orders_customer_id`.
- **Revealing PostgreSQL Statistics / Logs:**
  - `pg_index` + `pg_stat_user_indexes`: multiple indexes with identical `indkey` / `indexdef`
  - `pg_relation_size`: duplicated ~10–15 MB index footprint per duplicate
  - Write workload `pg_stat_statements`: elevated `shared_blks_dirtied` / execution time on `INSERT`/`UPDATE`
- **Expected Diagnostic Evidence:** Tools (especially `postgresqltuner` and `dbForge`) should detect duplicate/redundant indexes on `orders(customer_id)` and recommend dropping the duplicates.
- **How to Restore Original State:** Run `restore.sql` (`DROP INDEX IF EXISTS idx_orders_customer_dup_a, idx_orders_customer_dup_b;`).

### S03 – Unused Indexes
- **Scenario ID:** `S03`
- **Directory:** `database/scenarios/s03_unused_indexes/`
- **Intended Performance Problem:** Speculative indexes on low-selectivity or unqueried columns (`orders(payment_method)`, `orders(shipping_region, priority_flag)`, `customers(phone)`) consume disk/shared buffers and slow down writes while serving zero queries.
- **How It Is Created:** `setup.sql` creates three unused indexes and resets `pg_stat_user_indexes` counters (`pg_stat_reset()`).
- **Revealing PostgreSQL Statistics / Logs:**
  - `pg_stat_user_indexes`: `idx_scan = 0` while `pg_relation_size(indexrelid)` is non-trivial
  - `pg_stat_user_tables`: `n_tup_ins` / `n_tup_upd` increases while unused indexes never record scans
- **Expected Diagnostic Evidence:** Tools should report zero-scan (`idx_scan = 0`) indexes and quantify wasted storage.
- **How to Restore Original State:** Run `restore.sql` to drop all three unused indexes.

### S04 – Table Bloat via Controlled Updates and Deletes
- **Scenario ID:** `S04`
- **Directory:** `database/scenarios/s04_table_bloat/`
- **Intended Performance Problem:** Heavy unvacuumed `UPDATE` and `DELETE` churn creates tens of thousands of dead tuples and bloated heap pages, inflating sequential scan I/O and table size.
- **How It Is Created:** `setup.sql` temporarily disables autovacuum on `orders`, updates 120,000 rows in `orders`, and deletes/re-inserts 40,000 rows in a controlled transaction batch.
- **Revealing PostgreSQL Statistics / Logs:**
  - `pg_stat_user_tables`: high `n_dead_tup` (>100,000) and `dead_tuple_pct`
  - `pgstattuple('orders')`: elevated `dead_tuple_percent` and `free_percent`
  - `EXPLAIN (ANALYZE, BUFFERS)`: elevated `Buffers: shared hit/read` per scan compared to clean baseline
- **Expected Diagnostic Evidence:** Tools should warn on high dead-tuple ratio, disabled autovacuum on `orders`, and recommend `VACUUM (ANALYZE)` / `VACUUM FULL` (for severe bloat recovery).
- **How to Restore Original State:** Run `restore.sql` (`ALTER TABLE orders RESET (autovacuum_enabled); VACUUM FULL ANALYZE orders;`).

### S05 – Poor Configuration Settings
- **Scenario ID:** `S05`
- **Directory:** `database/scenarios/s05_poor_config/`
- **Intended Performance Problem:** Undersized memory and overly frequent checkpoint settings (`work_mem = '256kB'`, `maintenance_work_mem = '4MB'`, `effective_cache_size = '64MB'`, `random_page_cost = 4.0`, `max_wal_size = '96MB'`, `checkpoint_timeout = '1min'`) cause planner misestimates, disk spills, and excessive checkpoint writes.
- **How It Is Created:** `setup.sql` applies `ALTER SYSTEM SET ...` and reloads PostgreSQL configuration (`SELECT pg_reload_conf();`).
- **Revealing PostgreSQL Statistics / Logs:**
  - `pg_settings`: degraded values visible directly
  - `pg_stat_checkpointer`: high `num_requested` checkpoints
  - PostgreSQL logs (`log_checkpoints = on`, `log_temp_files = 0`): frequent checkpoint warnings/logs and temp-file writes
- **Expected Diagnostic Evidence:** `postgresqltuner` should flag misconfigured parameters (`work_mem`, `effective_cache_size`, `random_page_cost`, checkpoints); `pgBadger` should report checkpoint frequency and temp files; `pgMustard` should highlight disk sort/hash spills.
- **How to Restore Original State:** Run `restore.sql` (`ALTER SYSTEM RESET` for all modified settings + `SELECT pg_reload_conf();`).

### S06 – Slow Sequential Scans (Non-SARGable Predicates)
- **Scenario ID:** `S06`
- **Directory:** `database/scenarios/s06_slow_seq_scan/`
- **Intended Performance Problem:** Queries wrap indexed columns in functions (`LOWER(email) = ...` on `customers`, `EXTRACT(YEAR FROM order_date) = 2024` on `orders`), preventing index usage and forcing full sequential scans.
- **How It Is Created:** `setup.sql` resets `pg_stat_statements` and ensures no expression index exists; `probe.sql` runs the non-SARGable queries.
- **Revealing PostgreSQL Statistics / Logs:**
  - `EXPLAIN (ANALYZE, BUFFERS)`: `Seq Scan on customers` despite `customers_email_key` existing; `Parallel Seq Scan on orders`
  - `pg_stat_statements`: high `total_exec_time` and `shared_blks_hit/read`
  - PostgreSQL logs: slow query entries captured by `pgBadger`
- **Expected Diagnostic Evidence:** `pgMustard` and `dbForge` should show `Seq Scan` with `Filter` discarding 99.9%+ of rows; `pgBadger` should rank these queries at the top by total/mean duration.
- **How to Restore Original State:** Run `restore.sql` (drops any expression indexes created during optimization testing and resets stats).

### S07 – Inefficient Joins
- **Scenario ID:** `S07`
- **Directory:** `database/scenarios/s07_inefficient_joins/`
- **Intended Performance Problem:** Type-cast join predicate (`c.customer_id::TEXT = o.customer_id::TEXT`) disables index/FK join optimization, and an unindexed multi-column filtered join with constrained `work_mem` causes a slow hash/nested-loop join with buffer thrashing.
- **How It Is Created:** `setup.sql` sets `work_mem = '512kB'` via `ALTER SYSTEM` (reloaded) and resets stats; `probe.sql` executes the inefficient join queries.
- **Revealing PostgreSQL Statistics / Logs:**
  - `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`: `Hash Join` with `Batches: >1` (disk spill) or `Seq Scan` on both `customers` and `orders`, high `actual time` and `shared_blks_read`
  - `pg_stat_statements`: high `mean_exec_time` and `temp_blks_written`
- **Expected Diagnostic Evidence:** `pgMustard` and `dbForge` should pinpoint the join node, cardinality/cost spike, and temp spill; `pgBadger` should surface the slow join query.
- **How to Restore Original State:** Run `restore.sql` (`ALTER SYSTEM RESET work_mem; SELECT pg_reload_conf();` and drop any temporary optimization indexes).

### S08 – Sorting and Temporary-File Activity
- **Scenario ID:** `S08`
- **Directory:** `database/scenarios/s08_sorting_temp_files/`
- **Intended Performance Problem:** Large sort and window/aggregation queries over 500,000 `orders` rows (`ORDER BY total_amount DESC, order_date DESC, notes`) run under `work_mem = '256kB'`, forcing external disk merge sorts and heavy temporary-file I/O.
- **How It Is Created:** `setup.sql` sets `work_mem = '256kB'` (`ALTER SYSTEM`) + reload and resets stats; `probe.sql` runs sort-heavy queries.
- **Revealing PostgreSQL Statistics / Logs:**
  - `EXPLAIN (ANALYZE, BUFFERS)`: `Sort Method: external merge Disk: ...kB` and `temp read/written` buffers
  - `pg_stat_database`: jump in `temp_files` and `temp_bytes`
  - `pg_stat_statements`: non-zero `temp_blks_written`
  - PostgreSQL logs (`log_temp_files = 0`): explicit `LOG: temporary file: path "base/pgsql_tmp/...", size ...` entries parsed by `pgBadger`
- **Expected Diagnostic Evidence:** `pgBadger` should highlight top temp-file queries; `pgMustard` should flag `external merge Disk` sort; `postgresqltuner` should recommend increasing `work_mem`; `dbForge` profiler should show high temp I/O.
- **How to Restore Original State:** Run `restore.sql` (`ALTER SYSTEM RESET work_mem; SELECT pg_reload_conf();`).
