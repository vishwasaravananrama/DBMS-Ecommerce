USE mini_ecommerce_db;

-- 1. All products with category names (INNER JOIN)
SELECT p.product_id, p.product_name, p.sku, c.category_name, p.price, p.stock_quantity
FROM products p JOIN categories c ON p.category_id = c.category_id;

-- 2. Customer order history (JOIN)
SELECT c.customer_name, o.order_id, o.order_date, o.total_amount, o.status
FROM customers c JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_name, o.order_date DESC;

-- 3. Order details with customer information (4-table JOIN)
SELECT o.order_id, c.customer_name, c.email, p.product_name, i.quantity, i.unit_price, i.subtotal
FROM orders o
JOIN customers c   ON o.customer_id = c.customer_id
JOIN order_items i ON o.order_id = i.order_id
JOIN products p    ON i.product_id = p.product_id
ORDER BY o.order_id;

-- 4. Total sales (aggregate functions)
SELECT SUM(total_amount) AS total_sales, COUNT(*) AS total_orders, AVG(total_amount) AS avg_order_value
FROM orders;

-- 5. Most ordered products (GROUP BY + ORDER BY)
SELECT p.product_name, SUM(i.quantity) AS units_sold, SUM(i.subtotal) AS revenue
FROM order_items i JOIN products p ON i.product_id = p.product_id
GROUP BY p.product_id, p.product_name
ORDER BY units_sold DESC;

-- 6. Low stock products (stock < 10)
SELECT product_name, sku, stock_quantity FROM products
WHERE stock_quantity < 10 ORDER BY stock_quantity;

-- 7. Number of products in each category (LEFT JOIN keeps empty categories)
SELECT c.category_name, COUNT(p.product_id) AS product_count
FROM categories c LEFT JOIN products p ON c.category_id = p.category_id
GROUP BY c.category_id, c.category_name;

-- 8. Total inventory value
SELECT SUM(price * stock_quantity) AS inventory_value FROM products;

-- 9. Customers who never ordered (subquery)
SELECT customer_name FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);

-- 10. Transaction demo (what the app does when placing an order)
START TRANSACTION;
INSERT INTO orders (customer_id, total_amount) VALUES (3, 499.00);
INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
VALUES (LAST_INSERT_ID(), 1, 1, 499.00, 499.00);
UPDATE products SET stock_quantity = stock_quantity - 1 WHERE product_id = 1;
-- Run COMMIT; to save the order, or ROLLBACK; to undo everything (atomicity demo)
ROLLBACK;
