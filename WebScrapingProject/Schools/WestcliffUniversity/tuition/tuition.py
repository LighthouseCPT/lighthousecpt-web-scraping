from io import StringIO

from bs4 import BeautifulSoup
from babel.numbers import format_currency
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def WestcliffUniversity_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    tbl = soup.table
    df = pd.read_html(StringIO(str(tbl)))[0]

    # Due to certain rows being merged across the table they appear in every row.
    # We need only the first of these sections called 'Degree Program Tuition'
    same_values_mask = df.apply(lambda row: row.nunique() == 1, axis=1)
    split_indices = same_values_mask[same_values_mask].index.tolist()

    df = df[1:split_indices[1]]
    df.columns = ['Program', 'RequiredCredits', 'Cost']
    # Extracting numeric part from 'Cost' column
    df['Cost_Numeric'] = df['Cost'].str.extract(r'(\d+)').astype(int)

    # Extracting numeric part from 'RequiredCredits' column
    df['RequiredCredits_Numeric'] = df['RequiredCredits'].str.split().str[0].astype(int)

    # Calculating total cost
    df['TotalCost'] = df['Cost_Numeric'] * df['RequiredCredits_Numeric']
    df['TotalCost'] = df['TotalCost'].apply(lambda x: format_currency(x, currency="USD", locale="en_US"))

    df.drop(['RequiredCredits_Numeric', 'Cost_Numeric'], axis=1, inplace=True)
    return df
