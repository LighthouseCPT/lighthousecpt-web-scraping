from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3
                      )
from bs4 import BeautifulSoup, NavigableString
import pandas as pd

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
        save_html_to_s3(page, self.HTML_BUCKET, S3_PATH)

        # Get HTML content from S3
        html = get_html_from_s3(self.HTML_BUCKET, S3_PATH)

        # Start Extracting Logic
        soup = BeautifulSoup(html, 'html.parser')
        soup.find(string='On Campus MS Programs')

        # find the p tag following the string 'On Campus MS Programs'
        p_tag = soup.find(string='On Campus MS Programs').find_next('p')

        # create an empty list to store subsequent divs
        subsequent_divs = []

        # next_siblings will return a generator which include all the siblings (not only divs)
        for elem in p_tag.next_siblings:
            if isinstance(elem, NavigableString):  # Ignore string elements
                continue
            if elem.name == 'u' and elem.get_text(strip=True) == 'APPLY NOW':
                break  # Break when find 'APPLY NOW'
            if elem.name == 'div':
                subsequent_divs.append(elem)

        data = [div.get_text(separator='\n', strip=True) for div in subsequent_divs]
        filtered_data = list(filter(None, data))
        df = pd.DataFrame([filtered_data])

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)
