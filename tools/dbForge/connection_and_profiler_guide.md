# dbForge Studio for PostgreSQL: Connection & Query Profiler Guide

## Connection Configuration
- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `tuning_lab`
- **User:** `projectuser`
- **Password:** Read from your local `.env` file (`POSTGRES_PASSWORD`).

## Steps to Profile Benchmark & Scenario Queries
1. Confirm the Docker container is healthy (`docker compose ps`).
2. Open dbForge Studio for PostgreSQL (record exact version and edition—Express vs. Trial/Enterprise).
3. Create a New Connection to `tuning_lab` and click **Test Connection**.
4. Open `workload/custom_queries/01_benchmark_queries.sql` or the active scenario `probe.sql`.
5. Enable **Query Profiler** mode before executing each query (if supported in your edition), and save screenshots + exported plan XML/reports to `reports/screenshots/` and `reports/tool_reports/`.
6. Inspect Database Explorer -> `orders` -> Indexes to document visibility of duplicate (`S02`) and unused (`S03`) indexes.
