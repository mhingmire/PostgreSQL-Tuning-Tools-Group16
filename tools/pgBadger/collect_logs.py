"""Copy PostgreSQL log files from the Docker container for pgBadger analysis."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")
    container = os.getenv("POSTGRES_CONTAINER", "tuning_lab_pg17")

    dest_dir = repo_root / "logs" / "postgresql"
    dest_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        ["docker", "cp", f"{container}:/var/lib/postgresql/data/pgdata/log/.", str(dest_dir)],
        check=True,
    )
    logs = sorted(dest_dir.glob("*.log"))
    print(f"Copied {len(logs)} log file(s) to {dest_dir}:")
    for p in logs:
        print(f"  - {p.name} ({p.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
