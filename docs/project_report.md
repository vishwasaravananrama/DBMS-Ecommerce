# Project Report — Mini E-Commerce Inventory & Order Management System

**Student:** Vishwa Saravanan Rama (RA2411047050019) · **Dept:** Artificial Intelligence · **Guide:** S.P. Ramya · SRMIST

## 1. Introduction
A database-driven web application that manages products, categories, customers and orders for a small online shop, keeping stock accurate when orders are placed.

## 2. Problem Statement
Manual/spreadsheet records cause outdated stock, duplicate data and difficulty tracking orders. A centralized relational database solves this.

## 3. Objectives
- Store data in a normalized MySQL database with keys and constraints
- Provide CRUD for products, categories and customers
- Place orders with automatic stock validation and update
- Show a dashboard and order history

## 4. Technologies
Python Flask (backend) · HTML, CSS, JavaScript, Bootstrap, Chart.js (frontend) · MySQL (database) · PyMySQL (connector) · VS Code, MySQL Workbench, Git

## 5. System Design
Browser → Flask routes → MySQL.
Tables: categories, products, customers, orders, order_items (see `er_diagram.md` and `data_dictionary.md`).

## 6. DBMS Concepts Demonstrated
Primary & foreign keys · UNIQUE / NOT NULL / CHECK / DEFAULT constraints · referential integrity (RESTRICT, CASCADE) · 1–M and M–N (via junction table) relationships · INNER/LEFT joins · GROUP BY & aggregates · subqueries · indexes · transactions (COMMIT/ROLLBACK, `SELECT … FOR UPDATE`) · 3NF normalization

## 7. Modules
Dashboard · Product management · Category management · Customer management · Order management

## 8. Business Rules
1. Stock is validated before an order is saved.
2. Orders exceeding stock are rejected.
3. Stock decreases when an order succeeds.
4. Order total = sum of price × quantity.
5. Order creation + stock update happen in one transaction; failure rolls back everything.
6. Prices at purchase time are preserved in `order_items`.
7. Products used in orders cannot be deleted.

## 9. Testing
| Test | Expected | Result |
|---|---|---|
| Add product with duplicate SKU | Error shown | _fill after running_ |
| Add product with negative price | Error shown | |
| Order with quantity > stock | Rejected, stock unchanged | |
| Valid order | Saved, stock reduced | |
| Delete product used in an order | Blocked | |

## 10. Screenshots
_Insert: ER diagram, dashboard, products, create order, order details, Workbench query results._

## 11. Conclusion & Future Scope
A working, consistent order/inventory system. Future work: suppliers, warehouses, cart, payments, shipments, returns, authentication, reports (the full planned system).
