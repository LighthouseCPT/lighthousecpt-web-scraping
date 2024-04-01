from io import StringIO
import requests
from bs4 import BeautifulSoup
import pandas as pd
import boto3
from log_config import configure_logger

logger = configure_logger(__name__)


def TUITION_run(url):
    TABLE = 'Tuition'
    BUCKET = 'lighthousecpt-schools'
    DIRECTORY = 'TrineUniversity'
    FILENAME = f'{DIRECTORY}_{TABLE}.html'

    try:
        page = requests.get(url)
    except requests.RequestException as e:
        logger.error(f'Request error: {e}')
        raise

    # Save HTML content to S3
    s3 = boto3.client('s3')
    s3_path = f'{DIRECTORY}/{FILENAME}'

    try:
        s3.put_object(Bucket=BUCKET, Key=s3_path, Body=page.text.encode('utf-8'))
        logger.info(f'Successfully saved HTML content to: {s3_path}')
    except Exception as e:
        logger.error(f'S3 put object error: {e}')
        raise

    # Get HTML content from S3
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=s3_path)
        html_content = obj['Body'].read().decode()
        logger.info(f'Successfully read HTML content from: {s3_path}')
    except Exception as e:
        logger.error(f'S3 get object error: {e}')
        raise

    soup = BeautifulSoup(html_content, 'html.parser')

    tbl = soup.table
    df = pd.read_html(StringIO(str(tbl)))[0]
    logger.info(f'scrape_tuition {df}')

    return df
