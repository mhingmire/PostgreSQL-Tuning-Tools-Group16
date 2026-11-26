"""Compare before-and-after processed benchmark summaries and export Markdown + CSV deltas."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


def pct_change(before: float, after: float) -> float:
    if before == 0:
        return 0.0
    return round(((after - before) / before) * 100.0, 2)


def build_comparison(before_data: dict[str, Any], after_data: dict[str, Any]) -> dict[str, Any]:
    b_agg = before_data["aggregate_metrics"]
    a_agg = after_data["aggregate_metrics"]

    metrics = [
        ("TPS (higher is better)", "tps_mean", True),
        ("Average Latency ms (lower is better)", "latency_avg_ms_mean", False),
        ("p95 Latency ms (lower is better)", "latency_p95_ms_mean", False),
        ("Cache Hit Ratio % (higher is better)", "cache_hit_ratio_pct_mean", True),
        ("Shared Blocks Hit (mean)", "blks_hit_mean", True),
        ("Shared Blocks Read (lower is better)", "blks_read_mean", False),
        ("Temp Bytes (lower is better)", "temp_bytes_mean", False),
    ]

    aggregate_rows = []
    for label, key, higher_better in metrics:
        b_val = float(b_agg.get(key, 0.0))
        a_val = float(a_agg.get(key, 0.0))
        delta_pct = pct_change(b_val, a_val)
        improved = (a_val > b_val) if higher_better else (a_val < b_val)
        aggregate_rows.append(
            {
                "metric": label,
                "before": b_val,
                "after": a_val,
                "delta_pct": delta_pct,
                "improved": improved,
            }
        )

    query_rows = []
    b_queries = before_data.get("custom_query_summary", {})
    a_queries = after_data.get("custom_query_summary", {})
    for qid in sorted(set(b_queries) | set(a_queries)):
        b_ms = float(b_queries.get(qid, {}).get("mean_exec_ms", 0.0))
        a_ms = float(a_queries.get(qid, {}).get("mean_exec_ms", 0.0))
        query_rows.append(
            {
                "query_id": qid,
                "before_ms": b_ms,
                "after_ms": a_ms,
                "delta_pct": pct_change(b_ms, a_ms),
                "before_blks_read": float(b_queries.get(qid, {}).get("avg_shared_blks_read", 0.0)),
                "after_blks_read": float(a_queries.get(qid, {}).get("avg_shared_blks_read", 0.0)),
            }
        )

    return {
        "before_label": before_data["label"],
        "after_label": after_data["label"],
        "aggregate_comparison": aggregate_rows,
        "query_comparison": query_rows,
    }


def write_markdown(comp: dict[str, Any], out_md: Path) -> None:
    lines = [
        f"# Before vs. After Performance Comparison: `{comp['before_label']}` -> `{comp['after_label']}`",
        "",
        "## Workload Aggregate Metrics",
        "",
        "| Metric | Before | After | Delta (%) | Improved? |",
        "|---|---:|---:|---:|:---:|",
    ]
    for row in comp["aggregate_comparison"]:
        lines.append(
            f"| {row['metric']} | {row['before']:.3f} | {row['after']:.3f} | "
            f"{row['delta_pct']:+.2f}% | {'Yes' if row['improved'] else 'No'} |"
        )

    lines.extend(
        [
            "",
            "## Individual Query Execution Time & Buffer Reads",
            "",
            "| Query ID | Before Mean (ms) | After Mean (ms) | Delta (%) | Before Blks Read | After Blks Read |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in comp["query_comparison"]:
        lines.append(
            f"| `{row['query_id']}` | {row['before_ms']:.3f} | {row['after_ms']:.3f} | "
            f"{row['delta_pct']:+.2f}% | {row['before_blks_read']:.1f} | {row['after_blks_read']:.1f} |"
        )
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_csv(comp: dict[str, Any], out_csv: Path) -> None:
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["metric", "before", "after", "delta_pct", "improved"])
        writer.writeheader()
        writer.writerows(comp["aggregate_comparison"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two processed benchmark summary JSON files.")
    parser.add_argument("--before", required=True, type=Path, help="Path to before summary JSON")
    parser.add_argument("--after", required=True, type=Path, help="Path to after summary JSON")
    parser.add_argument("--out-prefix", default=None, help="Output filename prefix inside results/comparison/")
    args = parser.parse_args()

    before_data = json.loads(args.before.read_text(encoding="utf-8"))
    after_data = json.loads(args.after.read_text(encoding="utf-8"))
    comp = build_comparison(before_data, after_data)

    comp_dir = Path(__file__).resolve().parent
    prefix = args.out_prefix or f"{before_data['label']}_vs_{after_data['label']}"
    out_md = comp_dir / f"{prefix}.md"
    out_csv = comp_dir / f"{prefix}.csv"
    out_json = comp_dir / f"{prefix}.json"

    write_markdown(comp, out_md)
    write_csv(comp, out_csv)
    out_json.write_text(json.dumps(comp, indent=2), encoding="utf-8")

    print(f"Comparison written to:\n  {out_md}\n  {out_csv}\n  {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
