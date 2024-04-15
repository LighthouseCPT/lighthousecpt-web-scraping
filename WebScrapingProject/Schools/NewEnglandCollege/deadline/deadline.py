from bs4 import BeautifulSoup, NavigableString
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def NewEnglandCollege_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')
    soup.find(string='On Campus MS Programs')

    # find the p tag following the string 'On Campus MS Programs'
    p_tag = soup.find(string='On Campus MS Programs').find_next('p')

    # create an empty list to store subsequent divs
    subsequent_divs = []

    # next_siblings will return a generator which include all the siblings (not only divs)
    for elem in p_tag.next_siblings:
        if isinstance(elem, NavigableString):  # Ignore string elements
            continue
        if elem.name == 'u' and elem.get_text(strip=True) == 'APPLY NOW':
            break  # Break when find 'APPLY NOW'
        if elem.name == 'div':
            subsequent_divs.append(elem)

    data = [div.get_text(separator='\n', strip=True) for div in subsequent_divs]
    filtered_data = list(filter(None, data))
    df = pd.DataFrame([filtered_data])
    return df
