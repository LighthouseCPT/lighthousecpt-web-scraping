import json
import os
from Schools.TrineUniversity.TrineUniversity import TrineUniversityScraper
from Schools.NewEnglandCollege.NewEnglandCollege import NewEnglandCollegeScraper
from Schools.WestcliffUniversity.WestcliffUniversity import WestcliffUniversityScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class SchoolScraper:
    HTML_BUCKET = 'lighthousecpt-schools-html'
    CSV_BUCKET = 'lighthousecpt-schools-csv'
    SCHOOL_FUNCTION_MAP = {
        'TrineUniversity': TrineUniversityScraper,
        'NewEnglandCollege': NewEnglandCollegeScraper,
        'WestcliffUniversity': WestcliffUniversityScraper
    }

    def scrape_and_save(self, event):
        for school in event['schools']:
            school_name = school['name']
            info = school
            scraper_class = self.SCHOOL_FUNCTION_MAP.get(school_name)
            if scraper_class:
                scraper_instance = scraper_class(self.HTML_BUCKET, self.CSV_BUCKET)
                scraper_instance.scrape(info)
            else:
                logging.error(f"No scraping function found for school: {school_name}")
                raise


def lambda_handler(event, context):
    scraper = SchoolScraper()
    scraper.scrape_and_save(event)


# The following is solely for local testing; AWS Lambda will NOT execute it. 
# AWS Lambda will execute the "lambda_handler" function above.
if __name__ == "__main__":
    parent_directory = os.path.dirname(os.getcwd())
    event_path = os.path.join('events', 'event.json')
    with open(event_path, 'r') as file:
        event_data = json.load(file)
    scraper_ = SchoolScraper()
    scraper_.scrape_and_save(event_data)
