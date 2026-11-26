# Tool Evaluation: postgresqltuner

- **Evaluators:** Assigned across P1, P2, P3 (cross-reviewed)
- **Tool Category:** Open-Source Perl Diagnostic & Configuration Audit Script
- **Official Project:** https://github.com/jfcoz/postgresqltuner

## 1. Purpose and Architecture
`postgresqltuner.pl` is a read-only diagnostic Perl script (inspired by MySQLTuner) that connects to a PostgreSQL instance, inspects `pg_settings`, `pg_stat_*`, `pg_index`, `pg_stat_statements`, and host OS metrics (when run locally on the DB host), and prints a color-coded health report with configuration and schema tuning advice.

## 2. Installation and Setup
- Can be executed via Perl (`perl postgresqltuner.pl`) or a lightweight Docker container attached to the Compose network (`--network host` or Compose network).
- **Constraint:** Because PostgreSQL runs inside a Docker container (`tuning_lab_pg17`), `postgresqltuner` run from outside the container may have **limited visibility into container/host-level OS resources** (e.g., `/proc/meminfo`, CPU count, sysctl `vm.*`, disk layout). Document clearly which checks run remotely vs. inside the container.
- Helper runner: `tools/postgresqltuner/run_postgresqltuner.py`

## 3. Data Sources
- PostgreSQL system catalogs and statistics views (`pg_settings`, `pg_stat_database`, `pg_stat_user_tables`, `pg_stat_user_indexes`, `pg_index`, `pg_stat_statements`), plus local OS `/proc` metrics if accessible.

## 4. Features Tested
- [ ] Configuration & memory audit (`S05`: `work_mem`, `effective_cache_size`, `shared_buffers`, checkpoints)
- [ ] Duplicate & redundant index detection (`S02`)
- [ ] Unused index detection (`S03`)
- [ ] Bloat & autovacuum diagnostics (`S04`)
- [ ] Temporary-file and cache-hit warnings (`S08`)

## 5. Four Core Evaluation Criteria
1. **Bottleneck Identification:** _TBD_
2. **Index Analysis:** _TBD_
3. **Tuning Recommendations:** _TBD_
4. **Reporting:** _TBD (plain-text CLI report; parseability vs. lack of charts)_

## 6. Experimental Observations (Scenarios S01–S08)
| Scenario | Observed in postgresqltuner? | Advice / Warnings Emitted | Notes |
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
- **Score:** `TBD / 16`

## 8. Screenshots and Raw Outputs
- Raw text reports: `reports/tool_reports/postgresqltuner_<scenario>.txt`
- Screenshots: `reports/screenshots/postgresqltuner_*.png`

## 9. Setup Effort
- _TBD (Perl + `DBD::Pg` dependency on Windows vs. running in a temporary Perl container)._

## 10. Cost and Licensing
- **License:** GPLv3 (Open Source, Free)
- **Cost:** \$0

## 11. Limitations
- Limited visibility into Docker host/container OS memory & kernel parameters when executed remotely.
- Cannot analyze individual query execution plans (`EXPLAIN ANALYZE`) like `pgMustard` or `dbForge`.
- Heuristic rule-based thresholds may occasionally emit generic advice without workload context.

## 12. Final Assessment
- _TBD after completing `S01`–`S08` and before/after optimization verification._
