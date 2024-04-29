import importlib
from Schools.base_scraper import BaseScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class SchoolScraper:

    def __init__(self, REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME_AND_INFO, TYPES):

        self.TYPES = TYPES
        SCHOOL_NAME = SCHOOL_NAME_AND_INFO['name']
        PROGRAMS = SCHOOL_NAME_AND_INFO['programs']
        self.base_path = f"Schools.{SCHOOL_NAME}"

        for TYPE in self.TYPES:
            if SCHOOL_NAME_AND_INFO.get(TYPE) != "SKIP":
                logging.info(f"STARTED SCRAPING: [{SCHOOL_NAME}]-[{TYPE}]")
                EXTRACTING_LOGIC = self._get_extraction_logic(SCHOOL_NAME, TYPE)
                INFO = SCHOOL_NAME_AND_INFO.get(TYPE)
                scraper = BaseScraper(REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME, TYPE, INFO,
                                      PROGRAMS, EXTRACTING_LOGIC)
                scraper.scrape()
                logging.info(f"COMPLETED SCRAPING: [{SCHOOL_NAME}]-[{TYPE}]")

    def _get_extraction_logic(self, SCHOOL_NAME, TYPE):
        module_path = f"{self.base_path}.{TYPE}.{TYPE}"
        func_name = f"{SCHOOL_NAME}_{TYPE}"
        return getattr(importlib.import_module(module_path), func_name)
