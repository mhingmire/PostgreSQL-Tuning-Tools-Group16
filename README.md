# PostgreSQL Tuning Tools – Group 16

**Course:** COMPSCI 4411/9538  
**Group Members:** Mrida Hingmire, Atika Hussain, Jasnav Bajaj

A reproducible experimental framework for comparing four PostgreSQL performance tuning tools under identical PostgreSQL 17 hardware, dataset, and workload conditions:

1. **pgBadger** (Log analyzer)
2. **pgMustard** (Web-based `EXPLAIN ANALYZE` plan analyzer)
3. **dbForge Studio for PostgreSQL** (Desktop IDE & query profiler)
4. **postgresqltuner** (SQL/catalog diagnostic & configuration auditor)

---

## 1. Project Overview

We evaluate each tool across four core criteria (**Bottleneck Identification**, **Index Analysis**, **Tuning Recommendations**, and **Reporting**) as well as installation/setup effort, ease of use, cost/licensing, compatibility, monitoring overhead, recommendation accuracy, and limitations. All experiments run against PostgreSQL 17 (`postgres:17`) seeded with:
- **pgbench** at scale factor `50` (~5,000,000 `pgbench_accounts` rows)
- **Order-management dataset** (`customers`: 20,000 rows; `orders`: 500,000 rows)
- **Eight controlled scenarios** (`S01`–`S08`) tested before and after optimizations with >=3 benchmark repetitions per condition.

---

## 2. Prerequisites

- **Docker Desktop** (with Docker Compose v2+)
- **Python 3.10+** with `python-dotenv` (optional `matplotlib` for `reports/figures/generate_figures.py`)
- **Git**
- **DBeaver Community Edition** (recommended for visual database inspection)
- Optional tool-specific prerequisites: Perl / WSL (for `pgBadger` and `postgresqltuner`), modern browser (for `pgMustard`), Windows installer (for `dbForge Studio`).

---

## 3. Installation & Starting Docker

1. Clone the repository and enter the project directory:
   ```powershell
   git clone https://github.com/mhingmire/PostgreSQL-Tuning-Tools-Group16.git
   cd PostgreSQL-Tuning-Tools-Group16
   ```
2. Create your local environment configuration from the template (never commit `.env`):
   ```powershell
   Copy-Item .env.example .env
   ```
   Edit `.env` and set a strong `POSTGRES_PASSWORD`.
3. Start PostgreSQL 17 and verify the health check passes:
   ```powershell
   docker compose up -d
   docker compose ps
   ```

---

## 4. Initializing the Database & Loading Sample Data

On first startup, Docker automatically runs:
- `database/initialization/01_extensions.sql` (`pg_stat_statements`, `pgstattuple`, `pg_buffercache`)
- `database/schema/01_order_management_schema.sql` (`customers` and `orders` tables + baseline FK index)

Next, populate the deterministic order-management dataset (20,000 customers, 500,000 orders) and initialize `pgbench` at scale factor 50:

```powershell
# Load 20,000 customers + 500,000 orders
Get-Content database\seed\01_generate_order_data.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab

# Initialize pgbench scale factor 50
python database\seed\02_init_pgbench.py

# Verify extensions, settings, and row counts
Get-Content database\initialization\02_verify_setup.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
```

---

## 5. Connecting Through DBeaver

Use these exact settings in DBeaver (**Database -> New Database Connection -> PostgreSQL**):

- **Host:** `localhost`
- **Port:** `5432`
- **Database:** `tuning_lab`
- **Username:** `projectuser`
- **Password:** Read from your local `.env` file (`POSTGRES_PASSWORD`)

Click **Test Connection** (download the PostgreSQL JDBC driver if DBeaver prompts you). See [dbeaver_connection_guide.md](documentation/setup_guides/dbeaver_connection_guide.md) for screenshot-ready validation queries.

---

## 6. Running Workloads, Scenarios & Collecting Statistics

### Baseline Benchmark (3 repetitions)
```powershell
python experiments\baseline\run_baseline.py
```

### Custom Benchmark Run (TPS, avg latency, p95 latency, buffer hits/reads)
```powershell
python workload\benchmark_scripts\run_benchmark.py --label baseline_clean --workload custom_orders --runs 3 --duration 30
```

### Collecting Database Statistics
```powershell
Get-Content database\statistics\collect_stats.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
```

### Accessing PostgreSQL Logs (for pgBadger)
PostgreSQL writes `pgBadger`-formatted logs (`log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '`) inside the persistent `pgdata` volume (`/var/lib/postgresql/data/pgdata/log`). Copy them locally with:
```powershell
python tools\pgBadger\collect_logs.py
```

---

## 7. Running Controlled Scenarios & Before/After Experiments

Run one scenario at a time from `database/scenarios/` (`S01`–`S08`):
```powershell
# Example: Scenario S01 (Missing Index)
Get-Content database\scenarios\s01_missing_index\setup.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
Get-Content database\scenarios\s01_missing_index\probe.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
python workload\benchmark_scripts\run_benchmark.py --label before_opt --workload custom_orders --runs 3 --duration 30

# Apply optimization & re-measure
Get-Content experiments\optimization\01_apply_optimizations.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
python workload\benchmark_scripts\run_benchmark.py --label after_opt --workload custom_orders --runs 3 --duration 30

# Compare before vs after
python results\comparison\compare_before_after.py --before results\processed\<before>.json --after results\processed\<after>.json

# Restore clean baseline before the next scenario
Get-Content experiments\optimization\02_revert_optimizations.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
Get-Content database\scenarios\s01_missing_index\restore.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
```

### Measuring Monitoring Overhead
```powershell
python experiments\overhead\measure_overhead.py --runs 3 --duration 20
```

---

## 8. Reproducing Results on a Clean Machine

Follow the step-by-step checklist in [clean_machine_reproducibility.md](documentation/reproducibility/clean_machine_reproducibility.md).

---

## 9. Stopping and Restarting the Environment

```powershell
# Stop container while preserving the pgdata volume (including logs)
docker compose stop

# Restart later
docker compose start

# Tear down container & volumes completely (WARNING: deletes all DB data)
docker compose down -v
```
