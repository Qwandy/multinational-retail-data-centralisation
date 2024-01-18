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
To run this project, the following packages need to be installed (I have provided a requirements.txt file which can be used to install these)
- Boto3 
- Pandas 
- SQLAlchemy 
- PyYAML 


## Tools Used
- [Boto3](https://aws.amazon.com/sdk-for-python/) to interface with AWS programmatically. From the [documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html):
> You use the AWS SDK for Python (Boto3) to create, configure, and manage AWS services, such as Amazon Elastic  Compute Cloud (Amazon EC2) and Amazon Simple Storage Service (Amazon S3). The SDK provides an object-oriented API as well as low-level access to AWS services.


- Pandas for housing and cleaning the extracted data.
- SQLAlchemy for creating an engine that allows connecting to data sources for programmatic extraction.
- PyYAML for creating files containing data necessary to create SQLAlchemy engines.
- Requests for writing API calls that extract data.

## Installation instructions

Clone the repo using `git clone https://github.com/Qwandy/multinational-retail-data-centralisation`. This will give you access to the code. You should familiarise yourself with the methods in the python file if you wish to explore and use them in your own code. 'data_cleaning.py' contains the DataCleaning class, 'data_extraction.py' contains the DataExtractor class and 'database_utils.py' contains the DatabaseConnector class. You can import these py files to your own code to use the methods within the classes.

## License

No License. Use this code as you please.

## Features
- Data extracting, cleaning, and cloud compting package to explore.
- SQL Database engineering and data querying files.

