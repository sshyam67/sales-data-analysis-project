SELECT region, SUM(sales) AS total_sales
FROM sales
GROUP BY region;

SELECT category, SUM(sales) AS total_sales
FROM sales
GROUP BY category;

SELECT sub_category, SUM(profit) AS total_profit
FROM sales
GROUP BY sub_category;

SELECT order_year, SUM(sales) AS yearly_sales
FROM sales
GROUP BY order_year;

-- Top 5 products by profit
SELECT product_name, SUM(profit) AS total_profit
FROM sales
GROUP BY product_name
ORDER BY total_profit DESC
LIMIT 5;

-- Loss making products
SELECT product_name, SUM(profit) AS total_profit
FROM sales
GROUP BY product_name
ORDER BY total_profit ASC
LIMIT 5;
