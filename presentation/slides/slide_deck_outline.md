# Presentation Slide Deck Outline (COMPSCI 4411/9538 – Group 16)

1. **Title & Team:** PostgreSQL Tuning Tools Comparative Evaluation (Mrida Hingmire, Atika Hussain, Jasnav Bajaj)
2. **Motivation & Problem Statement:** Why comparing log analyzers, plan analyzers, IDEs, and catalog auditors requires controlled ground truth
3. **Lab Architecture & Datasets:** Docker PostgreSQL 17, `pgbench` (scale 50), Order-Management schema (20k customers / 500k orders)
4. **Controlled Scenarios (`S01`–`S08`):** Summary of the 8 isolated performance faults and ground-truth signals
5. **Benchmarking & Overhead Methodology:** 3-run repeatability, TPS, avg/p95 latency, buffer hits/reads, logging overhead
6. **Tool Profiles & Setup/Licensing Comparison:** pgBadger, pgMustard, dbForge Studio, postgresqltuner
7. **Ground-Truth Detection Matrix Results (`0–16`):** Side-by-side strengths & blind spots across `S01`–`S08`
8. **Empirical Before vs. After Optimization Results:** Measured TPS, latency, and temp-file improvements
9. **Monitoring Overhead Findings:** Impact of full query logging vs. slow-query logging vs. minimal instrumentation
10. **Recommendations & When to Use Which Tool:** Practical decision guide + Q&A
