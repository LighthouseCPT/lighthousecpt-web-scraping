class BaseScraper:
    def __init__(self, SOURCE_BUCKET, CSV_BUCKET, school_name):
        self.SOURCE_BUCKET = SOURCE_BUCKET
        self.CSV_BUCKET = CSV_BUCKET
        self.SCHOOL_NAME = school_name

