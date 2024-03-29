from .Tuition.Tuition import TUITION_run
from log_config import configure_logger

logger = configure_logger(__name__)


class TrineUniversityScraper:
    def __init__(self):
        pass

    def scrape(self, info):
        data = {}

        tuition_url = info.get("tuition")
        if tuition_url:
            data['tuition'] = TUITION_run(tuition_url)

        return data

    #
    # # Save dataframe to S3
    # S3FileSystem = s3fs.S3FileSystem(anon=False)
    # with S3FileSystem.open(f's3://your-bucket-name/{TABLE}.csv', 'w') as file:
    #     df.to_csv(file)
    #
    # # can return some info if required
    # return f"Scraped and saved data for {TABLE}"
