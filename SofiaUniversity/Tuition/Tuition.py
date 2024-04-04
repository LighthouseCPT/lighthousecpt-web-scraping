import os

from bs4 import BeautifulSoup
from io import StringIO
from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3,
                      get_csv_from_s3)
import pandas as pd
from log_config import configure_logger

logging = configure_logger(__name__)


class TuitionScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Tuition'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # If PDF, then get the RAW CSV
        df = None
        if url == 'PDF':
            _FILENAME = FILENAME + '_RAW'
            _S3_PATH = f'{self.SCHOOL_NAME}/{_FILENAME}'
            try:
                df = get_csv_from_s3(self.SOURCE_BUCKET, _S3_PATH)

            except ValueError as e:
                error_msg = (f"Since {url}, a RAW CSV file named '{_FILENAME}' should be present at location "
                             f"'{self.SOURCE_BUCKET}/{self.SCHOOL_NAME}'. However, this file was not found. Please "
                             f"ensure it's correctly placed.")
                logging.error(f'{str(e)} Additional Info: {error_msg}')
                raise

        # Start Extracting Logic

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)

        upload_df_to_dynamodb(df, FILENAME)
