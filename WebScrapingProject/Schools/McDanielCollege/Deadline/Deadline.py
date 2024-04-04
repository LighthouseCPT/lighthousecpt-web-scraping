import re
from bs4 import BeautifulSoup
from ...base_scraper import BaseScraper
from ...utils import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


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
        pattern = re.compile(r'Graduate Academic Schedule')

        match = soup.find(string=pattern).find_next('div').get_text(separator='\n', strip=True)

        df = pd.DataFrame([match])

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)

        upload_df_to_dynamodb(df, FILENAME)
