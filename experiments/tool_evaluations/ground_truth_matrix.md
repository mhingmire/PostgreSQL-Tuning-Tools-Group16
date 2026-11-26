# Ground-Truth Evaluation Matrix

All four PostgreSQL tuning tools are scored against the exact same controlled scenarios (`S01`–`S08`) using a 0–2 detection scale per scenario:
- **2 – Full Detection & Actionable Diagnosis:** Tool identifies the root cause and provides an accurate, actionable recommendation.
- **1 – Partial Detection:** Tool surfaces a symptom (e.g., slow query or high I/O) without pinpointing the specific root cause or remediation.
- **0 – Not Detected / Out of Scope:** Tool does not detect the issue (e.g., log-only analyzers cannot inspect unused indexes).

| Scenario | Problem | Key Ground-Truth Evidence | pgBadger | pgMustard | dbForge Studio | postgresqltuner |
|---|---|---|---:|---:|---:|---:|
| **S01** | Missing index (`orders.order_status`, `order_date`) | `Seq Scan` + high `seq_tup_read` + slow logs | TBD | TBD | TBD | TBD |
| **S02** | Duplicate indexes (`orders.customer_id`) | Identical `pg_index.indkey` definitions | TBD | TBD | TBD | TBD |
| **S03** | Unused indexes (`idx_scan = 0`) | `pg_stat_user_indexes.idx_scan = 0` | TBD | TBD | TBD | TBD |
| **S04** | Table bloat (`orders` dead tuples) | `n_dead_tup` + `pgstattuple('orders')` | TBD | TBD | TBD | TBD |
| **S05** | Poor configuration settings | `pg_settings` + `pg_stat_checkpointer` | TBD | TBD | TBD | TBD |
| **S06** | Slow sequential scans (non-SARGable) | `Seq Scan` + `Rows Removed by Filter` | TBD | TBD | TBD | TBD |
| **S07** | Inefficient joins (cast + hash spill) | `Hash Join` `Batches > 1` + temp blocks | TBD | TBD | TBD | TBD |
| **S08** | Sorting & temporary-file activity | `external merge Disk` + `log_temp_files` | TBD | TBD | TBD | TBD |
| **Total** | **Max Score: 16** | | **TBD / 16** | **TBD / 16** | **TBD / 16** | **TBD / 16** |

## Four Core Evaluation Criteria Rubric (1–5 Scale)
1. **Bottleneck Identification:** Ability to surface slow queries, I/O waits, checkpoints, locks, and temp spills accurately.
2. **Index Analysis:** Detection of missing, duplicate, redundant, and unused indexes.
3. **Tuning Recommendations:** Specificity, safety, and empirical accuracy of suggested fixes (verified via before/after benchmarks).
4. **Reporting:** Clarity, exportability (HTML/PDF/JSON), visualization quality, and suitability for team workflows.
