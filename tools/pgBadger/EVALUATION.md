# Tool Evaluation: pgBadger

- **Evaluators:** Assigned across P1, P2, P3 (cross-reviewed)
- **Tool Category:** Offline PostgreSQL Log Analyzer
- **Official Project:** https://pgbadger.darold.net/

## 1. Purpose and Architecture
pgBadger is a Perl-based PostgreSQL log analyzer that parses PostgreSQL log files (`stderr`, `csvlog`, `jsonlog`, or `syslog`) and generates interactive static HTML reports with charts, query rankings, checkpoint/autovacuum timelines, lock waits, and temporary-file statistics. It operates completely out-of-band on exported log files.

## 2. Installation and Setup
- **Log Format Prerequisites (Configured in `database/initialization/postgresql.conf`):**
  - `log_destination = 'stderr'`
  - `log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '`
  - `lc_messages = 'C'`
  - `log_min_duration_statement = 0` (or thresholded for overhead comparison)
  - `log_checkpoints = on`, `log_lock_waits = on`, `log_temp_files = 0`, `log_autovacuum_min_duration = 0`
- **Export Logs from Docker:** Run `python tools/pgBadger/collect_logs.py`
- **Run pgBadger (via WSL/Perl or Docker):** Document exact version and command used in `reports/tool_reports/`.

## 3. Data Sources
- PostgreSQL server log files copied from `/var/lib/postgresql/data/pgdata/log/` inside `tuning_lab_pg17` (no direct database connection required during analysis).

## 4. Features Tested
- [ ] Slowest queries & time-consuming query normalization
- [ ] Temporary file usage & largest temp files (`S08`)
- [ ] Checkpoint & restartpoint frequency (`S05`)
- [ ] Lock waits & deadlocks
- [ ] Autovacuum / autoanalyze activity (`S04`)
- [ ] Connection & error summaries

## 5. Four Core Evaluation Criteria
1. **Bottleneck Identification:** _TBD after experiment execution_
2. **Index Analysis:** _TBD (expected limitation: log-only scope cannot inspect unused/duplicate indexes directly)_
3. **Tuning Recommendations:** _TBD_
4. **Reporting:** _TBD (HTML report quality, graphs, drill-down)_

## 6. Experimental Observations (Scenarios S01–S08)
| Scenario | Observed in pgBadger? | Evidence / Metrics Reported | Notes |
|---|---|---|---|
| S01 (Missing index) | TBD | | |
| S02 (Duplicate indexes) | TBD | | |
| S03 (Unused indexes) | TBD | | |
| S04 (Table bloat) | TBD | | |
| S05 (Poor config) | TBD | | |
| S06 (Slow seq scans) | TBD | | |
| S07 (Inefficient joins) | TBD | | |
| S08 (Sorting & temp files) | TBD | | |

## 7. Ground-Truth Detection Score
- **Score:** `TBD / 16` (see `experiments/tool_evaluations/ground_truth_matrix.md`)

## 8. Screenshots and Raw Outputs
- Store HTML reports in `reports/tool_reports/pgbadger_<scenario>.html`
- Store screenshots in `reports/screenshots/pgbadger_*.png`

## 9. Setup Effort
- _TBD: Document time/commands to configure `log_line_prefix`, export logs, and run pgBadger on Windows._

## 10. Cost and Licensing
- **License:** PostgreSQL License (Open Source, Free)
- **Cost:** \$0

## 11. Limitations
- Requires properly formatted PostgreSQL logs (`lc_messages = 'C'`, specific `log_line_prefix`).
- Does not inspect catalog metadata (`pg_stat_user_indexes`, `pg_index`), so it cannot directly identify duplicate (`S02`) or unused (`S03`) indexes.
- Setting `log_min_duration_statement = 0` introduces disk I/O logging overhead under high TPS (quantified in `experiments/overhead/`).

## 12. Final Assessment
- _TBD after completing `S01`–`S08` and before/after optimization verification._
