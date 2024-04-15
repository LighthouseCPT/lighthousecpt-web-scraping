from bs4 import BeautifulSoup
from ...utils import *
import pandas as pd


def TrineUniversity_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    tbl = soup.table
    df = pd.read_html(StringIO(str(tbl)))[0]
    return df
