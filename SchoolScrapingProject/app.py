import json
import os
from urllib.parse import urlparse

import boto3

from Schools.utils import get_school_names
from log_config import configure_logger
from Schools.SchoolScraper import SchoolScraper

logging = configure_logger(__name__)


def download_s3_bucket_contents(bucket_name, local_directory=None):
    s3 = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    if not local_directory:
        local_directory = os.getcwd() + '/s3_download'  # Set to a subfolder in the current directory
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)  # Make sure the directory exists

    for obj in s3_resource.Bucket(bucket_name).objects.all():
        local_file_path = os.path.join(local_directory, obj.key)
        if not os.path.exists(os.path.dirname(local_file_path)):
            os.makedirs(os.path.dirname(local_file_path))
        s3.download_file(bucket_name, obj.key, local_file_path)


class MainSchoolScraper:
    TYPES = ['tuition', 'requirement', 'deadline']
    ALLOWED_VALUES = ['PDF_TXT', 'PDF_CSV', 'RAW_TXT', 'RAW_CSV', 'SKIP']  # OR a 'URL to a webpage'

    def __init__(self, event):
        self.event = event
        self.region = event['config']['region']
        self.source_bucket = event['config']['source_bucket']
        self.csv_bucket = event['config']['csv_bucket']
        self.mode = event['config']['mode']
        self.event_schools = [school['name'] for school in event['schools']]
        try:
            self.dir_schools = get_school_names('Schools')
        except FileNotFoundError:
            self.dir_schools = get_school_names('SchoolScrapingProject/Schools')

    def scrape_and_save(self):

        self._validate_event()

        if self.mode == 'all':
            self._all_mode()
        else:
            self._specified_mode()

    def _all_mode(self):
        if set(self.event_schools) == set(self.dir_schools):
            self._initiate_school_scraping()
        else:
            self._missing_schools()

    def _specified_mode(self):
        specified_schools = [school.strip() for school in self.mode.split(',')]
        if (set(specified_schools).issubset(set(self.event_schools)) and
                set(specified_schools).issubset(set(self.dir_schools))):
            self._initiate_school_scraping(specified_schools)
        else:
            error_msg = (f"Schools specified in mode here: {specified_schools} are not valid. "
                         f"Must be 'all' or one or multiple of: {self.dir_schools}")
            logging.error(error_msg)
            raise ValueError(error_msg)

    def _validate_event(self):

        for school in self.event['schools']:
            school_name = school['name']
            missing_keywords = [keyword for keyword in self.TYPES if keyword not in school]

            if len(missing_keywords) > 0:
                missing_keywords_error = f"Missing keywords {missing_keywords} for school: {school_name}"
                logging.error(missing_keywords_error)
                raise ValueError(missing_keywords_error)

            for keyword in self.TYPES:
                if not (school[keyword] in self.ALLOWED_VALUES or self._isValidUrl(school[keyword])):
                    invalid_value_error = (
                        f"Incorrect value {school[keyword]} for keyword: {keyword} of school: {school_name}."
                        f" Must be a 'URL to a webpage' or one of {self.ALLOWED_VALUES}"
                    )
                    logging.error(invalid_value_error)
                    raise ValueError(invalid_value_error)

        logging.debug(f"Valid event: {json.dumps(self.event, indent=4)}")

    def _missing_schools(self):
        logging.debug(f"Directory Schools: {self.dir_schools}")
        logging.debug(f"Event Schools: {self.event_schools}")
        missing_in_event = [school for school in self.dir_schools if school not in self.event_schools]
        missing_in_directory = [school for school in self.event_schools if school not in self.dir_schools]

        if len(missing_in_event) > 0:
            logging.error(f"Missing schools in event: {missing_in_event}")
            raise ValueError(f"Missing schools in event: {missing_in_event}")
        if len(missing_in_directory) > 0:
            logging.error(f"Extra schools in event not in directory: {missing_in_directory}")
            raise ValueError(f"Extra schools in event not in directory: {missing_in_directory}")

    def _initiate_school_scraping(self, schools=None):
        if schools:
            for SCHOOL_NAME_AND_INFO in self.event['schools']:
                if SCHOOL_NAME_AND_INFO['name'] in schools:
                    SchoolScraper(
                        self.region,
                        self.source_bucket,
                        self.csv_bucket,
                        SCHOOL_NAME_AND_INFO,
                        self.TYPES
                    )

        else:
            for SCHOOL_NAME_AND_INFO in self.event['schools']:
                SchoolScraper(
                    self.region,
                    self.source_bucket,
                    self.csv_bucket,
                    SCHOOL_NAME_AND_INFO,
                    self.TYPES
                )

    def _isValidUrl(self, url):
        if isinstance(url, str):
            try:
                result = urlparse(url)
                return all([result.scheme, result.netloc])
            except ValueError:
                return False
        elif isinstance(url, dict):
            return all(self._isValidUrl(value) for value in url.values())
        return False


def lambda_handler(event, context):
    scraper = MainSchoolScraper(event)
    scraper.scrape_and_save()


# The following is solely for local testing; AWS Lambda will NOT execute it.
# AWS Lambda will execute the "lambda_handler" function above.
if __name__ == "__main__":
    # download_s3_bucket_contents('lighthousecpt-schools-csv')
    parent_directory = os.path.dirname(os.getcwd())
    event_path = os.path.join('events', 'event.json')
    with open(event_path, 'r') as file:
        event_data = json.load(file)
    scraper_ = MainSchoolScraper(event_data)
    scraper_.scrape_and_save()