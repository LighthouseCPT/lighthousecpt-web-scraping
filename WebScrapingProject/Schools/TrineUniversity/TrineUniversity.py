from .Tuition.Tuition import TuitionScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class TrineUniversityScraper:
    def __init__(self, HTML_BUCKET, CSV_BUCKET, school_name='TrineUniversity'):
        self.tuition_scraper = TuitionScraper(HTML_BUCKET, CSV_BUCKET, school_name)

    def scrape(self, info):
        print(info)
        tuition_url = info.get("tuition")
        if tuition_url:
            self.tuition_scraper.scrape(tuition_url)
