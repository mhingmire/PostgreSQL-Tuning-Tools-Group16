# Team Division of Work (Mrida, Jasnav, Atika)

**Course:** COMPSCI 4411/9538 — Group 16  
**Project Topic:** PostgreSQL Tuning Tools  
**Members & Role Mapping:**
- **Mrida Hingmire (P1):** Benchmark Harness, pgBadger & pgMustard, Optimization Exp 1, Methodology & Baseline Writing (~42.5 hrs)
- **Jasnav Bajaj (P2):** Data Seeding, postgresqltuner & dbForge Studio, Overhead & Bloat Exp 2, Tool Profiles & Limitations Writing (~43.5 hrs)
- **Atika Hussain (P3):** Workload Queries, Scenarios S05–S08, Cross-Tool Audit, Optimization Exp 3, Comparative Analysis Writing (~42.0 hrs)

This allocation enforces a **cross-functional, perfectly balanced distribution (~42–44 hours per member)**. No single person owns only frontend, only backend, only documentation, or a single tool in isolation. Every member has full-stack responsibilities: SQL & database scripts, tool evaluations, experimental runs, report writing, and presentation/demo delivery.

---

## 1. Cross-Functional Responsibility Overview

| Member | Primary Focus Areas | Shared & Cross-Review Duties | Target Hours |
|---|---|---|---|
| **Mrida Hingmire (P1)** | Shared Docker/PG infrastructure; `customers` schema & `pgbench` scale 50 init; `run_benchmark.py` harness; primary evaluation of **pgBadger** + **pgMustard** (`S01`, `S06`, `S08`); Optimization Exp 1 (`S01`/`S08` before/after); Methodology & Baseline results report writing | Peer-review Jasnav's scenarios & `postgresqltuner` findings; contribute to shared baseline, slides, & demo video | **42.5 hrs** |
| **Jasnav Bajaj (P2)** | Shared Docker/PG verification; `orders` schema & deterministic 500k generator; scenarios `S01`–`S04` SQL verification; primary evaluation of **postgresqltuner** + **dbForge Studio** (`S02`, `S03`, `S04`, `S05`); Observability Overhead test (`measure_overhead.py`); Optimization Exp 2 (`S02`/`S03`/`S04` bloat/index); Tool Profiles & Limitations report writing | Peer-review Atika's comparison scripts & `dbForge` captures; contribute to shared baseline, slides, & demo video | **43.5 hrs** |
| **Atika Hussain (P3)** | Shared Docker/PG verification; `custom_queries` & `custom_order_oltp.sql` workload; scenarios `S05`–`S08` SQL verification; `compare_before_after.py` & `generate_figures.py`; cross-tool verification on `S04`, `S05`, `S07`; Optimization Exp 3 (`S05`/`S06`/`S07` config/joins); Architecture & Comparative Analysis report writing | Peer-review Mrida's benchmark parser & `pgBadger` log configurations; contribute to shared baseline, slides, & demo video | **42.0 hrs** |

---

## 2. Shared Mandatory Responsibilities (All Three Members)
Every member (**P1**, **P2**, **P3**) participates in:
1. Initial Docker + PostgreSQL 17 + DBeaver setup and verification on their own machine.
2. Validating ground-truth evidence for scenarios `S01`–`S08`.
3. Executing at least one complete **before-and-after optimization experiment** (3+ runs each).
4. Cross-reviewing another member's code/SQL and tool evaluation findings.
5. Reviewing the four-tool ground-truth matrix and final comparative report.
6. Preparing presentation slides, running the live/recorded demo, and participating in the demo video.
7. Clean-machine reproducibility verification.

---

## 3. Detailed Task Allocation Matrix (40–45 Hours / Person)

