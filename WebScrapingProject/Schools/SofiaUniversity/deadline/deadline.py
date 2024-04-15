from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def header_exists(table):
    thead = table.find('thead')
    return thead is not None


def SofiaUniversity_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')
    tbl = soup.table
    df = pd.read_html(StringIO(str(tbl)))[0]
    df.rename(columns={'Unnamed: 0': 'Upcoming Start Dates'}, inplace=True)
    df.dropna(how='all', inplace=True)
    return df
