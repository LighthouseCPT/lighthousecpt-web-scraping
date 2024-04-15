import json
import os
from urllib.parse import urlparse
from utils import get_school_names
from log_config import configure_logger
from Schools.SchoolScraper import SchoolScraper

logging = configure_logger(__name__)


class MainSchoolScraper:

    # Specify the Region (This must be consistent with all AWS services used in this application)
    REGION = "us-east-2"

    # This bucket includes HTMLs and PDFs
    SOURCE_BUCKET = 'lighthousecpt-schools-source'

    # This bucket contains the somewhat unrefined, extracted Information in CSVs
    CSV_BUCKET = 'lighthousecpt-schools-csv'

    SCHOOLS = get_school_names('WebScrapingProject/Schools')
    # # TODO: Uncomment the above and comment the one below when in production
    # SCHOOLS = [
    #     'StFrancisCollege'
    # ]

    TYPES = ['tuition', 'requirement', 'deadline']
    ALLOWED_VALUES = ['PDF', 'RAW_CSV', 'NOT_REQUIRED']  # OR a 'URL to a webpage'

    def validate_event(self, event):
        event_school_names = [school['name'] for school in event['schools']]

        missing_schools = [school for school in self.SCHOOLS if school not in event_school_names]
        if len(missing_schools) > 0:
            logging.error(f"Missing schools in event: {missing_schools}")
            raise ValueError(f"Missing schools in event: {missing_schools}")

        for school in event['schools']:
            missing_keywords = [keyword for keyword in self.TYPES if keyword not in school]
            if len(missing_keywords) > 0:
                logging.error(f"Missing keywords {missing_keywords} for school: {school['name']}")
                raise ValueError(f"Missing keywords {missing_keywords} for school: {school['name']}")

            for keyword in self.TYPES:
                if not (school[keyword] in self.ALLOWED_VALUES or self.isValidUrl(school[keyword])):
                    error_msg = (f"Incorrect value {school[keyword]} for keyword: {keyword} of school: {school['name']}"
                                 f". Must be a 'URL to a webpage' or one of {self.ALLOWED_VALUES}")
                    logging.error(error_msg)
                    raise ValueError(error_msg)

        logging.info(f"Valid event: {json.dumps(event, indent=4)}")

    def isValidUrl(self, url):
        if isinstance(url, str):
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False
        elif isinstance(url, dict):
            return all(self.isValidUrl(value) for value in url.values())
        return False

    def scrape_and_save(self, event):

        self.validate_event(event)

        for SCHOOL_NAME_AND_INFO in event['schools']:
            SchoolScraper(
                self.REGION, self.SOURCE_BUCKET, self.CSV_BUCKET, SCHOOL_NAME_AND_INFO, self.TYPES
            )


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
