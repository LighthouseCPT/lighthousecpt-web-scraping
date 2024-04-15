from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def CaliforniaInstituteOfAdvancedManagement_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')
    text = soup.find(string='Application Deadlines').find_next('ul').get_text(strip=True, separator='\n')
    df = pd.DataFrame([text])
    return df

