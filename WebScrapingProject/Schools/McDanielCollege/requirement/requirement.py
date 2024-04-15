import re
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def McDanielCollege_requirement(source):
    soup = BeautifulSoup(source, 'html.parser')
    pattern = re.compile(r'Admissions Requirements')
    match = soup.find(string=pattern).find_next('div').get_text(separator='\n', strip=True)
    df = pd.DataFrame([match])
    return df
