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
        soup = BeautifulSoup(html.text, 'html.parser')
        div_tag = soup.find('div', id="description2")
        paragraphs = div_tag.find_all('p')
        h3 = div_tag.find_all('h3')
        h3 = [t.contents[0] for t in h3]
        
        # Initialize lists to store data
        semesters = []
        session_dates = []
        deadlines = []
        
        # Iterate over paragraphs and extract data
        for p in paragraphs:
            strong_tag = p.find('strong')
            if strong_tag:
                semester_info = strong_tag.text.strip()
                deadline_info = p.text.replace(strong_tag.text, '').strip()[22:]
                semester, session_date = semester_info.split(' - ')
                semesters.append(semester)
                session_dates.append(session_date)
                deadlines.append(deadline_info)
        
        # Create DataFrame
        data = {'Semester': semesters, 'Session Date': session_dates, 'Application Deadline': deadlines}
        df = pd.DataFrame(data)
                
        # Add a new column with specified values based on ranges
        ranges_values = {(0, 5): h3[0], (6, 11): h3[1], (12,17): h3[2]}
        df['Student Type'] = [next((value for (start, end), value in ranges_values.items() if start <= i <= end), None) for i in range(len(df))]

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)