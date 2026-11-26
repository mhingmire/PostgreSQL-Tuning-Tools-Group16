"""Repeatable PostgreSQL benchmarking framework for Group 16.

Runs pgbench (standard TPC-B-like or custom order-management workload) and
standardized analytical/OLTP queries across >=3 runs, captures TPS, average
latency, p95 latency, individual query execution time, buffer hits/reads, and
PostgreSQL statistics, and writes raw and processed outputs separately.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import statistics
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


CUSTOM_BENCHMARK_QUERIES: list[dict[str, str]] = [
    {
        "id": "Q1_status_date_filter",
        "sql": (
            "SELECT order_id, customer_id, order_date, total_amount "
            "FROM orders "
            "WHERE order_status = 'RETURNED' "
            "  AND order_date >= TIMESTAMPTZ '2025-01-01 00:00:00+00' "
            "ORDER BY order_date DESC LIMIT 100"
        ),
    },
    {
        "id": "Q2_priority_cancelled_agg",
        "sql": (
            "SELECT COUNT(*) AS cancelled_priority_cnt, COALESCE(SUM(total_amount), 0) AS cancelled_total "
            "FROM orders "
            "WHERE order_status = 'CANCELLED' AND priority_flag = TRUE"
        ),
    },
    {
        "id": "Q3_region_segment_join",
        "sql": (
            "SELECT c.region, c.segment, COUNT(o.order_id) AS orders_cnt, ROUND(AVG(o.total_amount), 2) AS avg_order "
            "FROM customers c JOIN orders o ON o.customer_id = c.customer_id "
            "WHERE o.order_date >= TIMESTAMPTZ '2024-07-01 00:00:00+00' "
            "GROUP BY c.region, c.segment ORDER BY orders_cnt DESC"
        ),
    },
    {
        "id": "Q4_customer_email_lookup",
        "sql": (
            "SELECT customer_id, full_name, email, segment "
            "FROM customers WHERE email = 'customer12345@tuninglab-demo.example'"
        ),
    },
    {
        "id": "Q5_region_top_orders_sort",
        "sql": (
            "SELECT order_id, customer_id, total_amount, order_date "
            "FROM orders WHERE shipping_region = 'NORTH' "
            "ORDER BY total_amount DESC, order_date DESC LIMIT 250"
        ),
    },
    {
        "id": "Q6_vip_top_spenders",
        "sql": (
            "SELECT c.customer_id, c.full_name, COUNT(o.order_id) AS order_cnt, SUM(o.total_amount) AS lifetime_spend "
            "FROM customers c JOIN orders o ON o.customer_id = c.customer_id "
            "WHERE c.segment = 'VIP' AND o.order_status = 'DELIVERED' "
            "GROUP BY c.customer_id, c.full_name ORDER BY lifetime_spend DESC LIMIT 25"
        ),
    },
]


def percentile(sorted_values: list[float], pct: float) -> float:
    """Compute linear-interpolated percentile on a pre-sorted list."""
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    rank = (pct / 100.0) * (len(sorted_values) - 1)
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return sorted_values[low]
    weight = rank - low
    return sorted_values[low] * (1.0 - weight) + sorted_values[high] * weight


def run_psql_json(container: str, user: str, db: str, sql: str) -> Any:
    """Execute a SQL statement returning a single JSON payload via psql."""
    wrapped = f"SELECT COALESCE(json_agg(t), '[]'::json) FROM ({sql}) AS t;"
    cmd = ["docker", "exec", container, "psql", "-U", user, "-d", db, "-At", "-c", wrapped]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(proc.stdout.strip() or "[]")


def run_psql_exec(container: str, user: str, db: str, sql: str) -> str:
    """Execute a SQL statement via psql and return stdout."""
    cmd = ["docker", "exec", container, "psql", "-U", user, "-d", db, "-At", "-c", sql]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def reset_pg_stats(container: str, user: str, db: str) -> None:
    """Reset PostgreSQL cumulative statistics before a measurement run."""
    run_psql_exec(container, user, db, "SELECT pg_stat_reset(); SELECT pg_stat_statements_reset();")


def collect_db_stats(container: str, user: str, db: str) -> dict[str, Any]:
    """Snapshot key PostgreSQL performance counters and top statements."""
    db_row = run_psql_json(
        container,
        user,
        db,
        """
        SELECT
            datname,
            xact_commit,
            xact_rollback,
            blks_read,
            blks_hit,
            ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 4) AS cache_hit_ratio_pct,
            temp_files,
            temp_bytes,
            deadlocks,
            blk_read_time,
            blk_write_time
        FROM pg_stat_database
        WHERE datname = current_database()
        """,
    )
    table_rows = run_psql_json(
        container,
        user,
        db,
        """
        SELECT
            relname,
            seq_scan,
            seq_tup_read,
            idx_scan,
            idx_tup_fetch,
            n_live_tup,
            n_dead_tup,
            pg_total_relation_size(relid) AS total_bytes
        FROM pg_stat_user_tables
        ORDER BY relname
        """,
    )
    stmt_rows = run_psql_json(
        container,
        user,
        db,
        """
        SELECT
            queryid::TEXT AS queryid,
            calls,
            ROUND(total_exec_time::NUMERIC, 3) AS total_exec_ms,
            ROUND(mean_exec_time::NUMERIC, 3) AS mean_exec_ms,
            rows,
            shared_blks_hit,
            shared_blks_read,
            temp_blks_written,
            LEFT(REGEXP_REPLACE(query, '\s+', ' ', 'g'), 140) AS query_snippet
        FROM pg_stat_statements
        WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
        ORDER BY total_exec_time DESC
        LIMIT 20
        """,
    )
    return {
        "database": db_row[0] if db_row else {},
        "tables": table_rows,
        "top_statements": stmt_rows,
    }


def parse_pgbench_output(stdout: str, tx_latencies_ms: list[float]) -> dict[str, Any]:
    """Parse TPS and average latency from pgbench stdout plus p95 from per-tx log."""
    tps_match = re.search(r"tps\s*=\s*([0-9.]+)\s*\(without initial connection time\)", stdout)
    if not tps_match:
        tps_match = re.search(r"tps\s*=\s*([0-9.]+)", stdout)
    lat_match = re.search(r"latency average\s*=\s*([0-9.]+)\s*ms", stdout)
    tx_match = re.search(r"number of transactions actually processed:\s*(\d+)", stdout)

    sorted_lats = sorted(tx_latencies_ms)
    return {
        "transactions_processed": int(tx_match.group(1)) if tx_match else len(sorted_lats),
        "tps": float(tps_match.group(1)) if tps_match else 0.0,
        "latency_avg_ms": float(lat_match.group(1)) if lat_match else (
            statistics.fmean(sorted_lats) if sorted_lats else 0.0
        ),
        "latency_p50_ms": round(percentile(sorted_lats, 50.0), 3),
        "latency_p95_ms": round(percentile(sorted_lats, 95.0), 3),
        "latency_p99_ms": round(percentile(sorted_lats, 99.0), 3),
        "logged_tx_samples": len(sorted_lats),
    }


def run_pgbench_iteration(
    container: str,
    user: str,
    db: str,
    clients: int,
    threads: int,
    duration: int,
    workload_mode: str,
    raw_dir: Path,
    run_idx: int,
) -> dict[str, Any]:
    """Run one pgbench iteration inside the container and copy raw tx logs out."""
    log_dir_in_container = f"/tmp/pgbench_run_{run_idx}"
    subprocess.run(
        ["docker", "exec", container, "sh", "-c", f"rm -rf {log_dir_in_container} && mkdir -p {log_dir_in_container}"],
        check=True,
    )

    pgbench_cmd = [
        "pgbench",
        "-c", str(clients),
        "-j", str(threads),
        "-T", str(duration),
        "-r",
        "-l",
        "--log-prefix", f"{log_dir_in_container}/tx",
        "-U", user,
    ]
    if workload_mode == "custom_orders":
        pgbench_cmd.extend(["-n", "-f", "/project/workload/pgbench/custom_order_oltp.sql"])
    pgbench_cmd.append(db)

    proc = subprocess.run(
        ["docker", "exec", container, *pgbench_cmd],
        capture_output=True,
        text=True,
        check=True,
    )

    raw_stdout_path = raw_dir / f"pgbench_run{run_idx}.txt"
    raw_stdout_path.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")

    tx_latencies_ms: list[float] = []
    local_tx_dir = raw_dir / f"pgbench_tx_run{run_idx}"
    local_tx_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["docker", "cp", f"{container}:{log_dir_in_container}/.", str(local_tx_dir)],
        check=True,
    )
    for log_file in local_tx_dir.glob("tx*"):
        with log_file.open("r", encoding="utf-8") as fh:
            for line in fh:
                parts = line.strip().split()
                if len(parts) >= 3:
                    # pgbench log column 3 (index 2) is transaction time in microseconds
                    try:
                        tx_latencies_ms.append(float(parts[2]) / 1000.0)
                    except ValueError:
                        continue

    subprocess.run(
        ["docker", "exec", container, "rm", "-rf", log_dir_in_container],
        check=True,
    )
    return parse_pgbench_output(proc.stdout, tx_latencies_ms)


def run_custom_queries_iteration(container: str, user: str, db: str, repeats: int = 3) -> list[dict[str, Any]]:
    """Execute each standardized query with EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)."""
    results: list[dict[str, Any]] = []
    for q in CUSTOM_BENCHMARK_QUERIES:
        exec_times: list[float] = []
        shared_hits: list[int] = []
        shared_reads: list[int] = []
        temp_written: list[int] = []
        top_node_type = ""

        for _ in range(repeats):
            explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {q['sql']}"
            cmd = ["docker", "exec", container, "psql", "-U", user, "-d", db, "-At", "-c", explain_sql]
            proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
            plan_json = json.loads(proc.stdout.strip())[0]
            plan = plan_json["Plan"]
            top_node_type = plan.get("Node Type", "")
            exec_times.append(float(plan_json.get("Execution Time", 0.0)))
            shared_hits.append(int(plan.get("Shared Hit Blocks", 0)))
            shared_reads.append(int(plan.get("Shared Read Blocks", 0)))
            temp_written.append(int(plan.get("Temp Written Blocks", 0)))

        sorted_times = sorted(exec_times)
        results.append(
            {
                "query_id": q["id"],
                "repeats": repeats,
                "top_node_type": top_node_type,
                "mean_exec_ms": round(statistics.fmean(exec_times), 3),
                "p95_exec_ms": round(percentile(sorted_times, 95.0), 3),
                "min_exec_ms": round(min(exec_times), 3),
                "max_exec_ms": round(max(exec_times), 3),
                "avg_shared_blks_hit": round(statistics.fmean(shared_hits), 1),
                "avg_shared_blks_read": round(statistics.fmean(shared_reads), 1),
                "avg_temp_blks_written": round(statistics.fmean(temp_written), 1),
            }
        )
    return results


def summarize_runs(
    label: str,
    workload_mode: str,
    params: dict[str, Any],
    run_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate across multiple benchmark repetitions (mean and stddev)."""
    tps_vals = [r["pgbench"]["tps"] for r in run_records]
    avg_lat_vals = [r["pgbench"]["latency_avg_ms"] for r in run_records]
    p95_lat_vals = [r["pgbench"]["latency_p95_ms"] for r in run_records]
    hit_ratios = [
        float(r["db_stats"]["database"].get("cache_hit_ratio_pct") or 0.0)
        for r in run_records
    ]
    blks_hit_vals = [int(r["db_stats"]["database"].get("blks_hit") or 0) for r in run_records]
    blks_read_vals = [int(r["db_stats"]["database"].get("blks_read") or 0) for r in run_records]
    temp_bytes_vals = [int(r["db_stats"]["database"].get("temp_bytes") or 0) for r in run_records]

    query_summary: dict[str, dict[str, Any]] = {}
    for q in CUSTOM_BENCHMARK_QUERIES:
        qid = q["id"]
        q_means = [
            qr["mean_exec_ms"]
            for r in run_records
            for qr in r["custom_queries"]
            if qr["query_id"] == qid
        ]
        q_hits = [
            qr["avg_shared_blks_hit"]
            for r in run_records
            for qr in r["custom_queries"]
            if qr["query_id"] == qid
        ]
        q_reads = [
            qr["avg_shared_blks_read"]
            for r in run_records
            for qr in r["custom_queries"]
            if qr["query_id"] == qid
        ]
        query_summary[qid] = {
            "mean_exec_ms": round(statistics.fmean(q_means), 3) if q_means else 0.0,
            "stddev_exec_ms": round(statistics.stdev(q_means), 3) if len(q_means) > 1 else 0.0,
            "avg_shared_blks_hit": round(statistics.fmean(q_hits), 1) if q_hits else 0.0,
            "avg_shared_blks_read": round(statistics.fmean(q_reads), 1) if q_reads else 0.0,
        }

    return {
        "label": label,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "workload_mode": workload_mode,
        "parameters": params,
        "runs_completed": len(run_records),
        "aggregate_metrics": {
            "tps_mean": round(statistics.fmean(tps_vals), 3),
            "tps_stddev": round(statistics.stdev(tps_vals), 3) if len(tps_vals) > 1 else 0.0,
            "latency_avg_ms_mean": round(statistics.fmean(avg_lat_vals), 3),
            "latency_p95_ms_mean": round(statistics.fmean(p95_lat_vals), 3),
            "cache_hit_ratio_pct_mean": round(statistics.fmean(hit_ratios), 3),
            "blks_hit_mean": round(statistics.fmean(blks_hit_vals), 1),
            "blks_read_mean": round(statistics.fmean(blks_read_vals), 1),
            "temp_bytes_mean": round(statistics.fmean(temp_bytes_vals), 1),
        },
        "custom_query_summary": query_summary,
        "per_run": run_records,
    }


