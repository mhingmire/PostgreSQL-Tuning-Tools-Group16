"""Measure monitoring and logging overhead across observability configurations.

Compares identical pgbench runs under:
  1. minimal_obs: log_min_duration_statement = -1, track_io_timing = off
  2. stats_only:  log_min_duration_statement = 1000, track_io_timing = on
  3. full_pgbadger: log_min_duration_statement = 0, track_io_timing = on (full query logging)

Always restores the baseline configuration via ALTER SYSTEM RESET + pg_reload_conf().
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "workload" / "benchmark_scripts"))
from run_benchmark import run_pgbench_iteration, reset_pg_stats, run_psql_exec  # noqa: E402


PROFILES = [
    {
        "name": "minimal_obs",
        "sql": [
            "ALTER SYSTEM SET log_min_duration_statement = -1;",
            "ALTER SYSTEM SET track_io_timing = off;",
            "ALTER SYSTEM SET log_checkpoints = off;",
            "ALTER SYSTEM SET log_lock_waits = off;",
            "SELECT pg_reload_conf();",
        ],
    },
    {
        "name": "stats_and_slow_logs",
        "sql": [
            "ALTER SYSTEM SET log_min_duration_statement = 200;",
            "ALTER SYSTEM SET track_io_timing = on;",
            "ALTER SYSTEM SET log_checkpoints = on;",
            "ALTER SYSTEM SET log_lock_waits = on;",
            "SELECT pg_reload_conf();",
        ],
    },
    {
        "name": "full_pgbadger_logging",
        "sql": [
            "ALTER SYSTEM SET log_min_duration_statement = 0;",
            "ALTER SYSTEM SET track_io_timing = on;",
            "ALTER SYSTEM SET log_checkpoints = on;",
            "ALTER SYSTEM SET log_lock_waits = on;",
            "SELECT pg_reload_conf();",
        ],
    },
]

RESTORE_SQL = """
ALTER SYSTEM RESET log_min_duration_statement;
ALTER SYSTEM RESET track_io_timing;
ALTER SYSTEM RESET log_checkpoints;
ALTER SYSTEM RESET log_lock_waits;
SELECT pg_reload_conf();
"""


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    parser = argparse.ArgumentParser(description="Measure PostgreSQL monitoring/logging overhead.")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--duration", type=int, default=20)
    parser.add_argument("--clients", type=int, default=int(os.getenv("PGBENCH_CLIENTS", "10")))
    parser.add_argument("--threads", type=int, default=int(os.getenv("PGBENCH_THREADS", "2")))
    args = parser.parse_args()

    container = os.getenv("POSTGRES_CONTAINER", "tuning_lab_pg17")
    db = os.getenv("POSTGRES_DB", "tuning_lab")
    user = os.getenv("POSTGRES_USER", "projectuser")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_raw = REPO_ROOT / "results" / "raw" / f"overhead_{stamp}"
    out_proc = REPO_ROOT / "results" / "processed"
    out_raw.mkdir(parents=True, exist_ok=True)
    out_proc.mkdir(parents=True, exist_ok=True)

    summary_rows = []
    try:
        for profile in PROFILES:
            print(f"=== Measuring profile: {profile['name']} ===")
            run_psql_exec(container, user, db, " ".join(profile["sql"]))
            profile_dir = out_raw / profile["name"]
            profile_dir.mkdir(parents=True, exist_ok=True)

            tps_list = []
            avg_lat_list = []
            p95_lat_list = []
            for r in range(1, args.runs + 1):
                reset_pg_stats(container, user, db)
                metrics = run_pgbench_iteration(
                    container=container,
                    user=user,
                    db=db,
                    clients=args.clients,
                    threads=args.threads,
                    duration=args.duration,
                    workload_mode="custom_orders",
                    raw_dir=profile_dir,
                    run_idx=r,
                )
                tps_list.append(metrics["tps"])
                avg_lat_list.append(metrics["latency_avg_ms"])
                p95_lat_list.append(metrics["latency_p95_ms"])

            summary_rows.append(
                {
                    "profile": profile["name"],
                    "runs": args.runs,
                    "tps_mean": round(sum(tps_list) / len(tps_list), 3),
                    "latency_avg_ms_mean": round(sum(avg_lat_list) / len(avg_lat_list), 3),
                    "latency_p95_ms_mean": round(sum(p95_lat_list) / len(p95_lat_list), 3),
                }
            )
    finally:
        print("Restoring baseline observability configuration...")
        run_psql_exec(container, user, db, RESTORE_SQL)

    out_json = out_proc / f"overhead_{stamp}.json"
    out_csv = out_proc / f"overhead_{stamp}.csv"
    out_json.write_text(json.dumps(summary_rows, indent=2), encoding="utf-8")
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)

    print(f"Overhead results saved to {out_json} and {out_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
