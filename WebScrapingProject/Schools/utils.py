import requests
import boto3
import pandas as pd
import io
from io import StringIO
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

# def get_pdf_from_s3(SOURCE_BUCKET, S3_PATH):
#     try:
#         S3_PATH = S3_PATH + '.pdf'
#         s3 = boto3.client('s3')
#         obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=S3_PATH)
#         pdf_content = obj['Body'].read()
#         return io.BytesIO(pdf_content)
#     except Exception as e:
#         logging.error(f'S3 get object error: {e}')
#         raise
