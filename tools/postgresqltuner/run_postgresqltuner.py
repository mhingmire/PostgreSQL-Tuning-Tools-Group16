"""Helper to run postgresqltuner.pl using Perl or Docker and save output to reports/tool_reports/."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / ".env")

    parser = argparse.ArgumentParser(description="Run postgresqltuner against tuning_lab.")
    parser.add_argument("--label", default="baseline", help="Scenario label for saved report")
    parser.add_argument(
        "--script-path",
        type=Path,
        default=repo_root / "tools" / "postgresqltuner" / "postgresqltuner.pl",
        help="Path to postgresqltuner.pl (download from https://github.com/jfcoz/postgresqltuner)",
    )
    args = parser.parse_args()

    if not args.script_path.exists():
        print(
            f"postgresqltuner.pl not found at {args.script_path}.\n"
            "Download it via:\n"
            "  curl -fsSL https://raw.githubusercontent.com/jfcoz/postgresqltuner/master/postgresqltuner.pl "
            "-o tools/postgresqltuner/postgresqltuner.pl"
        )
        return 1

    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "tuning_lab")
    user = os.getenv("POSTGRES_USER", "projectuser")
    password = os.getenv("POSTGRES_PASSWORD", "")

    perl_bin = shutil.which("perl")
    if not perl_bin:
        print("Perl not found on host PATH. Run inside WSL or a Perl container with DBD::Pg installed.")
        return 1

    env = os.environ.copy()
    env["PGPASSWORD"] = password
    cmd = [
        perl_bin,
        str(args.script_path),
        "--host", host,
        "--port", str(port),
        "--user", user,
        "--database", db,
        "--ssd",
    ]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True, check=False)

    out_dir = repo_root / "reports" / "tool_reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = out_dir / f"postgresqltuner_{args.label}_{stamp}.txt"
    out_file.write_text(proc.stdout + "\n" + proc.stderr, encoding="utf-8")
    print(f"Saved postgresqltuner output to {out_file} (exit code {proc.returncode})")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
