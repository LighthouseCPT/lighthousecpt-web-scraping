import re
from io import StringIO

from pypdf import PdfReader
from WebScrapingProject.ai_utils import *
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def StFrancisCollege_deadline(source):
    reader = PdfReader(source)
    number_of_pages = len(reader.pages)
    all_text = ""

    for i in range(number_of_pages):  # Start from index 0, which is the first page
        page = reader.pages[i]
        all_text += page.extract_text() + "\n"

    lines = all_text.split('\n')
    new_lines = [re.sub('\.{3,}', '=', line) for line in lines]
    new_lines = [re.sub(r'(\d+)\s+(\d+)', r'\1\2', line) for line in new_lines]

    output_text = get_confident_response(
        extract_dates_to_csv(new_lines),
        model='gpt-4-0125-preview',
        temperature=0.2,
        identical_responses_needed=2
    )

    output_text = output_text.lstrip("```").rstrip("```")  # This removes backticks from start and end
    output_text = output_text.strip()  # This removes leading and trailing newlines
    data = StringIO(output_text)
    df = pd.read_csv(data, sep=",")
    return df