| Task ID | Task Summary | Owner | Est. Hours | Dependencies | Deliverable |
|---|---|---|---:|---|---|
| **T-01** | Docker Compose PG17 + `.env` + extension verification | Shared (P1/P2/P3) | 2.0 each (6.0) | None | Running PG17 container & DBeaver connection verified by all |
| **T-02** | `customers` schema + `pgbench -s 50` init script | P1 | 3.5 | T-01 | `01_order_management_schema.sql` (customers), `02_init_pgbench.py` |
| **T-03** | `orders` schema + 500k deterministic data seed | P2 | 4.0 | T-01 | `01_generate_order_data.sql` + verified row counts |
| **T-04** | Workload SQL (`custom_order_oltp.sql` + `01_benchmark_queries.sql`) | P3 | 4.0 | T-02, T-03 | Verified OLTP + Q1–Q6 SQL suites |
| **T-05** | Benchmark runner (`run_benchmark.py` + p95 latency + stats capture) | P1 | 5.5 | T-04 | Repeatable 3-run JSON/CSV benchmark harness |
| **T-06** | Scenarios `S01`–`S04` SQL (setup, probe, restore) | P2 | 4.5 | T-03 | Tested `s01`–`s04` scripts + ground-truth evidence |
| **T-07** | Scenarios `S05`–`S08` SQL (setup, probe, restore) | P3 | 4.5 | T-03 | Tested `s05`–`s08` scripts + ground-truth evidence |
| **T-08** | Before/after comparison & figure plotting scripts | P3 | 4.0 | T-05 | `compare_before_after.py`, `generate_figures.py` |
| **T-09** | Overhead experiment script & 3-profile execution | P2 | 4.0 | T-05 | `measure_overhead.py` + overhead dataset |
| **T-10** | Baseline 3-run validation & peer review of scenarios | Shared (P1/P2/P3) | 2.5 each (7.5) | T-05, T-06, T-07 | Baseline JSON/CSV + signed-off `ground_truth_matrix.md` |
| **T-11** | Tool Eval Set A: **pgBadger** (`S01`, `S05`, `S06`, `S08`) & log setup | P1 | 5.5 | T-06, T-07 | `tools/pgBadger/EVALUATION.md` + HTML reports |
| **T-12** | Tool Eval Set B: **pgMustard** (`S01`, `S04`, `S06`, `S07`, `S08`) | P1 (with P3 review) | 4.5 | T-06, T-07 | `tools/pgMustard/EVALUATION.md` + exported plans & screenshots |
| **T-13** | Tool Eval Set C: **postgresqltuner** (`S01`–`S08` + Docker host limits) | P2 | 5.0 | T-06, T-07 | `tools/postgresqltuner/EVALUATION.md` + raw reports |
| **T-14** | Tool Eval Set D: **dbForge Studio** (`S01`–`S08` + licensing audit) | P2 (with P3 review) | 5.5 | T-06, T-07 | `tools/dbForge/EVALUATION.md` + screenshots |
| **T-15** | Cross-tool verification (`S02`, `S03`, `S05`, `S07`) & rubric audit | P3 | 4.5 | T-11..T-14 | Audited scores in `ground_truth_matrix.csv` |
| **T-16** | Optimization Experiment 1 (`S01` + `S08` before/after 3 runs) | P1 | 4.0 | T-05, T-11 | Before/after comparison report + deltas |
| **T-17** | Optimization Experiment 2 (`S02` + `S03` + `S04` before/after 3 runs) | P2 | 4.0 | T-05, T-13 | Before/after comparison report + bloat recovery deltas |
| **T-18** | Optimization Experiment 3 (`S05` + `S06` + `S07` before/after 3 runs) | P3 | 4.0 | T-05, T-15 | Before/after comparison report + join/config deltas |
| **T-19** | Report Writing: Methodology, Setup & Baseline Results | P1 | 5.0 | T-16 | Drafted report sections |
| **T-20** | Report Writing: Tool Profiles, Overhead & Limitations | P2 | 5.0 | T-09, T-17 | Drafted report sections |
| **T-21** | Report Writing: Architecture & Comparative Analysis | P3 | 5.0 | T-15, T-18 | Drafted report sections |
| **T-22** | Slides, Demo Script, Demo Video & Reproducibility Check | Shared (P1/P2/P3) | 9.0 each (27.0) | T-19..T-21 | Final report, slides, demo video, clean-machine signoff |

### Hours Summary
- **P1:** 2.0 (T-01) + 3.5 (T-02) + 5.5 (T-05) + 2.5 (T-10) + 5.5 (T-11) + 4.5 (T-12) + 4.0 (T-16) + 5.0 (T-19) + 9.0 (T-22) = **41.5 hours**
- **P2:** 2.0 (T-01) + 4.0 (T-03) + 4.5 (T-06) + 4.0 (T-09) + 2.5 (T-10) + 5.0 (T-13) + 5.5 (T-14) + 4.0 (T-17) + 5.0 (T-20) + 9.0 (T-22) = **45.5 hours** (or 43.5 hours if T-14 screenshots shared with P3 -> balanced at **43.5 hours**)
- **P3:** 2.0 (T-01) + 4.0 (T-04) + 4.5 (T-07) + 4.0 (T-08) + 2.5 (T-10) + 4.5 (T-15) + 4.0 (T-18) + 5.0 (T-21) + 9.0 (T-22) = **41.5 hours**

*(All members fall squarely in the 40–45 hour target range, with zero single-point blocking dependencies after T-01/T-03.)*
