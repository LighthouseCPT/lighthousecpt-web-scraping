from .Tuition.Tuition import TuitionScraper
# from .Requirement.Requirement import RequirementScraper
# from .Deadline.Deadline import DeadlineScraper
from log_config import configure_logger

logging = configure_logger(__name__)


class SofiaUniversityScraper:
    def __init__(self, SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME='SofiaUniversity'):
        self.tuition_scraper = TuitionScraper(SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME)
        # self.requirement_scraper = RequirementScraper(SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME)
        # self.deadline_scraper = DeadlineScraper(SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME)

    def scrape(self, info):
        print(info)
        tuition_url = info.get("tuition")
        requirement_url = info.get("requirement")
        deadline_url = info.get("deadline")
        if tuition_url:
            self.tuition_scraper.scrape(tuition_url)
        # if requirement_url:
        #     self.requirement_scraper.scrape(requirement_url)
        # if deadline_url:
        #     self.deadline_scraper.scrape(deadline_url)