from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3
                      )

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def header_exists(table):
    thead = table.find('thead')
    return thead is not None


class DeadlineScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Deadline'
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
        tables = soup.find_all('table')

        df_list = []
        for table in tables:
            h3 = table.find_previous_sibling('h3')
            if h3 is not None:
                str_io = StringIO(str(table))
                if header_exists(table):
                    temp_df = pd.read_html(str_io)[0]
                else:
                    temp_df = pd.read_html(str_io, header=None)[0]
                    temp_df.columns = ['Date', 'Information']

                temp_df['Term'] = h3.get_text()
                df_list.append(temp_df)

        df = pd.concat(df_list, ignore_index=True)

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)