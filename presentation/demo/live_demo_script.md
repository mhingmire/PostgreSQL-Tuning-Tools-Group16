# Live Demo Script (All 3 Members Participating)

- **Segment 1 (P1 – ~2 min):** Show `docker compose ps`, DBeaver connection to `tuning_lab`, and row counts (`customers`, `orders`, `pgbench_accounts`).
- **Segment 2 (P2 – ~2.5 min):** Apply Scenario `S01` or `S08`, run `probe.sql`, and show live diagnostic evidence (`EXPLAIN ANALYZE BUFFERS` / `pg_stat_statements`) + `postgresqltuner` or `dbForge` output.
- **Segment 3 (P3 – ~2.5 min):** Show `pgBadger` HTML report / `pgMustard` plan tips, apply optimization (`01_apply_optimizations.sql`), and show `compare_before_after.py` measured TPS/latency speedup.
