import requests
import boto3
import pandas as pd
import io
from io import StringIO
from decimal import Decimal
import numpy as np
from log_config import configure_logger

logging = configure_logger(__name__)


def make_request(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, '
                                 'like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        page = requests.get(url, headers=headers)
        logging.info(f'Successfully made request to: {url}')
        return page
    except requests.RequestException as e:
        logging.error(f'Request error: {e}')
        raise


# Save HTML content to S3
def save_html_to_s3(page, SOURCE_BUCKET, S3_PATH):
    try:
        S3_PATH = S3_PATH + '.html'
        s3 = boto3.client('s3')
        s3.put_object(Bucket=SOURCE_BUCKET, Key=S3_PATH, Body=page.text.encode('utf-8'))
        logging.info(f'Successfully saved to: {S3_PATH}')
    except Exception as e:
        logging.error(f'S3 put object error: {e}')
        raise


# Get HTML content from S3
def get_html_from_s3(SOURCE_BUCKET, S3_PATH):
    try:
        S3_PATH = S3_PATH + '.html'
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=S3_PATH)
        html_content = obj['Body'].read().decode()
        logging.info(f'Successfully read from: {S3_PATH}')
        return html_content
    except Exception as e:
        logging.error(f'S3 get object error: {e}')
        raise


# Save to S3 as CSV file
def save_csv_to_s3(df, CSV_BUCKET, S3_PATH):
    S3_PATH = S3_PATH + '.csv'
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    csv_buffer.seek(0)
    try:
        s3 = boto3.client('s3')
        s3.put_object(Bucket=CSV_BUCKET, Key=S3_PATH, Body=csv_buffer.getvalue())
        logging.info(f'Successfully saved to: {S3_PATH}')
    except Exception as e:
        logging.error(f'S3 put object error: {e}')
        raise


def get_csv_from_s3(SOURCE_BUCKET: str, S3_PATH: str) -> pd.DataFrame:
    """
    Function to read a CSV file from an S3 bucket and convert it into a Pandas DataFrame

    Parameters:
    SOURCE_BUCKET (str): The name of the S3 bucket
    S3_PATH (str): The path to the CSV file in the S3 bucket

    Returns:
    pd.DataFrame: A pandas dataframe containing the data of the CSV file
    """
    try:
        S3_PATH = S3_PATH + '.csv'
        s3 = boto3.client('s3')
        csv_obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=S3_PATH)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_string))
        logging.info(f'Successfully retrieved. Key: {S3_PATH}, Bucket: {SOURCE_BUCKET}.')
        return df
    except Exception as e:
        error_msg = f'Failed to retrieve. Key: {S3_PATH}, Bucket: {SOURCE_BUCKET}. {str(e)}'
        raise ValueError(error_msg) from None


def get_raw_csv_from_s3(FILENAME, SCHOOL_NAME, SOURCE_BUCKET):
    _FILENAME = FILENAME + '_RAW'
    _S3_PATH = f'{SCHOOL_NAME}/{_FILENAME}'
    try:
        df = get_csv_from_s3(SOURCE_BUCKET, _S3_PATH)
        return df
    except ValueError as e:
        error_msg = (f"A CSV file named '{_FILENAME}' should be present at location "
                     f"'{SOURCE_BUCKET}/{SCHOOL_NAME}'. However, this file was not found. Please "
                     f"ensure it's correctly placed.")
        logging.error(f'{str(e)} Additional Info: {error_msg}')
        raise


def get_pdf_from_s3(FILENAME, SCHOOL_NAME, SOURCE_BUCKET):
    _FILENAME = FILENAME + '.pdf'
    S3_PATH = f'{SCHOOL_NAME}/{_FILENAME}'
    try:
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=S3_PATH)
        pdf_content = obj['Body'].read()
        return io.BytesIO(pdf_content)
    except Exception as e:
        error_msg = (f"A PDF file named '{_FILENAME}' should be present at location "
                     f"'{SOURCE_BUCKET}/{SCHOOL_NAME}'. However, this file was not found. Please "
                     f"ensure it's correctly placed.")
        logging.error(f'{str(e)} Additional Info: {error_msg}')
        raise


def float_to_decimal(value):
    if isinstance(value, float):
        if np.isnan(value):  # Handle NaNs
            return None
        elif np.isinf(value):  # Handle Infinity
            return None
        return Decimal(str(value))
    return value


def upload_df_to_dynamodb(df, table_name):
    dynamodb = boto3.resource('dynamodb')

    # Add an 'id' column as the primary key
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'id'}, inplace=True)

    try:
        table = dynamodb.Table(table_name)
        table.load()
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        # create table.
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 10,
                'WriteCapacityUnits': 10
            }
        )

        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)

    # Convert any NaN or Infinity values to None, and floats to decimals
    df = df.applymap(float_to_decimal)

    # Convert DataFrame into list of dictionaries (JSON). Ensure that keys are strings.
    items = [{str(key): value for key, value in item.items()} for item in df.to_dict('records')]

    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
