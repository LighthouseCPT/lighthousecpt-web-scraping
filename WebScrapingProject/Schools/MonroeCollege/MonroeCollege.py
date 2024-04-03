from .Tuition.Tuition import TuitionScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class MonroeCollegeScraper:
    def __init__(self, SOURCE_BUCKET, CSV_BUCKET, school_name='MonroeCollege'):
        self.tuition_scraper = TuitionScraper(SOURCE_BUCKET, CSV_BUCKET, school_name)

    def scrape(self, info):
        print(info)
        tuition_url = info.get("tuition")
        requirement_url = info.get("requirement")
        deadline_url = info.get("deadline")
        if tuition_url:
            self.tuition_scraper.scrape(tuition_url)
