from bs4 import BeautifulSoup
import pandas as pd
from ...base_scraper import BaseScraper
from ...utils import (make_request,
                      save_html_to_s3,
                      get_html_from_s3,
                      save_csv_to_s3,
                      get_pdf_from_s3)
from pypdf import PdfReader


class RequirementScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Requirement'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # If PDF, then get the PDF
        pdf = None
        if url == 'PDF':
            pdf = get_pdf_from_s3(FILENAME, self.SCHOOL_NAME, self.SOURCE_BUCKET)

        # Start Extracting Logic
        reader = PdfReader(pdf)
        number_of_pages = len(reader.pages)

        # Create an empty string to store all text
        all_text = ""

        # Loop through all pages and append their text to all_text
        for i in range(number_of_pages):
            page = reader.pages[i]
            all_text += page.extract_text() + "\n"  # Add a newline after each page's text

        df = pd.DataFrame([all_text])

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)
