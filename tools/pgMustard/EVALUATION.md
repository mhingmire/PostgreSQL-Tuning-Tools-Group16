# Tool Evaluation: pgMustard

- **Evaluators:** Assigned across P1, P2, P3 (cross-reviewed)
- **Tool Category:** Web-Based PostgreSQL Query Execution Plan Analyzer
- **Official Site:** https://www.pgmustard.com/

## 1. Purpose and Architecture
pgMustard is a web-based (SaaS) execution plan analyzer that evaluates `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` outputs from PostgreSQL. Users submit query text and JSON query plans manually via the browser UI (or API on paid tiers); pgMustard scores plan nodes, highlights time/cost/buffer bottlenecks, and provides plain-English tuning tips.

## 2. Installation and Setup
- **No database agent or server installation required.**
- **Constraint:** pgMustard is a web-based tool requiring **manual submission** of execution plans. Do NOT create accounts or start paid trials without explicit group confirmation; check free-tier/demo limits before testing.
- **Export Plans for Submission:** Run `python tools/pgMustard/export_explain_plans.py` to generate clean `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` files for each scenario probe query.

## 3. Data Sources
- Single-query `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` outputs (plus optional SQL query text). Does not connect directly to PostgreSQL or read server logs/system catalogs.

## 4. Features Tested
- [ ] Visual plan tree & node timing attribution
- [ ] Efficiency scoring (rows removed by filter, read amplification, spill detection)
- [ ] Index recommendation tips (`S01`, `S06`)
- [ ] External disk sort / hash batch spill detection (`S07`, `S08`)
- [ ] Buffer hit vs. disk read analysis (`S04` bloat impact on scan buffers)

## 5. Four Core Evaluation Criteria
1. **Bottleneck Identification:** _TBD after manual plan submissions_
2. **Index Analysis:** _TBD (per-query missing/non-SARGable index tips; cannot detect unused/duplicate indexes globally)_
3. **Tuning Recommendations:** _TBD_
4. **Reporting:** _TBD (plan share links, tip prioritization)_

## 6. Experimental Observations (Scenarios S01–S08)
| Scenario | Observed in pgMustard? | Plan Tips / Findings | Notes |
|---|---|---|---|
| S01 (Missing index) | TBD | | |
| S02 (Duplicate indexes) | TBD | | |
| S03 (Unused indexes) | TBD | | |
| S04 (Table bloat) | TBD | | |
| S05 (Poor config) | TBD | | |
| S06 (Slow seq scans) | TBD | | |
| S07 (Inefficient joins) | TBD | | |
| S08 (Sorting & temp files) | TBD | | |

## 7. Ground-Truth Detection Score
- **Score:** `TBD / 16`

## 8. Screenshots and Raw Outputs
- Exported JSON plans: `tools/pgMustard/exported_plans/`
- Screenshots of pgMustard web analysis: `reports/screenshots/pgmustard_*.png`

## 9. Setup Effort
- _TBD (expected minimal setup effort since no local install, though manual plan export/paste adds workflow friction)._

## 10. Cost and Licensing
- **License:** Commercial SaaS (free limited evaluations / paid monthly subscription per user/team).
- **Important Note:** Record exact tier/limits observed at evaluation time; never claim paid-tier features were tested unless actually licensed and tested.

## 11. Limitations
- Operates on one query execution plan at a time; no workload-wide log aggregation or catalog-level health checks.
- Cannot detect duplicate indexes (`S02`), unused indexes (`S03`), or checkpoint misconfigurations (`S05` checkpoints).
- Requires manual submission of `EXPLAIN` JSON to an external web service (potential privacy considerations for production SQL/plans).

## 12. Final Assessment
- _TBD after completing `S01`–`S08` and before/after optimization verification._
