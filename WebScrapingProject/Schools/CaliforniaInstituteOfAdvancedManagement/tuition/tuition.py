from bs4 import BeautifulSoup, NavigableString
import re
from io import StringIO
from Schools.ai_utils import *
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def CaliforniaInstituteOfAdvancedManagement_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    content = ''
    start = soup.find(string='Tuition & Fees')
    end = soup.find(string='Application Deadlines')
    if start and end:  # ensuring both start and end points are found
        for element in start.parent.find_all_next(string=True):  # iterate over next elements in tree
            if element == end:
                break  # stop iteration when reaching 'end' string
            if isinstance(element, NavigableString):
                content += element.strip() + '\n'  # add a newline character after each element
    content = re.sub('\n+', '\n', content)
    content = content.replace(",", "")
    output_text = get_confident_response(
        extract_tuition_to_csv(content),
        model='gpt-4-0125-preview',
        temperature=0.4,
        identical_responses_needed=2,
        max_attempts=10
    )

    output_text = output_text.lstrip("```").rstrip("```")  # This removes backticks from start and end
    output_text = output_text.strip()  # This removes leading and trailing newlines

    data = StringIO(output_text)
    df = pd.read_csv(data, sep=',')
    return df
