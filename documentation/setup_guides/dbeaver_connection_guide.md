# DBeaver Connection Guide

Follow these steps to open and inspect `tuning_lab` in DBeaver:

1. Verify the PostgreSQL 17 Docker container is running and healthy:
   ```powershell
   docker compose ps
   ```
   Ensure `tuning_lab_pg17` shows status `Up (healthy)`.

2. Open **DBeaver** and select **Database -> New Database Connection** (or click the plug icon).
3. Choose **PostgreSQL** and click **Next**.
4. Enter the exact connection settings:
   - **Connect by:** Host
   - **Host:** `localhost`
   - **Port:** `5432`
   - **Database:** `tuning_lab`
   - **Username:** `projectuser`
   - **Password:** Read `POSTGRES_PASSWORD` from your local `.env` file.
5. Check **Save password locally** (optional for convenience on your personal workstation).
6. Click **Test Connection...** (if prompted to download the PostgreSQL JDBC driver, click **Download**).
7. Once `Connected` appears, click **Finish**.

## Quick Verification Queries Inside DBeaver SQL Editor
```sql
SELECT version();
SELECT COUNT(*) AS customers_count FROM customers;
SELECT COUNT(*) AS orders_count FROM orders;
SELECT * FROM pg_extension WHERE extname IN ('pg_stat_statements', 'pgstattuple', 'pg_buffercache');
```
