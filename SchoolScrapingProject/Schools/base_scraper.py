import os
from Schools.ai_prompts import extract_dates_to_csv, extract_tuition_to_csv, extract_requirement_to_csv
from pypdf import PdfReader
from Schools.ai_utils import gen_and_get_best_csv
from Schools.base_scraper2 import BaseScraper2
from pdftables import PDFTables
from log_config import configure_logger

logging = configure_logger(__name__)


class BaseScraper(BaseScraper2):
    def __init__(self, REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME, TYPE, INFO, PROGRAMS,
                 EXTRACTING_LOGIC):
        super().__init__(REGION, SOURCE_BUCKET, CSV_BUCKET, EXTRA_CSV_BUCKET, SCHOOL_NAME, TYPE)

        self.TYPE = TYPE
        self.INFO = INFO
        self.PROGRAMS = ', '.join(PROGRAMS)
        self.EXTRACTING_LOGIC = EXTRACTING_LOGIC
        self.prompt_mapping = {
            'deadline': extract_dates_to_csv,
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
                self._gen_and_save_csv(all_text)
            except FileNotFoundError as e:
                logging.warn(f'As PDF_TXT was chosen, a PDF file was anticipated for extraction and storage '
                             f'to a RAW TXT file. To generate and save a new CSV from a previously extracted PDF, '
                             f'please choose RAW_TXT. (Additional Information: {e})')

        elif self.INFO == 'RAW_TXT':
            try:
                raw_text_string = self.get_latest_raw_text_from_s3()
                cleaned_text = self.EXTRACTING_LOGIC(raw_text_string)
                self._gen_and_save_csv(cleaned_text)
            except FileNotFoundError as e:
                logging.warn(f'As RAW_TXT was chosen, a TXT file was anticipated to generate and save a new CSV.'
                             f' (Additional Information: {e})')

        elif self.INFO == 'PDF_CSV':
            try:
                pdf = self.get_pdf_from_s3()
                csv = PDFTables(os.getenv('PDFTABLES_API_KEY')).csv(pdf)
                self.save_raw_csv_to_s3(csv)
                self.delete_pdf_from_s3()
                self._gen_and_save_csv(csv)
            except FileNotFoundError as e:
                logging.warn(f'As PDF_CSV was chosen, a PDF file was anticipated for extraction and storage '
                             f'to a RAW CSV file. To generate and save a new CSV from a previously extracted PDF, '
                             f'please choose RAW_CSV. (Additional Information: {e})')

        elif self.INFO == 'PDF_CSV':

            pdf = self.get_pdf_from_s3()
            csv = PDFTables(os.getenv('PDFTABLES_API_KEY')).csv(pdf)
            self.save_raw_csv_to_s3(csv)
            self.delete_pdf_from_s3()
            raw_csv_string = self.get_latest_raw_csv_from_s3()
            readable_csv_string = self.make_csv_readable(raw_csv_string)
            df = self.EXTRACTING_LOGIC(readable_csv_string)
            self.save_csv_to_s3(df)

        elif self.INFO == 'RAW_CSV':
            raw_csv_string = self.get_latest_raw_csv_from_s3()
            readable_csv_string = self.make_csv_readable(raw_csv_string)
            self._gen_and_save_csv(readable_csv_string)

        else:  # URLs
            self.process_urls()

    def process_urls(self):
        try:
            scraped_text_from_s3 = self.get_latest_raw_text_from_s3()
            fresh_scraped_text = self._extract_scraped_text()
            self._handle_existing_scrape(scraped_text_from_s3, fresh_scraped_text)
        except FileNotFoundError:
            fresh_scraped_text = self._extract_scraped_text()
            self.save_raw_txt_to_s3(fresh_scraped_text)
            self._gen_and_save_csv(fresh_scraped_text)

    def _handle_existing_scrape(self, scraped_text, fresh_scraped_text):
        if scraped_text == fresh_scraped_text:
            logging.info("Website HAS NOT changed, skipping...")
        else:
            logging.info("Website HAS changed, continuing...")
            self.save_raw_txt_to_s3(fresh_scraped_text)
            self._gen_and_save_csv(fresh_scraped_text)

    def _request_and_extract(self):
        source = self.make_request(self.INFO)
        return self.EXTRACTING_LOGIC(source.text)

    def _gen_and_save_csv(self, text):
        df1, df2, df3 = gen_and_get_best_csv(self.prompt,
                                             text, self.PROGRAMS,
                                             model='gpt-4',
                                             temperature=0.4)
        self.save_csv_to_s3(df1)

        if df2 is not None and df3 is not None:
            self.save_extra_csv_to_s3(df2, df3)

    def _extract_scraped_text(self):
        if isinstance(self.INFO, dict):
            return self.EXTRACTING_LOGIC(self.INFO)
        else:
            return self._request_and_extract()
