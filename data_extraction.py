import pandas as pd
import database_utils as db_u
from sqlalchemy import inspect
import tabula as tb
import requests as rq
import json
import boto3
import data_cleaning as dc


class DataExtractor():

    #Initialise class
    def __init__(self):
        pass
        return
    
    def list_db_tables(self, db_yaml):
        
        #initialise Database Connector
        my_db_conn = db_u.DatabaseConnector(db_yaml)

        #Initialise engine using init_db_engine method from database_utils.py
        db_engine = my_db_conn.init_db_engine()

        #Initialise inspector to use for checking schema
        inspector = inspect(db_engine)
        
        #Use list comprehension with inspector get_table_names method to return list
        table_names = [table_name for table_name in inspector.get_table_names()]

        return table_names
    
    def read_rds_table(self, db_conn, table_name):
        
        #Initialise engine for use in pd.read_sql_table()
        engine = db_conn.init_db_engine()

        #read in sql table data with table name and return table as dataframe
        the_table = pd.read_sql_table(table_name, engine)

        return the_table
    
    def retrieve_pdf_data(self, link):
        
        dfs = tb.read_pdf(link, stream = True, pages = 'all')
        result_pdf_data = pd.concat(dfs[:])
        return result_pdf_data
    
    def list_number_of_stores(self, my_endpoint, certification):
        
        number_of_stores = rq.get(my_endpoint, headers = certification)

        return number_of_stores
    
    def retrieve_stores_data(self):
        
        # An integer which contains the number of stores, attained using the list_number_of_stores method.
        num_stores = self.list_number_of_stores('https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/number_stores',
                                                {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}).json()['number_stores']
        
        # An empty dictionary to append values obtained using request
        request_dictionary = {"index": [], 'address': [], 'longitude': [], 'lat': [], 'locality': [],
                              'store_code': [], 'staff_numbers': [], 'opening_date': [], 'store_type': [],
                              'latitude': [], 'country_code': [], 'continent': []}
        
        # A loop to go through all of the stores
        for i in list(range(num_stores)):
            
            # Initialising a temporary dictionary with all the stores details of a store with number i
            temp_dictionary = rq.get(f'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod/store_details/{i}',
                       headers = {'x-api-key': 'yFBQbwXe9J3sd6zWVAMrK6lcxxr0q1lr2PT6DDMX'}).json()

            # Another loop which loops through dictionary keys in the request dictionary and appends the 
            # value for that key
            for k in request_dictionary.keys():
                try:
                    request_dictionary[k].append(temp_dictionary[k])
                except KeyError:
                    continue

        # Creates the dataframe using the request dictionary and drops the index column
        store_data = pd.DataFrame.from_dict(request_dictionary)
        store_data = pd.DataFrame.from_dict(request_dictionary).drop('index', axis = 1)

        return store_data
        
    def extract_from_s3(self, address, file = None):
        s3 = boto3.client('s3')
        
        # Conditional for downloading product data
        if file == 'products':
            s3.download_file(address[8:27], address[26:38], 'products.csv')
            df = pd.read_csv('products.csv')
        # Conditional for downloading date_time data
        elif file == 'date_times':
            s3.download_file(address[8:28], address[56:73], 'date_times.json')
            df = pd.read_json('date_times.json')
        return df


if __name__ == "__main__":
    
    my_extractor = DataExtractor()
    my_cleaner = dc.DataCleaning()
    stores_data = my_extractor.retrieve_stores_data()
    database_connector = db_u.DatabaseConnector('db_creds_local.yaml')
    stores_data = my_cleaner.clean_store_data(stores_data)
    database_connector.upload_to_db(stores_data, 'dim_store_details')

        
