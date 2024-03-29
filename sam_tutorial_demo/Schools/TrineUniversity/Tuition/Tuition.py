from io import StringIO
import requests
from bs4 import BeautifulSoup
import pandas as pd
import boto3


def TUITION_run(url):
    TABLE = 'Tuition'
    BUCKET = 'imbilalx'
    DIRECTORY = 'TrineUniversity'
    FILENAME = f'{DIRECTORY}_{TABLE}.html'

    page = requests.get(url)

    # Save HTML content to S3
    s3 = boto3.client('s3')
    s3_path = f'{DIRECTORY}/{FILENAME}'
    s3.put_object(Bucket=BUCKET, Key=s3_path, Body=page.text.encode('utf-8'))

    # Get HTML content from S3
    obj = s3.get_object(Bucket=BUCKET, Key=s3_path)
    html_content = obj['Body'].read().decode()

    soup = BeautifulSoup(html_content, 'html.parser')

    tbl = soup.table
    df = pd.read_html(StringIO(str(tbl)))[0]
    print(f'scrape_tuition {df}')

    return df
