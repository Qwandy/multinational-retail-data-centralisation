import pandas as pd
import numpy as np
import database_utils as db_u
import data_extraction as de
import requests as rq


class DataCleaning():
    '''A class for performing all the data cleaning of the project.'''

    def __init__(self):
        pass

    def clean_user_data(self):
        '''Method for extracting and cleaning user data. Takes no inputs.'''

        my_db_conn = db_u.DatabaseConnector('db_creds.yaml')
        my_db_extractor = de.DataExtractor()


        # Setting a variable to None so I can overwrite it with the name of the user table
        user_table_name = None

        # A loop to find the name of the user table since it isn't just called 'user'
        for i in my_db_extractor.list_db_tables('db_creds.yaml'):
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
       

        # There is an outlier where 'GB' is 'GGB', fixing it here
        user_table = user_table.replace('GGB', 'GB')

        #list of country codes
        country_codes = ['DE', 'GB', 'US']

        # Filtering dataframe to rows where the country code is one of the above country codes
        user_table = user_table[user_table['country_code'].isin(country_codes)]

        # loop which iterates through country_codes list and removes country code prefix (i.e +44), brackets
        # and spaces to make phone numbers consistent.
        for code in country_codes:
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace('+49', '')
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace('(', '')
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace(')', '')
            user_table['phone_number'][user_table.country_code == code] = user_table['phone_number'][user_table.country_code == code].str.replace(' ', '')


        # Converting date of birth and join date columns to datetimes
        user_table['date_of_birth'] = pd.to_datetime(user_table['date_of_birth'], format='mixed')
        user_table['join_date'] = pd.to_datetime(user_table['join_date'], format='mixed')

        # Dropping strings that do not contain a @ in the email
        user_table = user_table[user_table.email_address.str.contains('@')]

        return user_table
    

    def clean_card_data(self, link):
        '''Method for cleaning card data. Takes a URL for where the data is stored as an input
        '''
        # Initialise extractor class
        extractor = de.DataExtractor()

        # Retrieve pandas dataframe of pdf link
        card_data = extractor.retrieve_pdf_data(link)

        # Remove '?' character from card numbers
        card_data = card_data.replace('\?', '', regex = True)

        # A list of legit card providers in the dataset to filter out random rows with 
        # card_numbers / providers like 'ALSK3123ASD'
        legit_providers = ['Diners Club / Carte Blanche', 'American Express', 'JCB 16 digit',
        'JCB 15 digit', 'Maestro', 'Mastercard', 'Discover', 'VISA 19 digit',
        'VISA 16 digit', 'VISA 13 digit']
        
        # Filtering the data to the legitimate card providers
        card_data = card_data[card_data['card_provider'].isin(legit_providers)]

        # Dropping NULL rows
        card_data = card_data.dropna()

        return card_data
    
    def clean_store_data(self, df):
        '''Method for cleaning store data. Takes in a dataframe as input'''

        # Drop latitude column since most of it is N/A or None, and should be latitude column anyway?
        df = df.drop(columns = ['lat'])
        
        # Doing some string formatting to make it cleaner
        df['address'] = df['address'].str.replace('\n', ' ')
        df['address'] = df['address'].str.replace('/', '')

        # Changing opening dates to date_times
        df['opening_date'] = pd.to_datetime(df['opening_date'], format='mixed', errors = 'coerce')

        # Adding data to web portal row so it isn't dropped with dropna
        df.at[0,'address']='online'
        df.at[0,'longitude']='0.00'
        df.at[0,'locality']='online'
        df.at[0,'latitude']='0.00'
        
        # Invalid datetimes are changed to 'NaT' so I will drop those rows
        df = df.dropna()

        # Dropping rows where store_type is not web_portal, local or super store
        df = df[df["store_type"].str.contains("Web Portal|Local|Super Store|Outlet|Mall Kiosk")]

        # Replaces strings in staff_numbers where it contains letters
        df['staff_numbers'] = df['staff_numbers'].str.replace('e', '')
        df['staff_numbers'] = df['staff_numbers'].str.replace('A', '')
        df['staff_numbers'] = df['staff_numbers'].str.replace('n', '')
        df['staff_numbers'] = df['staff_numbers'].str.replace('J', '')
        df['staff_numbers'] = df['staff_numbers'].str.replace('R', '')

        return df
    
    def convert_kg_to_kg(self, df):
        '''Method used in clean_product_data which strips kg substring from row values containing kg substring.
        Takes in a dataframe as input.'''

        # Replacing 'kg' with an empty string
        df['weight_in_kg'] = df['weight_in_kg'].where(df['weight_in_kg'][-2:] == 'kg',
                                                     df['weight_in_kg'].str.replace('kg', ''), axis = 0)

        return df
    
    def convert_units_to_kg(self, df):
        '''Method used in clean_product_data which strips (g, ml, oz) substrings from weight column
        and performs arithmetic calculations to convert those units to kg. Takes in a dataframe as input.'''

        # A tuple of numbers to check valid entries
        num_list = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')
        try:
            for i in range(len(df['weight_in_kg'])):
                if df['weight_in_kg'][i].endswith(num_list):
                    continue
                elif df['weight_in_kg'][i].endswith('g'):
                    df['weight_in_kg'][i] = df['weight_in_kg'][i].replace('g', '')
                    df['weight_in_kg'][i] = float(df['weight_in_kg'][i])
                    df['weight_in_kg'][i] = round(df['weight_in_kg'][i] / 1000, 4)
                elif df['weight_in_kg'][i].endswith('ml'):
                    df['weight_in_kg'][i] = df['weight_in_kg'][i].replace('ml', '')
                    df['weight_in_kg'][i] = float(df['weight_in_kg'][i])
                    df['weight_in_kg'][i] = round(df['weight_in_kg'][i] / 1000, 4)
                elif df['weight_in_kg'][i].endswith('oz'):
                    df['weight_in_kg'][i] = df['weight_in_kg'][i].replace('oz', '')
                    df['weight_in_kg'][i] = float(df['weight_in_kg'][i])
                    df['weight_in_kg'][i] = round(df['weight_in_kg'][i] * 0.283, 4)
            
        # Except to allow code to continue running if error encountered
        except KeyError:
            print(f"an error occured at key {i}")

        return df
    
    
    
    def convert_product_weights(self, df):
        '''Does additional data manipulation and cleaning. Takes in a dataframe as input.'''

        # Renaming column because i'm standardising units for row values
        df = df.rename(columns = {'weight': 'weight_in_kg'})

        # Dropping NaN values because they will mess with the loops I run later
        df = df.dropna()

        # Correcting for rows where products are multipacks as they will break my loop
        df.loc[df['weight_in_kg'].str.contains('12 x 100'), 'weight_in_kg'] = '1.200'
        df.loc[df['weight_in_kg'].str.contains('8 x 150'), 'weight_in_kg'] = '1.200'
        df.loc[df['weight_in_kg'].str.contains('6 x 412'), 'weight_in_kg'] = '2.472'
        df.loc[df['weight_in_kg'].str.contains('6 x 400'), 'weight_in_kg'] = '2.400'
        df.loc[df['weight_in_kg'].str.contains('8 x 85'), 'weight_in_kg'] = '0.68'
        df.loc[df['weight_in_kg'].str.contains('40 x 100'), 'weight_in_kg'] = '4.00'
        df.loc[df['weight_in_kg'].str.contains('12 x 85'), 'weight_in_kg'] = '1.020'
        df.loc[df['weight_in_kg'].str.contains('3 x 2'), 'weight_in_kg'] = '0.006'
        df.loc[df['weight_in_kg'].str.contains('g .'), 'weight_in_kg'] = '0.077'
        df.loc[df['weight_in_kg'].str.contains('3 x 90'), 'weight_in_kg'] = '0.27'
        df.loc[df['weight_in_kg'].str.contains('16 x 10'), 'weight_in_kg'] = '1.6'
        df.loc[df['weight_in_kg'].str.contains('3 x 132'), 'weight_in_kg'] = '0.394'
        df.loc[df['weight_in_kg'].str.contains('5 x 145'), 'weight_in_kg'] = '0.725'
        df.loc[df['weight_in_kg'].str.contains('4 x 400'), 'weight_in_kg'] = '1.6'
        df.loc[df['weight_in_kg'].str.contains('2 x 200'), 'weight_in_kg'] = '0.4'
        
        # Creating a list of legitimate categories
        category_list = ['toys-and-games', 'sports-and-leisure', 'pets', 'homeware', 'health-and-beauty',
                         'food-and-drink', 'diy']
        
        # Using pd isin to filter rows with only legitimate categories to remove rows containing
        # entries such as 'C3NCA2CL35'
        df = df[df['category'].isin(category_list)]

        # Resetting index after dropping NaN values
        df = df.reset_index(drop=True)

        # Stripping rows which have 'kg' unit to be unitless
        df = self.convert_kg_to_kg(df)

        # Converting g, ml, oz to kg
        df = self.convert_units_to_kg(df)

        return df

    def clean_products_data(self, df):
        '''Calls the convert_product weights function. This is the master method for cleaning product data,
        and calls other methods for doing so. Takes in a dataframe as input.'''

        # Calling method that converts all the units to standardise weight column
        df = self.convert_product_weights(df)

        # Drops nan values
        df = df.dropna()
        
        return df
    
    def clean_orders_data(self, df):
        '''A method for cleaning orders data. Takes in a dataframe as input.'''

        # Dropping level_0 column because it is a repeat of index, first_name, last_name and 1
        df = df.drop(labels = ['level_0', 'first_name', 'last_name', '1'], axis = 1)

        # Drop rows where card_number or expiry date are Nones
        df = df.dropna()

        # Replace '?' in card number with empty string
        df['card_number'] = df['card_number'].str.replace('?', '')
        
        # Make sure card number is between 14 and 
        df = df.loc[df['card_number'].str.len() >= 14]
        df = df.loc[df['card_number'].str.len() <= 19]
        
        return df

    def clean_date_times(self, df):
        '''A method for cleaning date_times data. Takes in a dataframe as input.'''

        # Filtering dataframe for where month is valid, i.e 1 -> 12 NOT something like 'LZLLPZ0ZUA'
        df = df.loc[df['month'].str.len() <= 2]

        return df

