# Monitoring & Logging Overhead Measurement Protocol

To evaluate tool monitoring overhead fairly, we measure identical `pgbench` workloads (`custom_orders`, 3 repetitions each) across three observability profiles using `experiments/overhead/measure_overhead.py`:

1. **`minimal_obs`:** `log_min_duration_statement = -1`, `track_io_timing = off`, `log_checkpoints = off`, `log_lock_waits = off` (minimum instrumentation control).
2. **`stats_and_slow_logs`:** `log_min_duration_statement = 200`, `track_io_timing = on`, `log_checkpoints = on`, `log_lock_waits = on` (production-style slow-query logging).
3. **`full_pgbadger_logging`:** `log_min_duration_statement = 0`, `track_io_timing = on` (logs every query for full pgBadger workload profiling).

Additionally, manual/periodic inspection tools (`pgMustard` single-plan `EXPLAIN ANALYZE BUFFERS`, `postgresqltuner` one-shot SQL diagnostic pass, and `dbForge Studio` query profiler session) are documented for active-session vs. passive overhead.
