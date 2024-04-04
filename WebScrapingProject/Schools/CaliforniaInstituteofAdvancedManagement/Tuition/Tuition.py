from bs4 import BeautifulSoup
from ...base_scraper import BaseScraper
from ...utils import *
from log_config import configure_logger

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
        tbl1 = soup.find(string='Estimated Tuition Rates 2022-2023').find_next('table')
        df1 = pd.read_html(str(tbl1))[0]
        tbl2 = soup.find(string='Student Fees 2022-2023').find_next('table')
        df2 = pd.read_html(str(tbl2))[0]
        head_str = 'Cost of Attendance'
        _ = soup.find(string=head_str).find_next('ul').get_text(strip=True, separator='\n')
        df3 = pd.DataFrame([_], columns=[head_str])
        df4 = pd.concat([df1, df2, df3])

        # Save to S3 as CSV File
        save_csv_to_s3(df4, self.CSV_BUCKET, S3_PATH)
