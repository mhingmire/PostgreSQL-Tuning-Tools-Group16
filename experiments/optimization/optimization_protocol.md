# Optimization & Before/After Validation Protocol

1. **Record Before-State:** Run `python workload/benchmark_scripts/run_benchmark.py --label before_opt --workload custom_orders --runs 3` against the scenario or baseline under study.
2. **Apply Candidate Optimization:** Apply only the recommended change (e.g., `experiments/optimization/01_apply_optimizations.sql` or a single-scenario fix).
3. **Warm Cache Consistency:** Perform identical benchmark iterations (`--runs 3`, identical `--clients`, `--threads`, `--duration`, and `--query-repeats`).
4. **Record After-State:** Run `python workload/benchmark_scripts/run_benchmark.py --label after_opt --workload custom_orders --runs 3`.
5. **Compute Deltas:** Run `python results/comparison/compare_before_after.py --before results/processed/<before>.json --after results/processed/<after>.json`.
6. **Verify No Regression on Writes:** Re-check `INSERT`/`UPDATE` TPS and index bloat/size before accepting a recommendation.
7. **Restore Baseline:** Run `experiments/optimization/02_revert_optimizations.sql` before moving to the next experiment.
