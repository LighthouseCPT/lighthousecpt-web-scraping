from .Requirement.Requirement import RequirementScraper
from .Deadline.Deadline import DeadlineScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class NewEnglandCollegeScraper:
    def __init__(self, SOURCE_BUCKET, CSV_BUCKET, school_name='NewEnglandCollege'):
        self.requirement_scraper = RequirementScraper(SOURCE_BUCKET, CSV_BUCKET, school_name)
        self.deadline_scraper = DeadlineScraper(SOURCE_BUCKET, CSV_BUCKET, school_name)

    def scrape(self, info):
        print(info)
        requirement_url = info.get("requirement")
        deadline_url = info.get("deadline")
        if requirement_url:
            self.requirement_scraper.scrape(requirement_url)
        if deadline_url:
            self.deadline_scraper.scrape(deadline_url)
