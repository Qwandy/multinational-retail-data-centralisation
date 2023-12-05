# Multinational-retail-data-centralisation

# Project description

The aim of this project is to use various Python cloud tools and data extractors (such as Boto3, SQLAlchemy, tabular-py, json) to make my own OOP-based Python package for extracting and cleaning data and having the option to upload to a cloud database. I have achieved this aims and made a Python package with tools that can perform these tasks.

## Features
- DatabaseConnector (Class):
    - `_read_db_creds`: Loads in a yaml file containing S3 credentials, returns yaml credentials.
    - `init_db_engine`: Calls the internal `_read_db_creds` method to obtain YAML file credentials and contains information on database type and database API to create an SQLAlchemy engine with these details, and returns engine.
    - `upload_to_db`: Takes in a dataframe (type) as an input and table name (string) as an input to upload a pandas dataframe to the cloud with the specified table name. Returns nothing.
- DataExtractor (Class):
   - `list_db_tables`: Takes a yaml credentials file to know what database to retrieve table names from. Returns a list of table names within the database.
   - `read_rds_table`: Takes in a instance of the DatabaseConnector class and table name (string) as inputs. Creates an engine by calling the `init_db_engine` method from DatabaseConnector and calls the Pandas `read_sql_table` method to transform an sql table into a Pandas dataframe. Returns Pandas dataframe.
   - `retrieve_pdf_data`: Takes in a URL link as input for where to obtain pdf data from. Uses tabular-py to read in the data then concatenates every page of data from the PDF to return a Pandas dataframe.
   - `list_number_of_stores`: Takes in an AWS endpoint for the AWS RDS to obtain data from as input and some certification (such as access key) to authenticate the API call. Returns the number of stores.
   - `retrieve_stores_data`: Takes in no inputs. Uses a loop to iterate through the number of stores, appending json data to an empty dictionary until data from all stores has been put into the dictionary. Creates a Dataframe to return as output from the created dictionary.
   - `extract_from_s3`: Takes in an URL as input and type of file (so that I didn't delete code to repurpose the function). The valid inputs for 'file' are 'products' to read in a products csv and 'date_times' to read in a date times  JSON file. Returns a dataframe with the data.
- DataCleaning (Class):
   - `clean_user_data`: Takes in no inputs. Calls the DataExtractor `read_rds_table` method to create a dataframe of user data. Drops any NaN-containing rows, converts phone numbers to consistent format and dates to pandas datetime objects. Also makes sure that emails have some validity by containing an '@'. Returns a cleaned user table.
   - `clean_card_data`: Takes in a link as input. Calls the DataExtractor class' `retrieve_pdf_data` method to obtain a dataframe of card data. Drops unneccessary columns, filters out rows with 'None', filters rows where card number lengths are valid and then returns the cleaned card data as a Pandas dataframe.
   - `clean_store_data`: Takes in a dataframe as input. Drops lat column as it is full of NaNs and redundant (latitude column contains the data). Cleans the address column data, converts dates to Pandas datetimes, drops NaNs, makes sure that store types are of the correct types and then returns a clean store data dataframe.
   - `convert_kg_to_kg`: Takes in a dataframe as input.  Finds rows where the values contain 'kg' and strips it from the full string. Returns a dataframe where weight rows containing kg are just the number without the unit.
   - `convert_units_to_kg`: Takes in a dataframe as input. Loops through the product data, converting rows that have 'g' (for grams), 'ml' (for ml) and 'oz' (for ounces) to kg so that values in the 'Weight (kg) column are all standardised.
   - `convert_product_weights`: Takes in a dataframe as input.  Does the heavy-lifting of `convert_kg_to_kg` &  `convert_units_to_kg` as well as contains additional functionality: does maths for rows containing an 'x' (for multiplication/multipacks) to replace the weights with the arithmetic computation of the multiplications, for standardisation. Returns a pandas dataframe with standardised weights.
   - `clean_products_data`: Tames in a dataframe as input. It is recommended to use `convert_product_weights` before this to standardise weights. This method dropps NaN values and filters the dataframe to make sure that values in 'date_added' are the correct length.
   - `clean_orders_data`: Takes in a orders data DataFrame as input. Drops unneccessary columns and returns the dataframe as output. The data here is pretty good quality so not much needed to be done. This dataframe will be a 'ground truth' for other tables.
   - `clean_date_times`: Takes in a dataframe as input. Filters out dates containing weird values such as 'LQWJ3SJZL3JC' by filtering out the max length of dates. Returns a DataFrame.

## Installation instructions

Clone the repo using `git clone https://github.com/Qwandy/multinational-retail-data-centralisation`. This will give you access to the code. You should familiarise yourself with the methods (described in the section above in the README) and use them in your own code. 'data_cleaning.py' contains the DataCleaning class, 'data_extraction.py' contains the DataExtractor class and 'database_utils.py' contains the DatabaseConnector class. You can import these py files to your own code to use the methods within the classes.

## License

No License. Use this code as you please.


