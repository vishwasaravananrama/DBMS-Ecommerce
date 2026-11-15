# Data Dictionary

## categories
| Column | Type | Constraints | Description |
|---|---|---|---|
| category_id | INT | PK, AUTO_INCREMENT | Category identifier |
| category_name | VARCHAR(80) | NOT NULL, UNIQUE | Category name |
| description | VARCHAR(255) | – | Optional notes |

## products
| Column | Type | Constraints | Description |
|---|---|---|---|
| product_id | INT | PK, AUTO_INCREMENT | Product identifier |
| product_name | VARCHAR(120) | NOT NULL | Name |
| sku | VARCHAR(40) | NOT NULL, UNIQUE | Stock keeping unit |
| category_id | INT | NOT NULL, FK → categories | Category |
| description | VARCHAR(255) | – | Details |
| price | DECIMAL(10,2) | NOT NULL, CHECK ≥ 0 | Current selling price |
| stock_quantity | INT | NOT NULL, DEFAULT 0, CHECK ≥ 0 | Units in stock |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Created date |

## customers
| Column | Type | Constraints | Description |
|---|---|---|---|
| customer_id | INT | PK, AUTO_INCREMENT | Customer identifier |
| customer_name | VARCHAR(100) | NOT NULL | Name |
| email | VARCHAR(120) | NOT NULL, UNIQUE | Email |
| phone | VARCHAR(20) | – | Phone |
| address | VARCHAR(255) | – | Address |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Registered date |

## orders
| Column | Type | Constraints | Description |
|---|---|---|---|
| order_id | INT | PK, AUTO_INCREMENT | Order identifier |
| customer_id | INT | NOT NULL, FK → customers (RESTRICT) | Who ordered |
| order_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When |
| total_amount | DECIMAL(12,2) | NOT NULL, CHECK ≥ 0 | Order total |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'Placed' | Order status |

## order_items
| Column | Type | Constraints | Description |
|---|---|---|---|
| order_item_id | INT | PK, AUTO_INCREMENT | Line identifier |
| order_id | INT | NOT NULL, FK → orders (CASCADE) | Parent order |
| product_id | INT | NOT NULL, FK → products (RESTRICT) | Product |
| quantity | INT | NOT NULL, CHECK > 0 | Quantity |
| unit_price | DECIMAL(10,2) | NOT NULL, CHECK ≥ 0 | Price at purchase time |
| subtotal | DECIMAL(12,2) | NOT NULL | quantity × unit_price |

## Normalization note
The schema is in **3NF**: every non-key attribute depends only on its table's primary key. Category data lives in its own table (no repeated category names), and order lines are separated from orders to avoid repeating groups. `unit_price` is deliberately stored in `order_items` so historical orders do not change when a product's price changes.
