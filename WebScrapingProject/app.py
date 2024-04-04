import json
import os
from importlib import import_module
from log_config import configure_logger
from Schools.SchoolScraper import SchoolScraper

logging = configure_logger(__name__)


class MainSchoolScraper:
    # This bucket includes HTMLs and PDFs
    SOURCE_BUCKET = 'lighthousecpt-schools-source'

    # This bucket contains the somewhat unrefined, extracted Information in CSVs
    CSV_BUCKET = 'lighthousecpt-schools-csv'

    SCHOOLS = [
        'TrineUniversity',
        'NewEnglandCollege',
        'MonroeCollege',
        'WestcliffUniversity',
        'McDanielCollege',
        'CaliforniaInstituteofAdvancedManagement'
        'SofiaUniversity'
    ]

    def scrape_and_save(self, event):
        for school in event['schools']:
            school_name = school['name']
            info = school
            if school_name not in self.SCHOOLS:
                logging.error(f"No scraping function found for school: {school_name}")
                raise
            else:
                scraper_instance = SchoolScraper(self.SOURCE_BUCKET, self.CSV_BUCKET, school_name, info)
                scraper_instance.scrape(info)


def lambda_handler(event, context):
    scraper = MainSchoolScraper()
    scraper.scrape_and_save(event)


# The following is solely for local testing; AWS Lambda will NOT execute it. 
# AWS Lambda will execute the "lambda_handler" function above.
if __name__ == "__main__":
    parent_directory = os.path.dirname(os.getcwd())
    event_path = os.path.join('events', 'event.json')
    with open(event_path, 'r') as file:
        event_data = json.load(file)
    scraper_ = MainSchoolScraper()
    scraper_.scrape_and_save(event_data)
