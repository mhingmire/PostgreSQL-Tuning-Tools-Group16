# Project Plan: PostgreSQL Tuning Tools Comparative Evaluation

**Course:** COMPSCI 4411/9538  
**Group 16:** Mrida Hingmire, Atika Hussain, Jasnav Bajaj  

---

## 1. Objectives
1. Stand up a reproducible PostgreSQL 17 Docker environment (`tuning_lab`) with `pg_stat_statements`, `pgstattuple`, `track_io_timing`, and pgBadger-compatible logging.
2. Seed identical datasets (`pgbench` scale 50 + 20k `customers` / 500k `orders`).
3. Create 8 isolated, reproducible performance scenarios (`S01`–`S08`) and a ground-truth matrix.
4. Execute >=3 benchmark repetitions per condition, capturing TPS, avg/p95 latency, per-query times, buffer hits/reads, and monitoring overhead.
5. Evaluate **pgBadger**, **pgMustard**, **dbForge Studio for PostgreSQL**, and **postgresqltuner** fairly against the ground-truth matrix and four core criteria.
6. Validate tool recommendations empirically via before-and-after benchmarks.
7. Deliver the final report, presentation slide deck, and live/recorded demo.

---

## 2. Milestones & Phases

| Phase | Scope | Key Deliverables |
|---|---|---|
| **Phase 1: Environment & Data** | Docker Compose PG 17, schema, deterministic seeding, DBeaver & Git setup | `docker-compose.yml`, `postgresql.conf`, `01_order_management_schema.sql`, `01_generate_order_data.sql`, `pgbench -s 50` |
| **Phase 2: Scenarios & Benchmark Harness** | `S01`–`S08` SQL scripts, `run_benchmark.py`, `measure_overhead.py`, `compare_before_after.py` | Verified scenario setup/probe/restore scripts, initial 3-run baseline JSON/CSV |
| **Phase 3: Tool Evaluations** | Run all 4 tools on `S01`–`S08`, score ground-truth matrix, document licensing/limitations | Completed `tools/*/EVALUATION.md`, screenshots, raw tool reports |
| **Phase 4: Empirical Optimization & Overhead** | Apply recommendations, run 3-run after-benchmarks, compute before/after deltas | `results/comparison/*.md`, `reports/figures/*.png`, overhead dataset |
| **Phase 5: Synthesis, Report & Presentation** | Finalize comparative report, peer reviews, clean-machine test, slides & demo video | Final report, `presentation/slides/`, `presentation/demo_video/` |
