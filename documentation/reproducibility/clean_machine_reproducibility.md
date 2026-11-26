# Clean-Machine Reproducibility Guide

Use this checklist to reproduce the entire PostgreSQL 17 lab and benchmark suite from scratch on a clean Windows, macOS, or Linux workstation.

## 1. Prerequisites
- Docker Desktop running (`docker info` succeeds)
- Python 3.10+ (`pip install python-dotenv matplotlib`)
- Git

## 2. Clone & Configure
```powershell
git clone https://github.com/mhingmire/PostgreSQL-Tuning-Tools-Group16.git
cd PostgreSQL-Tuning-Tools-Group16
Copy-Item .env.example .env
# Edit .env to set POSTGRES_PASSWORD
```

## 3. Start & Verify PostgreSQL 17
```powershell
docker compose up -d
docker compose ps
```
Wait until `tuning_lab_pg17` reports `healthy`.

## 4. Seed Datasets (Order Management + pgbench Scale 50)
```powershell
Get-Content database\seed\01_generate_order_data.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
python database\seed\02_init_pgbench.py
Get-Content database\initialization\02_verify_setup.sql -Raw | docker exec -i tuning_lab_pg17 psql -U projectuser -d tuning_lab
```
Expected verification outputs:
- PostgreSQL `17.x`
- Extensions active: `pg_stat_statements`, `pgstattuple`, `pg_buffercache`
- `customers`: `20,000` rows; `orders`: `500,000` rows; `pgbench_accounts`: `5,000,000` rows

## 5. Run Baseline Benchmark (>=3 runs)
```powershell
python workload\benchmark_scripts\run_benchmark.py --label clean_repro_baseline --workload custom_orders --runs 3 --duration 30
```
Check `results/processed/` for the generated JSON/CSV summary and `results/raw/` for per-run logs.
