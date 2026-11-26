# Experimental Methodology

## 1. Controlled Evaluation Design
- **Identical Baseline:** Every experiment starts from a clean PostgreSQL 17 instance seeded with `pgbench -s 50` and `customers` (20,000 rows) + `orders` (500,000 rows).
- **Scenario Isolation (`S01`–`S08`):** Only one scenario is active at a time (`setup.sql` -> `probe.sql` -> tool analysis -> `restore.sql`) to prevent cross-scenario confounding.
- **Repeated Measurements:** Every benchmark (`workload/benchmark_scripts/run_benchmark.py`) executes at least **3 independent repetitions** (`--runs 3`), resetting `pg_stat_*` and `pg_stat_statements` before each run.
- **Metrics Collected:**
  - Throughput (`TPS`)
  - Average, p50, p95, and p99 transaction latency (`ms`) from per-transaction `pgbench -l` logs
  - Per-query `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` execution times
  - Shared buffer hits/reads, cache hit ratio, and temp files/bytes
  - Monitoring overhead across `minimal_obs`, `stats_and_slow_logs`, and `full_pgbadger_logging` (`experiments/overhead/measure_overhead.py`)

## 2. Four Core Evaluation Criteria
1. **Bottleneck Identification** (1–5)
2. **Index Analysis** (1–5)
3. **Tuning Recommendations** (1–5)
4. **Reporting** (1–5)

Additionally, each tool is scored `0–2` against each of the 8 scenarios in `experiments/tool_evaluations/ground_truth_matrix.md` (max `16`), and assessed on setup effort, ease of use, cost/licensing, compatibility, monitoring overhead, recommendation accuracy, and limitations.
