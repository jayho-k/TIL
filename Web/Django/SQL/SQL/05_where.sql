CREATE TABLE users (
first_name TEXT NOT NULL,
last_name TEXT NOT NULL,
age INT NOT NULL,
country TEXT NOT NULL,
phone TEXT NOT NULL,
balance TEXT NOT NULL
);

SELECT * FROM users where age >= 30;

SELECT first_name FROM users where age >= 30;

SELECT age, first_name, last_name FROM users 
where age >= 30 AND last_name = '김';

