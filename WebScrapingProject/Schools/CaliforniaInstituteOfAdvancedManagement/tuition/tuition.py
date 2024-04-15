from bs4 import BeautifulSoup
from io import StringIO
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def CaliforniaInstituteOfAdvancedManagement_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    tbl1 = soup.find(string='Estimated Tuition Rates 2022-2023').find_next('table')
    df1 = pd.read_html(StringIO(str(tbl1)))[0]
    tbl2 = soup.find(string='Student Fees 2022-2023').find_next('table')
    df2 = pd.read_html(StringIO(str(tbl2)))[0]
    head_str = 'Cost of Attendance'
    _ = soup.find(string=head_str).find_next('ul').get_text(strip=True, separator='\n')
    df3 = pd.DataFrame([_], columns=[head_str])
    df4 = pd.concat([df1, df2, df3])
    return df4
