"""Convenience wrapper to execute the standardized 3-run baseline benchmark."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    runner = repo_root / "workload" / "benchmark_scripts" / "run_benchmark.py"
    cmd = [
        sys.executable,
        str(runner),
        "--label",
        "baseline_clean",
        "--workload",
        "custom_orders",
        "--runs",
        "3",
        *sys.argv[1:],
    ]
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
