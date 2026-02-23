CREATE DATABASE IF NOT EXISTS company_db;
USE company_db;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    department VARCHAR(50),
    salary INT,
    city VARCHAR(50)
);

INSERT INTO employees (name, department, salary, city) VALUES
('Alice Smith', 'HR', 60000, 'New York'),
('Bob Johnson', 'Engineering', 80000, 'San Francisco'),
('Charlie Brown', 'Sales', 55000, 'Chicago'),
('David Lee', 'Marketing', 65000, 'Los Angeles'),
('Eve Wilson', 'Engineering', 85000, 'Seattle'),
('Frank Miller', 'Sales', 52000, 'Boston'),
('Grace Davis', 'HR', 62000, 'Austin'),
('Hank Moore', 'Engineering', 78000, 'Denver'),
('Ivy Taylor', 'Marketing', 67000, 'Miami'),
('Jack White', 'Sales', 54000, 'Phoenix'),
('Liam Scott', 'Engineering', 90000, 'San Jose'),
('Mia Green', 'HR', 61000, 'Atlanta');
