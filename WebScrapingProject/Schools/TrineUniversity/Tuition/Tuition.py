from bs4 import BeautifulSoup
from io import StringIO
import boto3
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3
                      )
import pandas as pd
from log_config import configure_logger

logger = configure_logger(__name__)


def TUITION_run(url, HTML_BUCKET, CSV_BUCKET, SCHOOL_NAME):
    TYPE = 'Tuition'
    FILENAME = f'{SCHOOL_NAME}_{TYPE}'
    S3_PATH = f'{SCHOOL_NAME}/{FILENAME}'

    page = make_request(url)

    # Save HTML content to S3
    save_html_to_s3(page, HTML_BUCKET, S3_PATH)

    # Get HTML content from S3
    html = get_html_from_s3(HTML_BUCKET, S3_PATH)

    # Start extracting logic
    soup = BeautifulSoup(html, 'html.parser')
    tbl = soup.table
    df = pd.read_html(StringIO(str(tbl)))[0]

    # Save to S3 as CSV file
    save_csv_to_s3(df, CSV_BUCKET, S3_PATH)
