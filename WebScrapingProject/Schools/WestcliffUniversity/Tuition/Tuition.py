from bs4 import BeautifulSoup
from io import StringIO
from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3
                      )
import pandas as pd
from log_config import configure_logger
import re
from babel.numbers import format_currency

logging = configure_logger(__name__)


class TuitionScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Tuition'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # Make URL Request
        page = make_request(url)

        # Save HTML Content to S3
        save_html_to_s3(page, self.SOURCE_BUCKET, S3_PATH)

        # Get HTML content from S3
        html = get_html_from_s3(self.SOURCE_BUCKET, S3_PATH)

        # Start Extracting Logic
        soup = BeautifulSoup(html, 'html.parser')
        tbl = soup.table
        df = pd.read_html(StringIO(str(tbl)))[0]

        # Due to certain rows being merged across the table they appear in every row.  
        # We need only the first of these sections called 'Degree Program Tuition'
        same_values_mask = df.apply(lambda row: row.nunique() == 1, axis=1)
        split_indices = same_values_mask[same_values_mask].index.tolist()

        df = df[1:split_indices[1]]
        df.columns = ['Program', 'RequiredCredits', 'Cost']
        # Extracting numeric part from 'Cost' column
        df['Cost_Numeric'] = df['Cost'].str.extract(r'(\d+)').astype(int)

        # Extracting numeric part from 'RequiredCredits' column
        df['RequiredCredits_Numeric'] = df['RequiredCredits'].str.split().str[0].astype(int)

        # Calculating total cost
        df['TotalCost'] = df['Cost_Numeric'] * df['RequiredCredits_Numeric']
        df['TotalCost'] = df['TotalCost'].apply(lambda x: format_currency(x, currency="USD", locale="en_US"))

        df.drop(['RequiredCredits_Numeric', 'Cost_Numeric'], axis=1, inplace=True)

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)
