from bs4 import BeautifulSoup
from ...base_scraper import BaseScraper
from ...utils import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
columns = ['Graduate', 'Doctor']
df = pd.DataFrame(columns=columns)
TABLE = 'Requirement'


class RequirementScraper(BaseScraper):
    def scrape(self, url):

        TYPE = 'Requirement'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # Since there are 2 HTMLs we need, will create 2x S3 Paths
        GRADUATE_S3_PATH = S3_PATH + '_GRADUATE'
        DOCTOR_S3_PATH = S3_PATH + '_DOCTOR'

        GRADUATE_URL = url['graduate']
        DOCTOR_URL = url['doctor']

        # Make URL Request
        GRADUATE_PAGE = make_request(GRADUATE_URL)
        DOCTOR_PAGE = make_request(DOCTOR_URL)

        # Save HTML Content to S3
        save_html_to_s3(GRADUATE_PAGE, self.SOURCE_BUCKET, GRADUATE_S3_PATH)
        save_html_to_s3(DOCTOR_PAGE, self.SOURCE_BUCKET, DOCTOR_S3_PATH)

        # Get HTML content from S3
        GRADUATE_HTML = get_html_from_s3(self.SOURCE_BUCKET, GRADUATE_S3_PATH)
        DOCTOR_HTML = get_html_from_s3(self.SOURCE_BUCKET, DOCTOR_S3_PATH)

        # Start Extracting Logic
        graduate_soup = BeautifulSoup(GRADUATE_HTML, 'html.parser')
        h2_tag = graduate_soup.find('h2', string="International Graduate/Master's Degree application")
        text = h2_tag.find_next_sibling("ul").find_next_sibling("ul").find('li').get_text(separator='\n', strip=True)
        df.at[0, 'Graduate'] = text

        doctor_soup = BeautifulSoup(DOCTOR_HTML, 'html.parser')
        text = doctor_soup.find(string='Admission Requirements').find_next('li').get_text(separator='\n', strip=True)
        df.at[0, 'Doctor'] = text

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)

        upload_df_to_dynamodb(df, FILENAME)
