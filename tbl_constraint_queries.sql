--Alter orders_table
ALTER TABLE IF EXISTS orders_table
ALTER COLUMN date_uuid TYPE uuid USING date_uuid::uuid,
ALTER COLUMN user_uuid TYPE uuid USING user_uuid::uuid,
ALTER COLUMN card_number TYPE VARCHAR(19),
ALTER COLUMN store_code TYPE VARCHAR(12),
ALTER COLUMN product_code  TYPE VARCHAR(11),
ALTER COLUMN product_quantity TYPE SMALLINT;

--Alter dim_users
ALTER TABLE IF EXISTS dim_users
ALTER COLUMN first_name TYPE VARCHAR(255),
ALTER COLUMN last_name TYPE VARCHAR(255),
ALTER COLUMN date_of_birth TYPE DATE,
ALTER COLUMN country_code TYPE VARCHAR(2),
ALTER COLUMN user_uuid TYPE uuid USING user_uuid::uuid,
ALTER COLUMN join_date TYPE DATE;

--Alter dim_store_details
ALTER TABLE IF EXISTS dim_store_details
ALTER COLUMN longitude TYPE FLOAT USING longitude::double precision,
ALTER COLUMN locality TYPE VARCHAR(255),
ALTER COLUMN store_code TYPE VARCHAR(12),
ALTER COLUMN staff_numbers TYPE SMALLINT USING staff_numbers::smallint,
ALTER COLUMN opening_date TYPE DATE USING opening_date::DATE,
ALTER COLUMN latitude TYPE FLOAT USING latitude::double precision,
ALTER COLUMN country_code TYPE VARCHAR(2),
ALTER COLUMN continent TYPE VARCHAR(255),
ALTER COLUMN store_type TYPE VARCHAR(255);


--Alter dim_products
UPDATE dim_products SET product_price = REPLACE(product_price, '£', '');

ALTER TABLE IF EXISTS dim_products
ADD COLUMN IF NOT EXISTS weight_class varchar(15);

UPDATE 
   dim_products
SET 
   removed = REPLACE(removed,'Still_avaliable', 't');
   
UPDATE 
   dim_products
SET 
   removed = REPLACE(removed,'Removed', 'f');

ALTER TABLE dim_products
  RENAME COLUMN removed TO still_available;

ALTER TABLE IF EXISTS dim_products
ALTER COLUMN product_price TYPE FLOAT USING product_price::double precision,
ALTER COLUMN weight_in_kg TYPE FLOAT USING weight_in_kg::double precision,
ALTER COLUMN "EAN" TYPE VARCHAR(20),
ALTER COLUMN product_code TYPE VARCHAR(11),
ALTER COLUMN date_added TYPE DATE USING date_added::DATE,
ALTER COLUMN "uuid" TYPE UUID USING "uuid"::UUID,
ALTER COLUMN still_available TYPE BOOL USING still_available::boolean,
ALTER COLUMN weight_class TYPE VARCHAR(15);

UPDATE dim_products
SET weight_class = 'Light' 
WHERE weight_in_kg < 2;

UPDATE dim_products
SET weight_class = 'Medium' 
WHERE weight_in_kg >= 2 AND weight_in_kg < 40;

UPDATE dim_products
SET weight_class = 'HEAVY' 
WHERE weight_in_kg >= 40 AND weight_in_kg < 140;

UPDATE dim_products
SET weight_class = 'Truck required' 
WHERE weight_in_kg > 140;


--Alter dim_date_times
ALTER TABLE IF EXISTS dim_date_times
ALTER COLUMN "month" TYPE VARCHAR(2),
ALTER COLUMN "year" TYPE VARCHAR(4),
ALTER COLUMN "day" TYPE VARCHAR(2),
ALTER COLUMN time_period TYPE VARCHAR(10),
ALTER COLUMN date_uuid TYPE "uuid" USING date_uuid::uuid;

--Alter dim_card_details
ALTER TABLE IF EXISTS dim_card_details
ALTER COLUMN card_number TYPE VARCHAR(19),
ALTER COLUMN expiry_date TYPE VARCHAR(7),
ALTER COLUMN date_payment_confirmed TYPE DATE USING date_payment_confirmed::DATE

--Add primary key to dim_card_details
ALTER TABLE dim_card_details
ADD PRIMARY KEY (card_number);

--Add primary key to dim_date_times
ALTER TABLE dim_date_times
ADD PRIMARY KEY (date_uuid);

--Add primary key to dim_products
ALTER TABLE dim_products
ADD PRIMARY KEY (product_code);

--Add primary key to dim_store_details
ALTER TABLE dim_store_details
ADD PRIMARY KEY (store_code);

--Add primary key to dim_users
ALTER TABLE dim_users
ADD PRIMARY KEY (user_uuid);


--Add foreign key to orders table to link it to dim_card_details
ALTER TABLE orders_table
      ADD CONSTRAINT fk_card_details FOREIGN KEY (card_number) 
          REFERENCES dim_card_details (card_number);

--Add foreign key to orders table to link it to dim_date_times
ALTER TABLE orders_table
      ADD CONSTRAINT fk_date_times FOREIGN KEY (date_uuid) 
          REFERENCES dim_date_times (date_uuid);
		  
--Add foreign key to orders table to link it to dim_store_details
ALTER TABLE orders_table
      ADD CONSTRAINT fk_store FOREIGN KEY (store_code) 
          REFERENCES dim_store_details (store_code);

--Add foreign key to orders table to link it to dim_users
ALTER TABLE orders_table
      ADD CONSTRAINT fk_users FOREIGN KEY (user_uuid) 
          REFERENCES dim_users (user_uuid);

--Add foreign key to orders table to link it to dim_products
ALTER TABLE orders_table
      ADD CONSTRAINT fk_product_orders FOREIGN KEY (product_code) 
          REFERENCES dim_products (product_code);


