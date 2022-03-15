SELECT last_name, COUNT(*) FROM users GROUP BY last_name;

SELECT last_name, COUNT(*) AS name_count FROM users GROUP BY last_name;