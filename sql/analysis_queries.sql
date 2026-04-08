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
