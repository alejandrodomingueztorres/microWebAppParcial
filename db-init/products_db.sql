CREATE DATABASE IF NOT EXISTS products_db;
USE products_db;

CREATE TABLE IF NOT EXISTS products (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    quantity INT NOT NULL DEFAULT 0
);

INSERT INTO products (name, price, quantity) VALUES
    ('Teclado mecanico', 150000.00, 25),
    ('Mouse inalambrico', 60000.00, 40),
    ('Monitor 24 pulgadas', 550000.00, 15),
    ('Audifonos USB', 90000.00, 30),
    ('Webcam HD', 120000.00, 20);
