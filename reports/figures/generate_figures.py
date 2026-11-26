"""Generate comparison bar charts from processed benchmark JSON files (optional matplotlib)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt


def main() -> int:
    parser = argparse.ArgumentParser(description="Plot before-vs-after TPS and latency charts.")
    parser.add_argument("--comparison-json", required=True, type=Path)
    args = parser.parse_args()

    comp = json.loads(args.comparison_json.read_text(encoding="utf-8"))
    queries = comp.get("query_comparison", [])
    if not queries:
        print("No query_comparison rows found.")
        return 1

    labels = [q["query_id"] for q in queries]
    before_ms = [q["before_ms"] for q in queries]
    after_ms = [q["after_ms"] for q in queries]

    x = range(len(labels))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar([i - width / 2 for i in x], before_ms, width, label=comp["before_label"])
    ax.bar([i + width / 2 for i in x], after_ms, width, label=comp["after_label"])
    ax.set_ylabel("Mean Execution Time (ms)")
    ax.set_title(f"Query Execution Time: {comp['before_label']} vs {comp['after_label']}")
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=25, ha="right")
    ax.legend()
    plt.tight_layout()

    out_png = Path(__file__).resolve().parent / f"{comp['before_label']}_vs_{comp['after_label']}_queries.png"
    fig.savefig(out_png, dpi=150)
    print(f"Saved figure to {out_png}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
