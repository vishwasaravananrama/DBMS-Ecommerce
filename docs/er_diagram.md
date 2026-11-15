# ER Diagram

Paste the block below into https://mermaid.live to export a PNG for your report/PPT.

```mermaid
erDiagram
    CATEGORIES ||--o{ PRODUCTS : "has"
    CUSTOMERS  ||--o{ ORDERS : "places"
    ORDERS     ||--|{ ORDER_ITEMS : "contains"
    PRODUCTS   ||--o{ ORDER_ITEMS : "appears in"

    CATEGORIES {
        int category_id PK
        varchar category_name UK
        varchar description
    }
    PRODUCTS {
        int product_id PK
        varchar product_name
        varchar sku UK
        int category_id FK
        varchar description
        decimal price
        int stock_quantity
        timestamp created_at
    }
    CUSTOMERS {
        int customer_id PK
        varchar customer_name
        varchar email UK
        varchar phone
        varchar address
        timestamp created_at
    }
    ORDERS {
        int order_id PK
        int customer_id FK
        timestamp order_date
        decimal total_amount
        varchar status
    }
    ORDER_ITEMS {
        int order_item_id PK
        int order_id FK
        int product_id FK
        int quantity
        decimal unit_price
        decimal subtotal
    }
```

**Relationships:** Category 1—M Product · Customer 1—M Order · Order 1—M OrderItem · Product 1—M OrderItem
(Order and Product have a many-to-many relationship, resolved by the `order_items` table.)
