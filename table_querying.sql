--Milestone 4 Task 1: How many stores does the business have and in what countries?
SELECT country_code, COUNT(country_code) FROM dim_store_details
GROUP BY country_code;

--Milestone 4 Task 2:  Which locations currently have the most scores?
SELECT locality, COUNT(locality) FROM dim_store_details
GROUP BY locality
ORDER BY COUNT(locality) DESC
LIMIT 7;

--Milestone 4 Task 3: Which months produced the largest amount of sales?
SELECT month, 
SUM(product_quantity * product_price) AS total_sales
FROM orders_table
JOIN dim_products on dim_products.product_code = orders_table.product_code
JOIN dim_date_times ON dim_date_times.date_uuid = orders_table.date_uuid
GROUP BY month
ORDER BY total_sales DESC
LIMIT 6;

--Milestone 4 Task 4: How many sales are coming from online?
SELECT 
	COUNT(still_available = 'F'),
	SUM(product_quantity) AS "product_quantity_online",
	CASE 
		WHEN store_type = 'Web Portal' THEN 'Web'
		ELSE 'offline'
	END AS "location"
FROM orders_table
JOIN dim_products on dim_products.product_code = orders_table.product_code
JOIN dim_store_details ON dim_store_details.store_code = orders_table.store_code
GROUP BY "location";

--Milestone 4 Task 5: What percentage of sales come from each type of store?
SELECT store_type,
ROUND(SUM(product_quantity * product_price)::numeric, 2) AS "total_sales",
ROUND((COUNT(*) / (SUM(COUNT(*)) OVER() )) * 100, 2) AS "percentage (%)"
FROM orders_table
JOIN dim_products on dim_products.product_code = orders_table.product_code
JOIN dim_store_details ON dim_store_details.store_code = orders_table.store_code
GROUP BY store_type
ORDER BY "total_sales" DESC;

--Milestone 4 Task 6: Which month in each year produced the highest cost of sales?
SELECT year,
month,
ROUND(SUM(product_quantity * product_price)::numeric, 2) AS "total_sales"
FROM orders_table
JOIN dim_products on dim_products.product_code = orders_table.product_code
JOIN dim_date_times ON dim_date_times.date_uuid = orders_table.date_uuid
GROUP BY dim_date_times.year, dim_date_times.month
ORDER BY "total_sales" DESC
LIMIT 10;

--Milestone 4 Task 7: What is the staff headcount?
SELECT SUM(staff_numbers) AS total_staff_numbers,
country_code
FROM dim_store_details
GROUP BY country_code
ORDER BY total_staff_numbers DESC;

--Milestone 4 Task 8: Which German store type is selling the most?
SELECT ROUND(SUM(product_price * product_quantity)::numeric, 2) AS total_sales,
store_type,
country_code
FROM orders_table
JOIN dim_products on dim_products.product_code = orders_table.product_code
JOIN dim_store_details ON dim_store_details.store_code = orders_table.store_code
WHERE country_code = 'DE'
GROUP BY dim_store_details.store_type, dim_store_details.country_code
ORDER BY total_sales ASC;

--Milestone 4 Task 9: How quickly is the company making sales?

with times as
(

   SELECT year,
	"timestamp",
	Day,
	month,
	TO_TIMESTAMP(CONCAT(year, '/', month, '/', day, '/', timestamp), 'YYYY/MM/DD/HH24:MI:ss') as my_times
	from orders_table
	JOIN dim_date_times on dim_date_times.date_uuid = orders_table.date_uuid
),  lead_times as (
	SELECT year,
	"timestamp",
	my_times,
	LEAD(my_times) OVER(ORDER BY my_times DESC) AS leading_times
	FROM times
), avg_times as (
	SELECT year,
	(AVG(my_times - leading_times)) AS time_diff
	FROM lead_times
	GROUP BY year
	ORDER BY time_diff DESC)
  
  SELECT year,

	FORMAT('Hours: %s Minutes: %s Seconds %s Milliseconds: %s', cast(round(avg(EXTRACT(HOUR FROM avg_times.time_diff))) as text),
		    cast(round(avg(EXTRACT(MINUTE FROM avg_times.time_diff))) as text),
		   cast(round(avg(EXTRACT(SECOND FROM avg_times.time_diff))) as text), 
			cast(round(avg(EXTRACT(MICROSECOND FROM avg_times.time_diff)), 2) as text)) AS actual_time_taken

FROM avg_times
GROUP BY year, avg_times
ORDER BY avg_times DESC
LIMIT 5;
