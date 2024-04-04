from ...base_scraper import BaseScraper
from bs4 import BeautifulSoup
from ...utils import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


class DeadlineScraper(BaseScraper):
    def scrape(self, url):
        TYPE = 'Deadline'
        FILENAME = f'{self.SCHOOL_NAME}_{TYPE}'
        S3_PATH = f'{self.SCHOOL_NAME}/{FILENAME}'

        # Make URL Request
        page = make_request(url)

        # Save HTML Content to S3
        save_html_to_s3(page, self.SOURCE_BUCKET, S3_PATH)

        # Get HTML content from S3
        html = get_html_from_s3(self.SOURCE_BUCKET, S3_PATH)

        # Start Extracting Logic
        soup = BeautifulSoup(html, 'html.parser')
        df_list = []

        h2_elements = soup.find_all('h2')

        for h2 in h2_elements:
            h2_text = h2.get_text()

            if 'Calendar' in h2_text:
                subsequent_siblings = list(h2.find_all_next())

                current_p = None
                for sibling in subsequent_siblings:
                    if sibling.name == 'h2':
                        break
                    if sibling.name == 'p' and ('Calendar' in sibling.get_text()):
                        current_p = sibling.get_text().strip()
                    if sibling.name == 'table':
                        temp_df = pd.read_html(io.StringIO(str(sibling)))[0]
                        temp_df['Term'] = h2_text
                        temp_df['Sub-Term'] = current_p
                        df_list.append(temp_df)

        df = pd.concat(df_list, ignore_index=True)
        df.rename(columns={0: "Date", 1: "Day", 2: "Information"}, inplace=True)
        df['Date'] = df[['Day', 'Date']].apply(lambda row: ', '.join(row.values), axis=1)
        df.drop('Day', axis=1, inplace=True)
        # df.reset_index(drop=True, inplace=True)
        df = df[df.columns[[2, 3, 0, 1]]]

        # Save to S3 as CSV File
        save_csv_to_s3(df, self.CSV_BUCKET, S3_PATH)

        upload_df_to_dynamodb(df, FILENAME)
