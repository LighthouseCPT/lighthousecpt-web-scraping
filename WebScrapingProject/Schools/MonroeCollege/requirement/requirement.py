import re
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def MonroeCollege_requirement(source):
    soup = BeautifulSoup(source, 'html.parser')
    pattern = re.compile(r'Graduate Admissions for Master’s Degrees')
    data = soup.find(string=pattern).find_next('ul').get_text(separator='\n', strip=True)
    df = pd.DataFrame([data])
    return df
