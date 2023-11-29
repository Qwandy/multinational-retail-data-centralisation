import pandas as pd
import numpy as np
import database_utils as db_u
import data_extraction as de

class DataCleaning():

    def __init__(self):
        pass

    def clean_user_data(self):
        my_db_conn = db_u.DatabaseConnector('db_creds.yaml')
        my_db_extractor = de.DataExtractor()


        # Setting a variable to None so I can overwrite it with the name of the user table
        user_table_name = None

        # A loop to find the name of the user table since it isn't just called 'user'
        for i in my_db_extractor.list_db_tables():
            if 'user' in i:
                user_table_name = i

        # Creating a pandas dataframe for the user table
        user_table = my_db_extractor.read_rds_table(my_db_conn, user_table_name)

        # Creating a list of columns
        user_table_columns = user_table.columns

        # Checking if any columns in user table have nulls
        for i in user_table_columns:
            if user_table[i].isnull().any():
                print(f"{i} has more than 0 NULL values.")
            else:
                continue
        
        #Checking if any columns in user table have NaNs
        for i in user_table_columns:
            if user_table[i].isna().any():
                print(f"{i} has more than 0 NaN values.")
            else:
                continue
        #print(user_table.head())

        # Phone numbers are very inconsistent, fixing it here:
        
        #list of country codes
        country_codes = ['DE', 'GB', 'US']

        # loop which iterates through country_codes list and removes country code prefix (i.e +44), brackets
        # and spaces to make phone numbers consistent.
        for code in country_codes:
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace('+49', '')
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace('(', '')
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace(')', '')
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace(' ', '')


        # Removing rows where the phone number is not 11 characters
        user_table = user_table[user_table['phone_number'].str.len() == 11]

        # Converting date of birth and join date columns to datetimes
        user_table['date_of_birth'] = pd.to_datetime(user_table['date_of_birth'], format='mixed')
        user_table['join_date'] = pd.to_datetime(user_table['join_date'], format='mixed')

        # Dropping strings that do not contain a @ in the email
        user_table = user_table[user_table.email_address.str.contains('@')]

        return user_table
    

if __name__ == "__main__":
    data_cleaner = DataCleaning()
    clean_table = data_cleaner.clean_user_data()
    print(clean_table)


