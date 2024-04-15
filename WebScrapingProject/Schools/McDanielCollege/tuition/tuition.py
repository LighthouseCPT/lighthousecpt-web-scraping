from io import StringIO
from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def McDanielCollege_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')

    degree = 'M.S. in Data Analytics'
    button = soup.find('h3', string=degree)
    div = button.find_next('div')
    p_tags = div.find_all('p')

    cols = ['Program', 'Tuition (Per Credit Hour)', 'Residency Fee', 'Practicum Fee']

    tuition_fee = p_tags[0].text
    residency_fee = p_tags[1].text.split(' - ')[-1]
    practicum_fee = p_tags[2].text.split(' - ')[-1]

    data_1 = {'Program': degree, 'Tuition (Per Credit Hour)': tuition_fee,
              'Residency Fee': residency_fee, 'Practicum Fee': practicum_fee}

    df1 = pd.DataFrame([data_1], columns=cols)

    ul = soup.find('h2', string='Graduate Program Fees').find_next('ul')
    li_tags = ul.find_all('li')

    data_2 = []
    for li in li_tags:
        item = li.get_text()
        description, cost = [x.strip() for x in item.split(':')]
        data_2.append([description, cost])

    df2 = pd.DataFrame(data_2, columns=["Description", "Cost"])

    tbl = soup.table

    df3 = pd.read_html(StringIO(str(tbl)))[0]

    merged_df = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

    return merged_df
