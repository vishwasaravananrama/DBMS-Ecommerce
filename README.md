# Mini E-Commerce Inventory & Order Management System
DBMS project · Flask + MySQL + Bootstrap

## Setup (Windows, PowerShell) — run inside this folder
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env        # then open .env and put your MySQL password
```
If PowerShell blocks activation: `Set-ExecutionPolicy -Scope Process Bypass`

## Create the database (new DB `mini_ecommerce_db`, does not touch `ecommerce_db`)
Open **MySQL Workbench**, connect, then open and run (lightning icon) in this order:
1. `database/schema.sql`
2. `database/sample_data.sql`

(Or from PowerShell: `mysql -u root -p < database/schema.sql` and the same for sample_data.sql.)

## Run
```powershell
python app.py
```
Open http://127.0.0.1:5000

## Demo script for faculty (5–7 minutes)
1. Show ER diagram (`docs/er_diagram.md`) and tables in MySQL Workbench.
2. Dashboard: cards, chart, low-stock list.
3. Products: search, filter by category, add, edit, delete. Try a duplicate SKU or negative price -> validation error.
4. Try deleting a product that has orders -> blocked by foreign key (referential integrity).
5. Create an order -> stock decreases; open order details.
6. Try ordering more than the stock -> rejected, nothing saved (transaction rollback).
7. Run queries from `database/dbms_queries.sql` in Workbench (joins, GROUP BY, subquery, transaction).

## Common errors
| Error | Fix |
|---|---|
| `Access denied for user 'root'` | Wrong password in `.env` |
| `Unknown database 'mini_ecommerce_db'` | Run `schema.sql` first |
| `Can't connect to MySQL server` | Start the MySQL service (Services app) |
| `cryptography package is required` | `pip install cryptography` |
| CHECK constraints seem ignored | Need MySQL 8.0.16 or newer |
