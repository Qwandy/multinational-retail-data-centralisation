import pandas as pd
import database_utils as db_u
from sqlalchemy import inspect
import tabula as tb
import requests as rq
import json
import boto3
import data_cleaning as dc


class DataExtractor():
    '''A method for extracting all the data from various sources by making API calls and using boto3. Is able
    to find all the tables stored within a database, read in RDS tables, retrieve and transform PDF data into
    a pandas dataframe and can extract data from S3.'''

    #Initialise class
    def __init__(self):
        pass
        return
    
    def list_db_tables(self, db_yaml):
        ''' Provides a list of the tables names in a database. Takes in a path to a yaml file as input, 
        which should contain all data for initialising an engine.'''

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
        '''Initialises an engine and reads an RDS sql table. Takes in an instance of the DataConnector class
        and a table name string to read from the database.'''

        #Initialise engine for use in pd.read_sql_table()
        engine = db_conn.init_db_engine()

        #read in sql table data with table name and return table as dataframe
        the_table = pd.read_sql_table(table_name, engine)

        return the_table
    
    def retrieve_pdf_data(self, link):
        '''Retrieves tabular data from a PDF file. Takes in a URL as input for the PDF.'''

        # Tabular read_pdf method to turn pdf into pandas dataframe
        dfs = tb.read_pdf(link, pages = 'all')
        
        # Concatenating all of the PDF pages into one big dataframe
        result_pdf_data = pd.concat(dfs)
        
        return result_pdf_data
    
    def list_number_of_stores(self, my_endpoint, certification):
        '''Returns an integer of how many stores there are in a stores table. Takes in a endpoint 
        and api-key as input.'''

        # Api call to check the number of stores
        number_of_stores = rq.get(my_endpoint, headers = certification)

        return number_of_stores
    
    def retrieve_stores_data(self):
        '''Retrieves stores data. Takes no input.'''

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
        store_data = pd.DataFrame.from_dict(request_dictionary).drop('index', axis = 1) # Drop extra idx col

        return store_data
        
    def extract_from_s3(self, address, file = None):
        '''Extracts products or date_times data from s3. Takes in a URL of where the data is,
        and a file type string to specify what kind of file it is: either "product", or "date_times".'''

        s3 = boto3.client('s3')
        
        # Address url variable array
        address_arr = address.split('/')
        address_header = address_arr[2]
        address_pointer = address_arr[3]

        # Conditional for downloading product data
        if file == 'products':
            s3.download_file(address_header, address_pointer, 'products.csv')
            df = pd.read_csv('products.csv')
        # Conditional for downloading date_time data
        elif file == 'date_times':
            s3.download_file(address_header, address_pointer, 'date_times.json')
            df = pd.read_json('date_times.json')
        return df


        
