create database db;

CREATE TABLE room_availability (
    room_no        INT          PRIMARY KEY,
    room_type      VARCHAR(30)  NOT NULL,
    room_available TINYINT(1)   NOT NULL DEFAULT 1,
    start_date     DATE         NULL,
    end_date       DATE         NULL
);
show tables;
select * from room_availability;
INSERT INTO room_availability (room_no, room_type)
VALUES
  (101, 'Single'),
  (102, 'Single'),
  (103, 'Double'),
  (104, 'Double'),
  (105, 'Suite'),
  (106, 'Suite'),
  (107, 'Single'),
  (108, 'Double'),
  (109, 'Suite'),
  (110, 'Single');

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

select* from users;
select* from support_tickets;
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    issue_description TEXT NOT NULL,
    status ENUM('open', 'closed', 'pending') DEFAULT 'open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
ALTER TABLE support_tickets
ADD COLUMN email VARCHAR(255);

-- Product Table
CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    stock INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
select * from products;
-- Order Table
CREATE TABLE IF NOT EXISTS orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    order_status ENUM('pending', 'shipped', 'delivered') DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
ALTER TABLE orders
ADD COLUMN name VARCHAR(255);

UPDATE orders 
SET order_status = 'delivered'
WHERE delivery_date <= NOW() AND order_status = 'pending';

select * from orders;
select * from products;

-- Insert test order with delivery date
INSERT INTO orders (user_id, order_status, delivery_date) 
VALUES (1, 'shipped', '2025-05-01');
INSERT INTO orders (user_id, order_status, delivery_date) 
VALUES (2,'pending','2025-05-10');

select * from orders where order_id=5;
-- OrderItem Table
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)

);
ALTER TABLE order_items ADD COLUMN name VARCHAR(255);

select * from order_items;
-- ProductInquiry Table
CREATE TABLE IF NOT EXISTS product_inquiries (
    inquiry_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    product_id INT,
    inquiry_text TEXT NOT NULL,
    response_text TEXT,
    inquiry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

select * from support_tickets;
CREATE TABLE IF NOT EXISTS table_reservation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    date DATE NOT NULL,
    time TIME NOT NULL,
    guests INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
select * from table_reservation;
DELIMITER //

CREATE TRIGGER update_order_status_after_delivery
AFTER UPDATE ON orders
FOR EACH ROW
BEGIN
    IF NEW.delivery_date <= NOW() AND NEW.order_status = 'pending' THEN
        UPDATE orders
        SET order_status = 'delivered'
        WHERE order_id = NEW.order_id;
    END IF;
END //

DELIMITER ;
SELECT * FROM orders WHERE order_status = 'pending' AND delivery_date <= NOW();






