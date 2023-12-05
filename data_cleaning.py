import pandas as pd
import numpy as np
import database_utils as db_u
import data_extraction as de
import requests as rq


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
    
    def clean_card_data(self, link):
        
        # Initialise extractor class
        extractor = de.DataExtractor()

        # Retrieve pandas dataframe of pdf link
        card_data = extractor.retrieve_pdf_data(link)

        # Drop columns that tabular read_pdf method created which are full of NaNs
        card_data = card_data.drop(labels = ['card_number expiry_date', 'Unnamed: 0'], axis = 1)

        # Drop rows where card_number or expiry date are Nones
        card_data = card_data.loc[card_data['card_number'] != None]
        card_data = card_data.loc[card_data['expiry_date'] != None]

        # Drop rows where card number is greather than 16 or less than than 19
        card_data = card_data.loc[card_data['card_number'].str.len() > 16]
        card_data = card_data.loc[card_data['card_number'].str.len() < 19]
        
        return card_data
    
    def clean_store_data(self, df):
        
        # Drop latitude column since most of it is N/A or None, and should be latitude column anyway?
        df = df.drop('lat', axis = 1)
        
        # Doing some string formatting to make it cleaner
        df['address'] = df['address'].str.replace('\n', ' ')
        df['address'] = df['address'].str.replace('/', '')

        # Changing opening dates to date_times
        df['opening_date'] = pd.to_datetime(df['opening_date'], format='mixed', errors = 'coerce')

        # Invalid datetimes are changed to 'NaT' so I will drop those rows
        df = df.dropna()

        # Dropping rows where store_type is not web_portal, local or super store
        df = df[df["store_type"].str.contains("Web Portal|Local|Super Store")]

        return df
    
    def convert_kg_to_kg(self, df):
        
        df['weight (kg)'] = df['weight (kg)'].where(df['weight (kg)'][-2:] == 'kg',
                                                     df['weight (kg)'].str.replace('kg', ''), axis = 0)

        return df
    
    def convert_units_to_kg(self, df):

        try:
            for i in range(len(df['weight (kg)'])):
                if df['weight (kg)'][i].endswith('g'):
                    df['weight (kg)'][i] = df['weight (kg)'][i].replace('g', '')
                    df['weight (kg)'][i] = float(df['weight (kg)'][i])
                    df['weight (kg)'][i] = round(df['weight (kg)'][i] / 1000, 4)
                elif df['weight (kg)'][i].endswith('ml'):
                    df['weight (kg)'][i] = df['weight (kg)'][i].replace('ml', '')
                    df['weight (kg)'][i] = float(df['weight (kg)'][i])
                    df['weight (kg)'][i] = round(df['weight (kg)'][i] / 1000, 4)
                elif df['weight (kg)'][i].endswith('oz'):
                    df['weight (kg)'][i] = df['weight (kg)'][i].replace('oz', '')
                    df['weight (kg)'][i] = float(df['weight (kg)'][i])
                    df['weight (kg)'][i] = round(df['weight (kg)'][i] * 0.283, 4)
                else:
                    df = df.drop(i)
                

        except KeyError:
            print(f"an error occured at key {i}")
        return df
    
    
    
    def convert_product_weights(self, df):
        
        # Renaming column because i'm standardising units for row values
        df = df.rename(columns = {'weight': 'weight (kg)'})

        # Dropping NaN values because they will mess with the loops I run later
        df = df.dropna()

        # Resetting index after dropping NaN values
        df = df.reset_index(drop=True)
        
        # Correcting for rows where products are multipacks as they will break my loop
        df.loc[df['weight (kg)'].str.contains('12 x 100'), 'weight (kg)'] = '1.200'
        df.loc[df['weight (kg)'].str.contains('8 x 150'), 'weight (kg)'] = '1.200'
        df.loc[df['weight (kg)'].str.contains('6 x 412'), 'weight (kg)'] = '2.472'
        df.loc[df['weight (kg)'].str.contains('6 x 400'), 'weight (kg)'] = '2.400'
        df.loc[df['weight (kg)'].str.contains('8 x 85'), 'weight (kg)'] = '0.68'
        df.loc[df['weight (kg)'].str.contains('40 x 100'), 'weight (kg)'] = '4.00'
        df.loc[df['weight (kg)'].str.contains('12 x 85'), 'weight (kg)'] = '1.020'
        df.loc[df['weight (kg)'].str.contains('3 x 2'), 'weight (kg)'] = '0.006'
        df.loc[df['weight (kg)'].str.contains('g .'), 'weight (kg)'] = '0.077'
        df.loc[df['weight (kg)'].str.contains('3 x 90'), 'weight (kg)'] = '0.27'
        df.loc[df['weight (kg)'].str.contains('16 x 10'), 'weight (kg)'] = '1.6'
        df.loc[df['weight (kg)'].str.contains('3 x 132'), 'weight (kg)'] = '0.394'
        df.loc[df['weight (kg)'].str.contains('5 x 145'), 'weight (kg)'] = '0.725'
        df.loc[df['weight (kg)'].str.contains('4 x 400'), 'weight (kg)'] = '1.6'
        df.loc[df['weight (kg)'].str.contains('2 x 200'), 'weight (kg)'] = '0.4'
        
        # Stripping rows which have 'kg' unit to be unitless
        df = self.convert_kg_to_kg(df)

        # Converting g, ml, oz to kg
        df = self.convert_units_to_kg(df)

        return df

    def clean_products_data(self, df):
        
        # Drops nan values
        df = df.dropna()

        # Filters data to rows where the 'opening date' is in the correct format.
        df = df.loc[df['date_added'].str.len() <= 10]

        
        return df
    
    def clean_orders_data(self, df):
        
        # Dropping level_0 column because it is a repeat of index, first_name, last_name and 1
        df = df.drop(columns = ['level_0', 'first_name', 'last_name', '1'])

        return df

    def clean_date_times(self, df):

        # Filtering dataframe for where month is valid, i.e 1 -> 12 NOT something like 'LZLLPZ0ZUA'
        df = df.loc[df['month'].str.len() <= 2]

        
        '''for col in df.columns:
            print(df[col].unique())'''
        
        # By using the loop above (which is now commented out) it appears that all the rows with non-valid
        # months/years/days/time_periods are for the same rows, so using the above .loc filter actually cleans
        # all the data without needing to clean columns individually.

        return df

if __name__ == "__main__":
    data_extractor = de.DataExtractor()
   