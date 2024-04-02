from .Tuition.Tuition import TuitionScraper
from .Requirement.Requirement import RequirementScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class TrineUniversityScraper:
    def __init__(self, HTML_BUCKET, CSV_BUCKET, school_name='TrineUniversity'):
        self.tuition_scraper = TuitionScraper(HTML_BUCKET, CSV_BUCKET, school_name)
        self.requirement_scraper = RequirementScraper(HTML_BUCKET, CSV_BUCKET, school_name)

    def scrape(self, info):
        print(info)
        tuition_url = info.get("tuition")
        requirement_url = info.get("requirement")
        if tuition_url:
            self.tuition_scraper.scrape(tuition_url)
        if requirement_url:
            self.requirement_scraper.scrape(requirement_url)
