import yaml
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

class DatabaseConnector():

    def __init__(self, yaml_file):
        self.yaml_file = yaml_file

    def _read_db_creds(self):
        with open(self.yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        return data
    
    def init_db_engine(self):
        #Return credentials to variable with _read_db_creds method
        db_creds = self._read_db_creds()

        #Initialising dictionary values to variables for engine creation
        DATABASE_TYPE = 'postgresql'
        DBAPI = 'psycopg2'
        USER = db_creds['RDS_USER']
        PASSWORD = db_creds['RDS_PASSWORD']
        ENDPOINT = db_creds['RDS_HOST']
        PORT = db_creds['RDS_PORT']
        DATABASE = db_creds['RDS_DATABASE']

        engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
        return engine
    
    def upload_to_db(self, df, table_name):
        
        # initialise engine
        db_engine = self.init_db_engine()

        # connect to database
        db_engine.connect()

        # push dataframe to database
        df.to_sql(table_name, db_engine, if_exists = 'replace')




            
    


