from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def NewEnglandCollege_requirement(source):
    soup = BeautifulSoup(source, 'html.parser')
    text = soup.find('h2', string='On-Campus MS Programs').find_next('h4',
                                                                     string='Admission Requirements').find_next(
        'div').get_text(separator='\n', strip=True)
    df = pd.DataFrame([text])
    return df
