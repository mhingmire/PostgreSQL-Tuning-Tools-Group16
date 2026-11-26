"""Initialize pgbench tables at scale factor 50 inside the PostgreSQL 17 Docker container."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from dotenv import load_dotenv


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    container = os.getenv("POSTGRES_CONTAINER", "tuning_lab_pg17")
    db = os.getenv("POSTGRES_DB", "tuning_lab")
    user = os.getenv("POSTGRES_USER", "projectuser")
    scale = os.getenv("PGBENCH_SCALE", "50")

    cmd = [
        "docker",
        "exec",
        container,
        "pgbench",
        "-i",
        "-s",
        str(scale),
        "-U",
        user,
        db,
    ]
    print(f"Initializing pgbench with scale factor {scale} in container '{container}'...")
    proc = subprocess.run(cmd, check=False)
    if proc.returncode != 0:
        print("Error: pgbench initialization failed.", file=sys.stderr)
        return proc.returncode

    verify_sql = (
        "SELECT relname AS table_name, n_live_tup AS estimated_rows, "
        "pg_size_pretty(pg_total_relation_size(relid)) AS total_size "
        "FROM pg_stat_user_tables WHERE relname LIKE 'pgbench_%' ORDER BY relname;"
    )
    subprocess.run(
        ["docker", "exec", container, "psql", "-U", user, "-d", db, "-c", verify_sql],
        check=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
