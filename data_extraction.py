import pandas as pd
import database_utils as db_u
from sqlalchemy import inspect
import tabula as tb


class DataExtractor():

    #Initialise class
    def __init__(self):
        pass
        return
    
    def list_db_tables(self):
        
        #initialise Database Connector
        my_db_conn = db_u.DatabaseConnector('db_creds.yaml')

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
        
        return dfs
    








my_db_conn = db_u.DatabaseConnector('db_creds.yaml')
my_db_extractor = DataExtractor()
pdf_data = my_db_extractor.retrieve_pdf_data('https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf')
print(pdf_data)
#Setting a variable to None so I can overwrite it with the name of the user table
user_table_name = None

#A loop to find the name of the user table since it isn't just called 'user'
#for i in my_db_extractor.list_db_tables():
#    if 'user' in i:
#        user_table_name = i

#Creating a pandas dataframe for the user table
#user_table = my_db_extractor.read_rds_table(my_db_conn, user_table_name)


#print(user_table.isnull().sum())


        
