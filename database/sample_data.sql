USE mini_ecommerce_db;

INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Gadgets and accessories'),
('Books', 'Academic and general books'),
('Clothing', 'Apparel'),
('Home & Kitchen', 'Household items');

-- Stock values below already reflect the sample orders further down
INSERT INTO products (product_name, sku, category_id, description, price, stock_quantity) VALUES
('Wireless Mouse',      'ELE-001', 1, '2.4GHz optical mouse',        499.00, 40),
('Bluetooth Headphones','ELE-002', 1, 'Over-ear headphones',        1999.00, 8),
('USB-C Charger 30W',   'ELE-003', 1, 'Fast charger',                899.00, 25),
('DBMS Concepts Book',  'BOK-001', 2, 'Database textbook',           650.00, 30),
('Python Crash Course', 'BOK-002', 2, 'Beginner Python book',        550.00, 4),
('Cotton T-Shirt',      'CLO-001', 3, 'Unisex round neck',           399.00, 60),
('Denim Jeans',         'CLO-002', 3, 'Slim fit',                   1299.00, 15),
('Steel Water Bottle',  'HOM-001', 4, '1 litre insulated',           449.00, 35),
('Non-stick Pan',       'HOM-002', 4, '24 cm pan',                   799.00, 6);

INSERT INTO customers (customer_name, email, phone, address) VALUES
('Arun Kumar',  'arun@example.com',   '9876543210', 'Trichy, Tamil Nadu'),
('Divya Raj',   'divya@example.com',  '9876500011', 'Chennai, Tamil Nadu'),
('Karthik S',   'karthik@example.com','9876500022', 'Coimbatore, Tamil Nadu');

INSERT INTO orders (customer_id, total_amount, status) VALUES
(1, 0, 'Placed'),
(2, 0, 'Placed'),
(1, 0, 'Placed');

INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal) VALUES
(1, 1, 1,  499.00,  499.00),
(1, 4, 1,  650.00,  650.00),
(2, 2, 1, 1999.00, 1999.00),
(2, 6, 1,  399.00,  399.00),
(2, 8, 1,  449.00,  449.00),
(3, 5, 2,  550.00, 1100.00);

-- make order totals match their items
UPDATE orders o
SET total_amount = (SELECT SUM(subtotal) FROM order_items i WHERE i.order_id = o.order_id);
