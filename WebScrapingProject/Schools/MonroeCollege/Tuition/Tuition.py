import os

from bs4 import BeautifulSoup
from io import StringIO
from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3,
                      get_csv_from_s3,
                      get_raw_csv_from_s3)
import pandas as pd
from log_config import configure_logger

logging = configure_logger(__name__)


class TuitionScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Tuition'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # If RAW_CSV, then get the CSV
        df = None
        if url == 'RAW_CSV':
            df = get_raw_csv_from_s3(FILENAME, self.SCHOOL_NAME, self.SOURCE_BUCKET)

        # Start Extracting Logic
        df.columns = range(df.shape[1])
        df.drop(df.columns[4], axis=1, inplace=True)
        df[1] = df[1].apply(lambda x: x + ' and Fees' if str(x) == 'Full time Tuition' else x)
        df[2] = df[2].apply(lambda x: x + ' Credit' if str(x) == 'Cost Per' else x)
        df.loc[df[1] == 'Full time Tuition and Fees', 2] = 'Cost Per Credit'
        df[3] = df[3].apply(lambda x: x + ' Class' if str(x) == 'Cost Per' else x)
        df[2] = df[2].combine_first(df[3])
        df.drop(df.columns[3], axis=1, inplace=True)
        df = df.loc[~df[0].isin(["and Fees", "Credit", "Class"])]

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)
