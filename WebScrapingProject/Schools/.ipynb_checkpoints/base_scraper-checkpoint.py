class BaseScraper:
    def __init__(self, SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME):
        self.SOURCE_BUCKET = SOURCE_BUCKET
        self.CSV_BUCKET = CSV_BUCKET
        self.SCHOOL_NAME = SCHOOL_NAME
