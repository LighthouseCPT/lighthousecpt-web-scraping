from pypdf import PdfReader
from ...utils import *


def CaliforniaInstituteOfAdvancedManagement_requirement(source):
    reader = PdfReader(source)
    number_of_pages = len(reader.pages)

    # Create an empty string to store all text
    all_text = ""

    # Loop through all pages and append their text to all_text
    for i in range(number_of_pages):
        page = reader.pages[i]
        all_text += page.extract_text() + "\n"  # Add a newline after each page's text

    df = pd.DataFrame([all_text])
    return df
