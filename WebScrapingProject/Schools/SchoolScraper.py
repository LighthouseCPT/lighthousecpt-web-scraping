import importlib
from WebScrapingProject.Schools.base_scraper import BaseScraper
from WebScrapingProject.log_config import configure_logger

logging = configure_logger(__name__)


class SchoolScraper:

    def __init__(self, REGION, SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME_AND_INFO, TYPES):

        self.TYPES = TYPES
        SCHOOL_NAME = SCHOOL_NAME_AND_INFO['name']
        self.base_path = f"Schools.{SCHOOL_NAME}"

        for TYPE in self.TYPES:
            if SCHOOL_NAME_AND_INFO.get(TYPE) != "NOT_REQUIRED":
                logging.info(f"**Started scraping for {SCHOOL_NAME} and type {TYPE}**")
                scraper = BaseScraper(REGION, SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME, TYPE)
                extraction_logic = self._get_extraction_logic(SCHOOL_NAME, TYPE)
                info = SCHOOL_NAME_AND_INFO.get(TYPE)
                scraper.scrape(info, extraction_logic)
                logging.info(f"**Completed scraping for {SCHOOL_NAME} and type {TYPE}**")

    def _get_extraction_logic(self, SCHOOL_NAME, TYPE):
        module_path = f"{self.base_path}.{TYPE}.{TYPE}"
        func_name = f"{SCHOOL_NAME}_{TYPE}"
        return getattr(importlib.import_module(module_path), func_name)
