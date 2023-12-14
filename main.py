# Imports
import data_cleaning as dc 
import data_extraction as de 
import database_utils as db_u
import pandas as np
import pandas as pd
import requests as rq 
import boto3

# Pipeline function
def data_to_db(type = None, to_return = False):
        data_extractor = de.DataExtractor()
        data_cleaner = dc.DataCleaning()
        data_connector = db_u.DatabaseConnector('db_creds_local.yaml')
        data_connector_external = db_u.DatabaseConnector('db_creds.yaml')

        if type == 'card':
            if to_return == True:
                df_cards = data_extractor.retrieve_pdf_data('https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf')
                df_cards.to_csv('card_data.csv')
            else:
                clean_card_data = data_cleaner.clean_card_data('https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf')
                data_connector.upload_to_db(clean_card_data, 'dim_card_details')

        elif type == 'date_times':
            df_date_times = data_extractor.extract_from_s3('https://data-handling-public.s3.eu-west-1.amazonaws.com/date_details.json.', file = 'date_times')
            clean_date_times = data_cleaner.clean_date_times(df_date_times)
            data_connector.upload_to_db(clean_date_times, 'dim_date_times')

        elif type == 'products':
            df_products = data_extractor.extract_from_s3('s3://data-handling-public/products.csv', file = 'products')
            clean_products = data_cleaner.clean_products_data(df_products)
            data_connector.upload_to_db(clean_products, 'dim_products')

        elif type == 'store':
            df_store = data_extractor.retrieve_stores_data()
            clean_store_data = data_cleaner.clean_store_data(df_store)
            data_connector.upload_to_db(clean_store_data, 'dim_store_details')

        elif type == 'users':
            clean_user_data = data_cleaner.clean_user_data()
            data_connector.upload_to_db(clean_user_data, 'dim_users')

        elif type == 'orders':
            df_orders = data_extractor.read_rds_table(data_connector_external, 'orders_table')
            df_orders['card_number'] = df_orders['card_number'].astype(str)
            clean_orders = data_cleaner.clean_orders_data(df_orders)
            data_connector.upload_to_db(clean_orders, 'orders_table')
    
#data_to_db(type = 'card')
#data_to_db(type = 'orders')
#data_to_db(type = 'products')


# Making an artifical dataframe to test my methods on
'''card_numbers = ['123456789012345678', '??34567890123', '1234', None]
exp_dates = ['01/01', '01/02', '03/02', None]
card_provider = ['Visa', 'Mastercard', 'JCB 15 digit', 'JBC 16 digit']
date_payment_confirmed = ['2015-11-25', '2001-06-18', '2000-12-26', None]


test_card_df = pd.DataFrame({'card_number': card_numbers, 'expiry_date': exp_dates, 'card_provider': card_provider,
                             'date_payment_confirmed': date_payment_confirmed})

#dropna will drop null values
test_card_df = test_card_df.dropna()

# can replace '?' with empty string
test_card_df['card_number'] = test_card_df['card_number'].str.replace('?', '')
test_card_df = test_card_df.loc[test_card_df['card_number'].str.len() > 14]

print(test_card_df)'''
data_to_db(type = 'orders')
data_to_db(type = 'products')
#data_to_db(type = 'users')
#store_data.to_csv('store_data.csv')
#print('done')