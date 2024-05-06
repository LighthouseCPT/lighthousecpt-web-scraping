import io
import csv
import os
from typing import Literal
import requests
from Schools.utils import get_latest_item
from datetime import datetime
import pandas as pd
import boto3
from log_config import configure_logger

logger = configure_logger(__name__)


class BaseScraper2:
    def __init__(self, REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME, TYPE):
        self.REGION = REGION
        self.TYPE = TYPE
        self.SOURCE_BUCKET = SOURCE_BUCKET
        self.CSV_BUCKET = CSV_BUCKET
        self.EXTRA_CSV_BUCKET = EXTRA_CSV_BUCKET
        self.SCHOOL_NAME = SCHOOL_NAME
        self.SCHOOL_NAME_TYPE = f'{self.SCHOOL_NAME}_{self.TYPE}'
        self.SCHOOL_NAME_TYPE_DATE = f"{self.SCHOOL_NAME_TYPE}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        self.BASE_PATH = f'{self.SCHOOL_NAME}/{self.SCHOOL_NAME_TYPE}/'
        self.EXTRA_BASE_PATH = f'{self.SCHOOL_NAME}/{self.SCHOOL_NAME_TYPE}/{self.SCHOOL_NAME_TYPE_DATE}/'
        self.HTML_FILENAME = self.SCHOOL_NAME_TYPE_DATE + '.html'
        self.CSV_FILENAME = self.SCHOOL_NAME_TYPE_DATE + '.csv'
        self.TXT_FILENAME = self.SCHOOL_NAME_TYPE_DATE + '.txt'
        self.PDF_FILENAME = f"{self.SCHOOL_NAME_TYPE}.pdf"
        self.S3 = boto3.client('s3')

    def save_html_to_s3(self, page):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.HTML_FILENAME}"
            self.S3.put_object(Bucket=self.SOURCE_BUCKET, Key=S3_PATH, Body=page.text.encode('utf-8'))
            logger.info(f'Successfully saved to: {S3_PATH}')
        except Exception as e:
            logger.error(f'S3 put object error: {e}')
            raise

    def save_csv_to_s3(self, df):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.CSV_FILENAME}"
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            self.S3.put_object(Bucket=self.CSV_BUCKET, Key=S3_PATH, Body=csv_buffer.getvalue())
            s3_console_url = (f"https://{self.REGION}.console.aws.amazon.com/s3/buckets/{self.CSV_BUCKET}?"
                              f"region={self.REGION}&bucketType=general&prefix={S3_PATH}")
            logger.info(f'Successfully saved to: {S3_PATH}. URL: {s3_console_url}')
        except Exception as e:
            logger.error(f'S3 put object error: {e}')
            raise

    def save_extra_csv_to_s3(self, *dfs):
        try:
            for i, df in enumerate(dfs, 1):
                S3_PATH = f"{self.EXTRA_BASE_PATH}{self.CSV_FILENAME.split('.csv')[0]}_{i}.csv"  # append the suffix
                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                self.S3.put_object(Bucket=self.EXTRA_CSV_BUCKET, Key=S3_PATH, Body=csv_buffer.getvalue())
                s3_console_url = (f"https://{self.REGION}.console.aws.amazon.com/s3/buckets/{self.EXTRA_CSV_BUCKET}?"
                                  f"region={self.REGION}&bucketType=general&prefix={S3_PATH}")
                logger.info(f'Successfully saved to: {S3_PATH}. URL: {s3_console_url}')
        except Exception as e:
            logger.error(f'S3 put object error: {e}')
            raise

    def save_raw_txt_to_s3(self, txt):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.TXT_FILENAME}"
            txt_buffer = io.StringIO(txt)
            txt_buffer.seek(0)
            self.S3.put_object(Bucket=self.SOURCE_BUCKET, Key=S3_PATH, Body=txt_buffer.getvalue())
            logger.info(f'Successfully saved to: {S3_PATH}')
        except Exception as e:
            logger.error(f'S3 put object error: {e}')
            raise

    def save_raw_csv_to_s3(self, csv_bytes):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.CSV_FILENAME}"
            self.S3.put_object(Bucket=self.SOURCE_BUCKET, Key=S3_PATH, Body=csv_bytes)
            logger.info(f'Successfully saved to: {S3_PATH}')
        except Exception as e:
            logger.error(f'S3 put object error: {e}')
            raise

    def get_latest_csv_from_s3(self):
        return self._get_latest_file_from_s3(self.CSV_BUCKET, 'csv')

    def get_latest_raw_csv_from_s3(self):
        df = self._get_latest_file_from_s3(self.SOURCE_BUCKET, 'csv')
        csv_string = df.to_csv(index=False)
        return csv_string

    def get_latest_raw_text_from_s3(self):
        return self._get_latest_file_from_s3(self.SOURCE_BUCKET, 'txt')

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
            raise FileNotFoundError(error_msg)

    def delete_pdf_from_s3(self):
        try:
            S3_PATH = f"{self.BASE_PATH}{self.PDF_FILENAME}"
            self.S3.delete_object(Bucket=self.SOURCE_BUCKET, Key=S3_PATH)
            logger.info(f'Successfully deleted the file: {self.PDF_FILENAME}')
        except Exception as e:
            logger.error(f'Error deleting the file: {str(e)}')
            raise

    def _get_latest_file_from_s3(self, bucket: str, extension: Literal['csv', 'txt']):
        allowed_extensions = {'csv', 'txt'}
        if extension not in allowed_extensions:
            raise ValueError(
                f'Invalid file extension: [{extension}]. Allowed extensions are [{", ".join(allowed_extensions)}]')
        items = [
            os.path.basename(obj.key) for obj in boto3.resource('s3').Bucket(bucket).objects.filter(
                Prefix=self.BASE_PATH) if obj.key.endswith(f".{extension}")
        ]
        if items:
            logger.debug(f'Bucket: "{bucket}" Path: "{self.BASE_PATH}" - Contains the following items: {items}'
                          f'{self._gen_bucket_url(bucket)}')
            latest_file = get_latest_item(items)
            logger.debug(f'Latest File is: {latest_file}')
            try:
                S3_PATH = f"{self.BASE_PATH}{latest_file}"
                file_content = self._get_file_from_s3(bucket, S3_PATH)  # get the content from S3
                if extension == 'csv':
                    data = io.StringIO(file_content.decode())
                    df = pd.read_csv(data)
                    return df
                elif extension == 'txt':
                    return file_content.decode()
            except Exception as e:
                logger.error(f'S3 get object error: {str(e)}')
                raise
        else:
            upload_url = self._get_or_create_directory()
            error_msg = (f"A file with '{extension}' extension should be present at location "
                         f"'{bucket}/{self.BASE_PATH}'. However, no files were found. Please "
                         f"upload here: {upload_url}.")
            raise FileNotFoundError(error_msg)

    def _get_file_from_s3(self, bucket: str, path: str) -> bytes:
        try:
            obj = self.S3.get_object(Bucket=bucket, Key=path)
            file_content = obj['Body'].read()
            logger.debug(f'Successfully read from: {path}')
            return file_content
        except Exception as e:
            logger.error(f'S3 get object error: {str(e)}')
            raise

    def _get_or_create_directory(self):

        # Creating the full path for the 'do_not_remove' file
        dummy_path = f"{self.BASE_PATH}do_not_remove"

        # Check if the 'do_not_remove' file already exists
        try:
            self.S3.head_object(Bucket=self.SOURCE_BUCKET, Key=dummy_path)
        except Exception as e:
            # If the 'do_not_remove' file does not exist create it
            if "Not Found" in str(e):
                self.S3.put_object(Bucket=self.SOURCE_BUCKET, Key=dummy_path, Body='')

        # Generate bucket URL
        return self._gen_bucket_url(self.SOURCE_BUCKET)

    def _gen_bucket_url(self, bucket):
        base_url = f"https://{self.REGION}.console.aws.amazon.com/s3/buckets/"
        bucket_url = f"{base_url}{bucket}?region={self.REGION}&bucketType=general&prefix={self.BASE_PATH}"
        return bucket_url

    @staticmethod
    def make_request(url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, '
                                     'like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            page = requests.get(url, headers=headers)
            logger.debug(f'Successfully made request to: {url}')
            return page
        except requests.RequestException as e:
            logger.error(f'Request error: {e}')
            raise

    @staticmethod
    def make_csv_readable(csv_string):
        temp = []
        reader = csv.reader(io.StringIO(csv_string))

        for row in reader:
            temp.append('|'.join(row))

        pipe_delimited_text = '\n'.join(temp)
        return pipe_delimited_text

    @staticmethod
    def log_warn(warning, message):
        msg = f"{message} (Additional Information: {warning})"
        logger.warn(msg)
        return msg

    @staticmethod
    def log_info(message):
        msg = f"{message}"
        logger.info(msg)
        return msg

