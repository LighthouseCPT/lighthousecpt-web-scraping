import requests
from log_config import configure_logger
import boto3
import pandas as pd
from io import StringIO

logger = configure_logger(__name__)


def make_request(url):
    try:
        page = requests.get(url)
        logger.info(f'Successfully made request to: {url}')
        return page
    except requests.RequestException as e:
        logger.error(f'Request error: {e}')
        raise


# Save HTML content to S3
def save_html_to_s3(page, HTML_BUCKET, S3_PATH):
    try:
        S3_PATH = S3_PATH + '.html'
        s3 = boto3.client('s3')
        s3.put_object(Bucket=HTML_BUCKET, Key=S3_PATH, Body=page.text.encode('utf-8'))
        logger.info(f'Successfully saved to: {S3_PATH}')
    except Exception as e:
        logger.error(f'S3 put object error: {e}')
        raise


# Get HTML content from S3
def get_html_from_s3(HTML_BUCKET, S3_PATH):
    try:
        S3_PATH = S3_PATH + '.html'
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=HTML_BUCKET, Key=S3_PATH)
        html_content = obj['Body'].read().decode()
        logger.info(f'Successfully read from: {S3_PATH}')
        return html_content
    except Exception as e:
        logger.error(f'S3 get object error: {e}')
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
        logger.info(f'Successfully saved to: {S3_PATH}')
    except Exception as e:
        logger.error(f'S3 put object error: {e}')
        raise
