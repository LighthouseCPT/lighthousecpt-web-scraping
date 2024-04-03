class BaseScraper:
    def __init__(self, HTML_BUCKET, CSV_BUCKET, school_name):
        self.HTML_BUCKET = HTML_BUCKET
        self.CSV_BUCKET = CSV_BUCKET
        self.SCHOOL_NAME = school_name
