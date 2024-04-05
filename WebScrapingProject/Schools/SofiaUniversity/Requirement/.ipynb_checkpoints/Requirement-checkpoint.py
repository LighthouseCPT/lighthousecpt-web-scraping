from bs4 import BeautifulSoup
from ...base_scraper import BaseScraper
from ...utils import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


class RequirementScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Requirement'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'
        
        # If PDF, then get the RAW CSV
        df = None
        if url == 'PDF':
            _FILENAME = FILENAME + '_RAW'
            _S3_PATH = f'{self.SCHOOL_NAME}/{_FILENAME}'
            try:
                df = get_csv_from_s3(self.SOURCE_BUCKET, _S3_PATH)

            except ValueError as e:
                error_msg = (f"Since {url}, a RAW CSV file named '{_FILENAME}' should be present at location "
                             f"'{self.SOURCE_BUCKET}/{self.SCHOOL_NAME}'. However, this file was not found. Please "
                             f"ensure it's correctly placed.")
                logging.error(f'{str(e)} Additional Info: {error_msg}')
                raise

        df.columns=('MBA Admission Requirements', 'Required For')
        df['Required For'] = 'Everyone'
        qqq = df.loc[df['MBA Admission Requirements'] == 'F-1 Admissions Requirements'].index[0]
        df.loc[df.index>qqq, 'Required For'] = 'F-1 Admissions'
        df=df.drop(7)
        df = df.reset_index(drop=True)

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)

        upload_df_to_dynamodb(df, FILENAME)
