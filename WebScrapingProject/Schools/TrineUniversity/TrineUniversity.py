from .Tuition.Tuition import TUITION_run
from log_config import configure_logger

logger = configure_logger(__name__)


class TrineUniversityScraper:
    def __init__(self, HTML_BUCKET, CSV_BUCKET):
        self.HTML_BUCKET = HTML_BUCKET
        self.CSV_BUCKET = CSV_BUCKET
        self.SCHOOL_NAME = 'TrineUniversity'

    def scrape(self, info):
        data = {}

        tuition_url = info.get("tuition")
        if tuition_url:
            data['tuition'] = TUITION_run(tuition_url, self.HTML_BUCKET, self.CSV_BUCKET, self.SCHOOL_NAME)

        return data

