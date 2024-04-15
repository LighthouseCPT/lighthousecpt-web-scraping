from bs4 import BeautifulSoup
from ...utils import *
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def header_exists(table):
    thead = table.find('thead')
    return thead is not None


def TrineUniversity_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')
    tables = soup.find_all('table')

    df_list = []
    for table in tables:
        h3 = table.find_previous_sibling('h3')
        if h3 is not None:
            str_io = StringIO(str(table))
            if header_exists(table):
                temp_df = pd.read_html(str_io)[0]
            else:
                temp_df = pd.read_html(str_io, header=None)[0]
                temp_df.columns = ['Date', 'Information']

            temp_df['Term'] = h3.get_text()
            df_list.append(temp_df)

    df = pd.concat(df_list, ignore_index=True)
    return df