def write_processed_csv(summary: dict[str, Any], csv_path: Path) -> None:
    """Write per-run and aggregate metrics to a flat CSV for analysis and plotting."""
    fieldnames = [
        "label",
        "run",
        "tps",
        "latency_avg_ms",
        "latency_p50_ms",
        "latency_p95_ms",
        "latency_p99_ms",
        "blks_hit",
        "blks_read",
        "cache_hit_ratio_pct",
        "temp_files",
        "temp_bytes",
        "wall_seconds",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for idx, run in enumerate(summary["per_run"], start=1):
            db = run["db_stats"]["database"]
            pgb = run["pgbench"]
            writer.writerow(
                {
                    "label": summary["label"],
                    "run": idx,
                    "tps": pgb["tps"],
                    "latency_avg_ms": pgb["latency_avg_ms"],
                    "latency_p50_ms": pgb["latency_p50_ms"],
                    "latency_p95_ms": pgb["latency_p95_ms"],
                    "latency_p99_ms": pgb["latency_p99_ms"],
                    "blks_hit": db.get("blks_hit", 0),
                    "blks_read": db.get("blks_read", 0),
                    "cache_hit_ratio_pct": db.get("cache_hit_ratio_pct", 0),
                    "temp_files": db.get("temp_files", 0),
                    "temp_bytes": db.get("temp_bytes", 0),
                    "wall_seconds": run["wall_seconds"],
                }
            )


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    parser = argparse.ArgumentParser(description="Run repeatable PostgreSQL tuning benchmarks.")
    parser.add_argument("--label", required=True, help="Experiment label, e.g., baseline_clean or after_s01_index")
    parser.add_argument("--workload", choices=["pgbench_tpcb", "custom_orders"], default="custom_orders")
    parser.add_argument("--runs", type=int, default=int(os.getenv("BENCHMARK_RUNS", "3")))
    parser.add_argument("--clients", type=int, default=int(os.getenv("PGBENCH_CLIENTS", "10")))
    parser.add_argument("--threads", type=int, default=int(os.getenv("PGBENCH_THREADS", "2")))
    parser.add_argument("--duration", type=int, default=int(os.getenv("PGBENCH_DURATION_SECONDS", "30")))
    parser.add_argument("--query-repeats", type=int, default=3, help="EXPLAIN ANALYZE repeats per custom query per run")
    args = parser.parse_args()

    if args.runs < 3:
        print("Warning: Project methodology requires at least 3 runs; proceeding with requested count.")

    container = os.getenv("POSTGRES_CONTAINER", "tuning_lab_pg17")
    db = os.getenv("POSTGRES_DB", "tuning_lab")
    user = os.getenv("POSTGRES_USER", "projectuser")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw_dir = repo_root / "results" / "raw" / f"{args.label}_{stamp}"
    processed_dir = repo_root / "results" / "processed"
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)

    run_records: list[dict[str, Any]] = []
    for run_idx in range(1, args.runs + 1):
        print(f"[{args.label}] Run {run_idx}/{args.runs} starting...")
        reset_pg_stats(container, user, db)
        t0 = time.perf_counter()

        pgbench_metrics = run_pgbench_iteration(
            container=container,
            user=user,
            db=db,
            clients=args.clients,
            threads=args.threads,
            duration=args.duration,
            workload_mode=args.workload,
            raw_dir=raw_dir,
            run_idx=run_idx,
        )
        custom_query_metrics = run_custom_queries_iteration(container, user, db, repeats=args.query_repeats)
        db_stats = collect_db_stats(container, user, db)
        wall_seconds = round(time.perf_counter() - t0, 3)

        run_payload = {
            "run": run_idx,
            "wall_seconds": wall_seconds,
            "pgbench": pgbench_metrics,
            "custom_queries": custom_query_metrics,
            "db_stats": db_stats,
        }
        (raw_dir / f"run{run_idx}_stats.json").write_text(
            json.dumps(run_payload, indent=2),
            encoding="utf-8",
        )
        run_records.append(run_payload)
        print(
            f"[{args.label}] Run {run_idx}/{args.runs} done: "
            f"TPS={pgbench_metrics['tps']:.2f}, avg={pgbench_metrics['latency_avg_ms']:.2f}ms, "
            f"p95={pgbench_metrics['latency_p95_ms']:.2f}ms"
        )

    summary = summarize_runs(
        label=args.label,
        workload_mode=args.workload,
        params={
            "clients": args.clients,
            "threads": args.threads,
            "duration_seconds": args.duration,
            "query_repeats": args.query_repeats,
            "pgbench_scale": int(os.getenv("PGBENCH_SCALE", "50")),
        },
        run_records=run_records,
    )

    json_out = processed_dir / f"{args.label}_{stamp}_summary.json"
    csv_out = processed_dir / f"{args.label}_{stamp}_summary.csv"
    json_out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_processed_csv(summary, csv_out)

    print(f"\nSaved raw outputs to:       {raw_dir}")
    print(f"Saved processed JSON to:    {json_out}")
    print(f"Saved processed CSV to:     {csv_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
