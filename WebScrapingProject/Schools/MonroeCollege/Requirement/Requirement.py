from ...utils import *
import re
from bs4 import BeautifulSoup
import pandas as pd
from ...base_scraper import BaseScraper
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


class RequirementScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Requirement'
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
        pattern = re.compile(r'Graduate Admissions for Master’s Degrees')
        data = soup.find(string=pattern).find_next('ul').get_text(separator='\n', strip=True)
        df = pd.DataFrame([data])

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)

        upload_df_to_dynamodb(df, FILENAME)