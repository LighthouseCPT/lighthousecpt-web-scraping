import io
import os
from typing import Literal
from .utils import make_request, get_latest_item
from datetime import datetime
import pandas as pd
import boto3
from WebScrapingProject.log_config import configure_logger

logging = configure_logger(__name__)


class BaseScraper:
    def __init__(self, REGION, SOURCE_BUCKET, CSV_BUCKET, SCHOOL_NAME, TYPE):
        self.REGION = REGION
        self.TYPE = TYPE
        self.SOURCE_BUCKET = SOURCE_BUCKET
        self.CSV_BUCKET = CSV_BUCKET
        self.SCHOOL_NAME = SCHOOL_NAME
        self.SCHOOL_NAME_AND_TYPE = f'{self.SCHOOL_NAME}_{self.TYPE}'
        self.BASE_PATH = f'{self.SCHOOL_NAME}/{self.SCHOOL_NAME_AND_TYPE}/'
        self.HTML_FILENAME = f"{self.SCHOOL_NAME_AND_TYPE}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.html"
        self.CSV_FILENAME = f"{self.SCHOOL_NAME_AND_TYPE}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        self.PDF_FILENAME = f"{self.SCHOOL_NAME_AND_TYPE}.pdf"
        self.RAW_CSV_FILENAME = f"{self.SCHOOL_NAME_AND_TYPE}.csv"
        self.S3 = boto3.client('s3')

    def scrape(self, INFO, extraction_logic):
        if INFO == 'PDF':
            old_df = self.get_latest_csv_from_s3()
            pdf = self.get_pdf_from_s3()
            if old_df is None:
                df = extraction_logic(pdf)
                self.save_csv_to_s3(df)
            else:
                new_df = extraction_logic(pdf)
                new_df.columns = old_df.columns
                new_df.index.names = old_df.index.names

                comparison_df = old_df.compare(new_df)

                if comparison_df.empty:
                    logging.info("No differences found between the old and new dataframes")

                else:
                    logging.info("Differences found between the old and new dataframes")

        elif INFO == 'RAW_CSV':
            old_df = self.get_latest_csv_from_s3()
            raw_csv = self.get_raw_csv_from_s3()
            if old_df is None:
                df = extraction_logic(raw_csv)
                self.save_csv_to_s3(df)
            else:
                new_df = extraction_logic(raw_csv).reset_index(drop=True)

                new_df.columns = old_df.columns
                new_df.index.names = old_df.index.names

                comparison_df = old_df.compare(new_df)

                if comparison_df.empty:
                    logging.info("No differences found between the old and new dataframes")

                else:
                    logging.info("Differences found between the old and new dataframes")

        else:
            old_df = self.get_latest_csv_from_s3()
            if isinstance(INFO, dict):  # For Schools with more than 2 URLS, we send the whole dict
                if old_df is None:
                    df = extraction_logic(INFO)
                    self.save_csv_to_s3(df)
                else:
                    new_df = extraction_logic(INFO).reset_index(drop=True)
                    if new_df.equals(old_df):
                        logging.info("No differences found between the old and new dataframes")

                    else:
                        logging.info("Differences found between the old and new dataframes")
                        df = extraction_logic(INFO)
                        self.save_csv_to_s3(df)
            else:
                page = make_request(INFO)
                if old_df is None:
                    self.save_html_to_s3(page)
                    source = self.get_latest_html_from_s3()
                    df = extraction_logic(source)
                    self.save_csv_to_s3(df)
                else:
                    new_df = extraction_logic(page.text).reset_index(drop=True)
                    new_df.columns = old_df.columns
                    new_df.index.names = old_df.index.names

                    comparison_df = old_df.compare(new_df)

                    if comparison_df.empty:
                        logging.info("No differences found between the old and new dataframes")
                    else:
                        logging.info("Differences found between the old and new dataframes")

                    # if new_df.equals(old_df):
                    #     print('same')
                    # else:
                    #     print('different')
                    #     # self.save_html_to_s3(page)
                    #     # source = self.get_latest_html_from_s3()
                    #     # df = extraction_logic(source)
                    #     # self.save_csv_to_s3(df)

    def save_html_to_s3(self, page):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.HTML_FILENAME}"
            self.S3.put_object(Bucket=self.SOURCE_BUCKET, Key=S3_PATH, Body=page.text.encode('utf-8'))
            logging.info(f'Successfully saved to: {S3_PATH}')
        except Exception as e:
            logging.error(f'S3 put object error: {e}')
            raise

    def save_csv_to_s3(self, df):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.CSV_FILENAME}"
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            self.S3.put_object(Bucket=self.CSV_BUCKET, Key=S3_PATH, Body=csv_buffer.getvalue())
            logging.info(f'Successfully saved to: {S3_PATH}')
        except Exception as e:
            logging.error(f'S3 put object error: {e}')
            raise

    def get_latest_html_from_s3(self):
        return self._get_latest_file_from_s3(self.SOURCE_BUCKET, 'html')

    def get_latest_csv_from_s3(self):
        return self._get_latest_file_from_s3(self.CSV_BUCKET, 'csv')

    def get_pdf_from_s3(self):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.PDF_FILENAME}"
            pdf_content = self._get_file_from_s3(self.SOURCE_BUCKET, S3_PATH)
            return io.BytesIO(pdf_content)
        except Exception as e:
            upload_url = None
            if "NoSuchKey" in str(e):
                upload_url = self._get_or_create_directory()

            error_msg = (f"A PDF file named '{self.PDF_FILENAME}' should be present at location "
                         f"'{self.SOURCE_BUCKET}/{self.BASE_PATH}'. However, this file was not found. Please "
                         f"upload here: {upload_url}.")
            logging.error(f'{str(e)} (Additional Info: {error_msg})')
            raise

    def get_raw_csv_from_s3(self):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.RAW_CSV_FILENAME}"
            csv_content = self._get_file_from_s3(self.SOURCE_BUCKET, S3_PATH)
            df = pd.read_csv(io.StringIO(csv_content.decode()))
            return df
        except Exception as e:
            upload_url = None
            if "NoSuchKey" in str(e):
                upload_url = self._get_or_create_directory()

            error_msg = (f"A CSV file named '{self.RAW_CSV_FILENAME}' should be present at location "
                         f"'{self.SOURCE_BUCKET}/{self.BASE_PATH}'. However, this file was not found. Please "
                         f"upload here: {upload_url}.")
            logging.error(f'{str(e)} (Additional Info: {error_msg})')
            raise

    def _get_latest_file_from_s3(self, bucket: str, extension: Literal['html', 'csv']):
        allowed_extensions = {'html', 'csv'}
        if extension not in allowed_extensions:
            raise ValueError(
                f'Invalid file extension: [{extension}]. Allowed extensions are [{", ".join(allowed_extensions)}]')
        items = [
            os.path.basename(obj.key) for obj in boto3.resource('s3').Bucket(bucket).objects.filter(
                Prefix=self.BASE_PATH) if obj.key.endswith(f".{extension}")
        ]
        if items:
            logging.debug(f'Bucket: "{bucket}" Path: "{self.BASE_PATH}" - Contains the following items: {items}')
            latest_file = get_latest_item(items)
            logging.debug(f'Latest File is: {latest_file}')
            try:
                S3_PATH = f"{self.BASE_PATH}{latest_file}"
                file_content = self._get_file_from_s3(bucket, S3_PATH)  # get the content from S3
                if extension == 'csv':
                    data = io.StringIO(file_content.decode())
                    df = pd.read_csv(data)
                    return df
                if extension == 'html':
                    return file_content
            except Exception as e:
                logging.error(f'S3 get object error: {str(e)}')
                raise
        else:
            logging.debug(f'Bucket: "{bucket}" Path: "{self.BASE_PATH}" - Contains NO items')
            return None

    def _get_file_from_s3(self, bucket: str, path: str) -> bytes:
        try:
            obj = self.S3.get_object(Bucket=bucket, Key=path)
            file_content = obj['Body'].read()
            logging.debug(f'Successfully read from: {path}')
            return file_content
        except Exception as e:
            logging.error(f'S3 get object error: {str(e)}')
            raise

    def _get_or_create_directory(self):

        # Creating the full path for the 'do_not_remove.txt' file
        dummy_path = f"{self.BASE_PATH}do_not_remove.txt"

        # Check if the 'do_not_remove.txt' file already exists
        try:
            self.S3.head_object(Bucket=self.SOURCE_BUCKET, Key=dummy_path)
        except Exception as e:
            # If the 'do_not_remove.txt' file does not exist create it
            if "Not Found" in str(e):
                self.S3.put_object(Bucket=self.SOURCE_BUCKET, Key=dummy_path, Body='')

        # Generate bucket URL
        base_url = f"https://{self.REGION}.console.aws.amazon.com/s3/buckets/"
        bucket_url = f"{base_url}{self.SOURCE_BUCKET}?region={self.REGION}&bucketType=general&prefix={self.BASE_PATH}"

        return bucket_url


