-- SQLite
INSERT INTO classmates (name, age) 
VALUES ('홍길동',23);

INSERT INTO classmates VALUES(11,'홍길동',37,'서울');

SELECT rowid, * FROM classmates;

DROP TABLE classmates;

CREATE TABLE classmates (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  age INT NOT NULL,
  address TEXT NOT NULL
);

INSERT INTO classmates
(name, age, address)
VALUES
('홍길동', 7, '서울'),
('홍길동', 71, '서울'),
('홍길동', 27, '서울'),
('홍길동', 37, '서울'),
('홍길동', 47, '서울'),
('홍길동', 67, '서울');

SELECT rowid,name FROM
classmates;

SELECT rowid,name FROM
classmates LIMIT 3;

SELECT rowid,name,address FROM
classmates LIMIT 3 OFFSET 10;

SELECT rowid,name,age FROM
classmates WHERE age>30;

SELECT DISTINCT name,age FROM classmates;