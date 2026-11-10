-- Monthly revenue
SELECT month, ROUND(SUM(price), 2) AS revenue, COUNT(*) AS sales
FROM sales GROUP BY month ORDER BY month;

-- Revenue and average ticket by service
SELECT service, ROUND(SUM(price), 2) AS revenue, ROUND(AVG(price), 2) AS avg_ticket, COUNT(*) AS sales
FROM sales GROUP BY service ORDER BY revenue DESC;

-- Acquisition channel performance
SELECT channel, COUNT(*) AS sales, ROUND(SUM(price), 2) AS revenue, ROUND(AVG(price), 2) AS avg_ticket
FROM sales GROUP BY channel ORDER BY revenue DESC;

-- Repeat-client rate
SELECT ROUND(100.0 * SUM(CASE WHEN visits > 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS repeat_client_pct
FROM clients;

-- Top 10 clients by lifetime value
SELECT client_id, visits, ROUND(lifetime_value, 2) AS lifetime_value
FROM clients ORDER BY lifetime_value DESC LIMIT 10;
