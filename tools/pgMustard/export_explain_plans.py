"""Export EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) files for manual submission to pgMustard."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "workload" / "benchmark_scripts"))
from run_benchmark import CUSTOM_BENCHMARK_QUERIES  # noqa: E402


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")
    container = os.getenv("POSTGRES_CONTAINER", "tuning_lab_pg17")
    db = os.getenv("POSTGRES_DB", "tuning_lab")
    user = os.getenv("POSTGRES_USER", "projectuser")

    out_dir = REPO_ROOT / "tools" / "pgMustard" / "exported_plans"
    out_dir.mkdir(parents=True, exist_ok=True)

    for q in CUSTOM_BENCHMARK_QUERIES:
        explain_sql = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {q['sql']}"
        proc = subprocess.run(
            ["docker", "exec", container, "psql", "-U", user, "-d", db, "-At", "-c", explain_sql],
            capture_output=True,
            text=True,
            check=True,
        )
        out_file = out_dir / f"{q['id']}_explain.json"
        out_file.write_text(proc.stdout.strip() + "\n", encoding="utf-8")
        print(f"Exported {out_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
