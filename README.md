# Multinational-retail-data-centralisation (MRDC)

## Project Brief

The aim of this project is to use various Python cloud tools and data extractors (such as Boto3, SQLAlchemy, tabular-py, json) to make my own OOP-based Python package for extracting and cleaning data and having the option to upload to a cloud database. I have achieved these aims and made a Python package with tools that can perform these tasks.

## The Data

In this section I show the architecture of the various tables used in this project for which I extracted the data. The tables show the format that the data came in and the changes I made to keep the data storage-efficient.

The MRDC data is comprised of multiple tables relating to:
- User data 

![Alt text](users_data.JPG)

- Customer card details

![Alt text](card_data.JPG)

- Store data

![Alt text](store_data.JPG)

- Product data

![Alt text](products_data.JPG)

- Orders data

![Alt text](orders_data.JPG)

- Date times data

![Alt text](date_times_data.JPG)

## Project Dependencies

## Tools Used


## Installation instructions

Clone the repo using `git clone https://github.com/Qwandy/multinational-retail-data-centralisation`. This will give you access to the code. You should familiarise yourself with the methods in the python file if you wish to explore and use them in your own code. 'data_cleaning.py' contains the DataCleaning class, 'data_extraction.py' contains the DataExtractor class and 'database_utils.py' contains the DatabaseConnector class. You can import these py files to your own code to use the methods within the classes.

## License

No License. Use this code as you please.

## Features
- Data extracting, cleaning, and cloud compting package to explore.
- SQL Database engineering and data querying files.

