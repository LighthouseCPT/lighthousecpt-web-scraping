import requests
from bs4 import BeautifulSoup
import pandas as pd
from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3
                      )

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)

class RequirementScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Requirement'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # Since there are 2 HTMLs we need, will create 2x S3 Paths
        DBA_S3_PATH = S3_PATH + '_DBA'
        EdD_S3_PATH = S3_PATH + '_EdD'

        DBA_URL = url['DBA']
        EdD_URL = url['EdD']

        # Make URL Request
        DBA_PAGE = make_request(DBA_URL)
        EdD_PAGE = make_request(EdD_URL)

        # Save HTML Content to S3
        save_html_to_s3(DBA_PAGE, self.SOURCE_BUCKET, DBA_S3_PATH)
        save_html_to_s3(EdD_PAGE, self.SOURCE_BUCKET, EdD_S3_PATH)

        # Get HTML content from S3
        DBA_HTML = get_html_from_s3(self.SOURCE_BUCKET, DBA_S3_PATH)
        EdD_HTML = get_html_from_s3(self.SOURCE_BUCKET, EdD_S3_PATH)

        DBA_soup = BeautifulSoup(DBA_HTML.text, 'html.parser')
        EdD_soup = BeautifulSoup(EdD_HTML.text.replace("\n", ""), 'html.parser')
        
        # Find the specified <a> tag based on its text
        specified_a_tag1 = DBA_soup.find('a', text=lambda text: text and 'admission' in text.lower() and 'requirements' in text.lower())
        DBA_areqs = specified_a_tag1.find_next_sibling('div').text.strip().replace('criteria:','criteria: ')
        
        specified_a_tag2 = DBA_soup.find('a', text=lambda text: text and 'graduation' in text.lower() and 'requirements' in text.lower())
        ## A LOT OF TEXT ON THIS ONE: 
        ## DBA_greqs = ' '.join(specified_a_tag2.find_next_sibling('div').stripped_strings)  
        ## SHORT VERSION:
        DBA_greqs = ' '.join([tag.get_text(separator=" ").strip() for tag in specified_a_tag2.find_next_sibling('div').find_all_next('p', limit=2)])

        specified_a_tag3 = EdD_soup.find('a', text=lambda text: text and 'admission' in text.lower() and 'requirements' in text.lower())
        EdD_areqs = specified_a_tag3.find_next_sibling('div').text.strip()
        
        specified_a_tag4 = EdD_soup.find('a', text=lambda text: text and 'graduation' in text.lower() and 'requirements' in text.lower())
        EdD_greqs = specified_a_tag4.find_next_sibling('div').text.strip()

        df = pd.DataFrame({
            'Program': ['Doctor of Business Administration (DBA)', 'Doctor of Education in Leadership, Curriculum, and Instruction (EdD)'],
            'Admission Requirements': [DBA_areqs, EdD_areqs],
            'Graduation Requirements': [DBA_greqs, EdD_greqs]
        })

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)
