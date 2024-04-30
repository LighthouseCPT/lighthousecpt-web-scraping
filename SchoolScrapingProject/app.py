import importlib
import json
import os
from urllib.parse import urlparse
import boto3
from Schools.base_scraper import BaseScraper
from Schools.utils import get_school_names, check_api_key, download_s3_bucket_contents
from log_config import configure_logger

logger = configure_logger(__name__)


class App:
    TYPES = ['tuition', 'requirement', 'deadline']
    ALLOWED_VALUES = ['PDF_TXT', 'PDF_CSV', 'RAW_TXT', 'RAW_CSV', 'SKIP']  # OR a 'URL to a webpage'

    def __init__(self, event):
        self.event = event
        self.region = event['config']['region']
        self.source_bucket = event['config']['source_bucket']
        self.csv_bucket = event['config']['csv_bucket']
        self.extra_csv_bucket = event['config']['extra_csv_bucket']
        self.mode = event['config']['mode']
        self.event_schools = [school['name'] for school in event['schools']]
        os.environ['OPENAI_API_KEY'] = check_api_key(self.get_parameter(event['config']['openai_api_key']))
        os.environ['PDFTABLES_API_KEY'] = self.get_parameter(event['config']['pdftables_api_key'])
        try:
            self.dir_schools = get_school_names('Schools')
        except FileNotFoundError:
            self.dir_schools = get_school_names('SchoolScrapingProject/Schools')

    def scrape_and_save(self):

        self._validate_event()

        if self.mode == 'all':
            return self._all_mode()
        else:
            return self._specified_mode()

    def _all_mode(self):
        if set(self.event_schools) == set(self.dir_schools):
            return self._initiate_school_scraping()
        else:
            self._missing_schools()

    def _specified_mode(self):
        specified_schools = [school.strip() for school in self.mode.split(',')]
        if (set(specified_schools).issubset(set(self.event_schools)) and
                set(specified_schools).issubset(set(self.dir_schools))):
            return self._initiate_school_scraping(specified_schools)
        else:
            error_msg = (f"Schools specified in mode here: {specified_schools} are not valid. "
                         f"Must be 'all' or one or multiple of: {self.dir_schools}")
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _validate_event(self):

        for school in self.event['schools']:
            school_name = school['name']
            missing_keywords = [keyword for keyword in self.TYPES if keyword not in school]

            if len(missing_keywords) > 0:
                missing_keywords_error = f"Missing keywords {missing_keywords} for school: {school_name}"
                logger.error(missing_keywords_error)
                raise ValueError(missing_keywords_error)

            for keyword in self.TYPES:
                if not (school[keyword] in self.ALLOWED_VALUES or self._isValidUrl(school[keyword])):
                    invalid_value_error = (
                        f"Incorrect value {school[keyword]} for keyword: {keyword} of school: {school_name}."
                        f" Must be a 'URL to a webpage' or one of {self.ALLOWED_VALUES}"
                    )
                    logger.error(invalid_value_error)
                    raise ValueError(invalid_value_error)

        logger.debug(f"Valid event: {json.dumps(self.event, indent=4)}")

    def _missing_schools(self):
        logger.debug(f"Directory Schools: {self.dir_schools}")
        logger.debug(f"Event Schools: {self.event_schools}")
        missing_in_event = [school for school in self.dir_schools if school not in self.event_schools]
        missing_in_directory = [school for school in self.event_schools if school not in self.dir_schools]

        if len(missing_in_event) > 0:
            logger.error(f"Missing schools in event: {missing_in_event}")
            raise ValueError(f"Missing schools in event: {missing_in_event}")
        if len(missing_in_directory) > 0:
            logger.error(f"Extra schools in event not in directory: {missing_in_directory}")
            raise ValueError(f"Extra schools in event not in directory: {missing_in_directory}")

    def _initiate_school_scraping(self, schools=None):
        for SCHOOL_NAME_AND_INFO in self.event['schools']:
            if schools and SCHOOL_NAME_AND_INFO['name'] not in schools:
                continue

            SCHOOL_NAME = SCHOOL_NAME_AND_INFO['name']
            PROGRAMS = SCHOOL_NAME_AND_INFO['programs']
            base_path = f"Schools.{SCHOOL_NAME}"

            for TYPE in self.TYPES:
                if SCHOOL_NAME_AND_INFO.get(TYPE) != "SKIP":
                    logger.info(f"STARTED SCRAPING: [{SCHOOL_NAME}]-[{TYPE}]")
                    module_path = f"{base_path}.{TYPE}.{TYPE}"
                    func_name = f"{SCHOOL_NAME}_{TYPE}"
                    EXTRACTING_LOGIC = getattr(importlib.import_module(module_path), func_name)
                    INFO = SCHOOL_NAME_AND_INFO.get(TYPE)
                    scraper = BaseScraper(self.region, self.source_bucket, self.csv_bucket, self.extra_csv_bucket,
                                          SCHOOL_NAME,
                                          TYPE, INFO, PROGRAMS, EXTRACTING_LOGIC)
                    returned_msg = scraper.scrape()
                    logger.info(f"ENDED SCRAPING: [{SCHOOL_NAME}]-[{TYPE}]")
                    final_returned_msg = f'[{SCHOOL_NAME}]-[{TYPE}] == {returned_msg}'
                    return final_returned_msg

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

    def get_parameter(self, parameter_name):
        ssm_client = boto3.client('ssm', region_name=self.region)
        param_value = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return param_value['Parameter']['Value']


def lambda_handler(event, context):
    scraper = App(event)
    return scraper.scrape_and_save()


# The following is solely for local testing; AWS Lambda will NOT execute it.
# AWS Lambda will only execute the "lambda_handler" function above.
if __name__ == "__main__":
    # download_s3_bucket_contents('lighthousecpt-schools-csv')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    event_path = os.path.join(script_dir, 'events/event.json')
    with open(event_path, 'r') as file:
        event_data = json.load(file)
    lambda_handler(event_data, None)
