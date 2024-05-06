import os
from Schools.ai_prompts import extract_deadline_to_csv, extract_tuition_to_csv, extract_requirement_to_csv
from pypdf import PdfReader
from Schools.ai_utils import gen_and_get_best_csv
from Schools.base_scraper2 import BaseScraper2
from pdftables import PDFTables
from log_config import configure_logger

logger = configure_logger(__name__)


class BaseScraper(BaseScraper2):
    def __init__(self, REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME, TYPE, INFO, PROGRAMS,
                 EXTRACTING_LOGIC):
        super().__init__(REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME, TYPE)

        self.TYPE = TYPE
        self.INFO = INFO
        self.PROGRAMS = ', '.join(PROGRAMS)
        self.EXTRACTING_LOGIC = EXTRACTING_LOGIC
        self.prompt_mapping = {
            'deadline': extract_deadline_to_csv,
            'tuition': extract_tuition_to_csv,
            'requirement': extract_requirement_to_csv
        }
        self.prompt = self.prompt_mapping.get(self.TYPE)

    def scrape(self):

        if self.INFO == 'PDF_TXT':
            try:
                pdf = self.get_pdf_from_s3()
                reader = PdfReader(pdf)
                number_of_pages = len(reader.pages)
                all_text = ""
                for i in range(number_of_pages):
                    page = reader.pages[i]
                    all_text += page.extract_text() + "\n"
                self.save_raw_txt_to_s3(all_text)
                self.delete_pdf_from_s3()
                cleaned_text, add_ins = self._unpack_text(lambda: self.EXTRACTING_LOGIC(all_text))
                self._gen_and_save_csv(cleaned_text, add_ins)
                return ("Scraped and saved raw data, then generated and saved CSV to S3. "
                        f"{self._gen_bucket_url(self.CSV_BUCKET)}")
            except FileNotFoundError as e:
                msg = (f'As PDF_TXT was chosen, a PDF file was anticipated for extraction and storage '
                       f'to a RAW TXT file. To generate and save a new CSV from a previously extracted PDF, '
                       f'please choose RAW_TXT')
                return self.log_warn(e, msg)

        elif self.INFO == 'RAW_TXT':
            try:
                raw_text_string = self.get_latest_raw_text_from_s3()
                cleaned_text, add_ins = self._unpack_text(lambda: self.EXTRACTING_LOGIC(raw_text_string))
                self._gen_and_save_csv(cleaned_text, add_ins)
                return ("Scraped and saved raw data, then generated and saved CSV to S3. "
                        f"{self._gen_bucket_url(self.CSV_BUCKET)}")
            except FileNotFoundError as e:
                msg = f'As RAW_TXT was chosen, a TXT file was anticipated to generate and save a new CSV'
                return self.log_warn(e, msg)

        elif self.INFO == 'PDF_CSV':
            try:
                pdf = self.get_pdf_from_s3()
                csv = PDFTables(os.getenv('PDFTABLES_API_KEY')).csv(pdf)
                self.save_raw_csv_to_s3(csv)
                self.delete_pdf_from_s3()
                csv, add_ins = self._unpack_text(lambda: self.EXTRACTING_LOGIC(csv))
                readable_csv_string = self.make_csv_readable(csv)
                self._gen_and_save_csv(readable_csv_string, add_ins)
                return ("Scraped and saved raw data, then generated and saved CSV to S3. "
                        f"{self._gen_bucket_url(self.CSV_BUCKET)}")
            except FileNotFoundError as e:
                msg = ('As PDF_CSV was chosen, a PDF file was anticipated for extraction and storage '
                       'to a RAW CSV file. To generate and save a new CSV from a previously extracted PDF, '
                       'please choose RAW_CSV')
                return self.log_warn(e, msg)

        elif self.INFO == 'RAW_CSV':
            try:
                csv_from_s3 = self.get_latest_raw_csv_from_s3()
                csv, add_ins = self._unpack_text(lambda: self.EXTRACTING_LOGIC(csv_from_s3))
                readable_csv_string = self.make_csv_readable(csv)
                self._gen_and_save_csv(readable_csv_string, add_ins)
                return ("Scraped and saved raw data, then generated and saved CSV to S3. "
                        f"{self._gen_bucket_url(self.CSV_BUCKET)}")
            except FileNotFoundError as e:
                msg = 'As RAW_CSV was chosen, a CSV file was anticipated to generate and save a new CSV.'
                return self.log_warn(e, msg)

        else:  # URLs
            return self.process_urls()

    def process_urls(self):
        try:
            scraped_text_from_s3 = self.get_latest_raw_text_from_s3()
            fresh_scraped_text, add_ins = self._unpack_text(self._extract_scraped_text)
            return self._handle_existing_scrape(scraped_text_from_s3, fresh_scraped_text, add_ins)
        except FileNotFoundError:
            fresh_scraped_text, add_ins = self._unpack_text(self._extract_scraped_text)
            self.save_raw_txt_to_s3(fresh_scraped_text)
            self._gen_and_save_csv(fresh_scraped_text, add_ins)
            return self.log_info(
                f"Scraped and saved raw data, then generated and saved CSV to S3. "
                f"{self._gen_bucket_url(self.CSV_BUCKET)}"
            )

    def _handle_existing_scrape(self, scraped_text, fresh_scraped_text, add_ins):
        if scraped_text == fresh_scraped_text:
            return self.log_info(
                f"Newly scraped data matches existing data in S3 bucket, no updates necessary. "
                f"{self._gen_bucket_url(self.CSV_BUCKET)}"
            )

        else:
            self.save_raw_txt_to_s3(fresh_scraped_text)
            self._gen_and_save_csv(fresh_scraped_text, add_ins)
            return self.log_info(
                f"Newly scraped data DID NOT match existing data in S3 bucket, updated new CSV. "
                f"{self._gen_bucket_url(self.CSV_BUCKET)}"
            )

    def _extract_scraped_text(self):
        if isinstance(self.INFO, dict):
            return self.EXTRACTING_LOGIC(self.INFO)
        else:
            source = self.make_request(self.INFO)
            return self.EXTRACTING_LOGIC(source.text)

    def _unpack_text(self, func):
        returned_value = func()
        add_ins = None
        if isinstance(returned_value, tuple) and len(returned_value) == 2:
            fresh_scraped_text, add_ins = returned_value
        else:
            fresh_scraped_text = returned_value
        return fresh_scraped_text, add_ins

    def _gen_and_save_csv(self, text, add_ins):
        df1, df2, df3 = gen_and_get_best_csv(self.prompt,
                                             text,
                                             add_ins,
                                             self.PROGRAMS,
                                             model='gpt-4-turbo',
                                             temperature=0.4)
        self.save_csv_to_s3(df1)

        if df2 is not None and df3 is not None:
            self.save_extra_csv_to_s3(df2, df3)


