from bs4 import BeautifulSoup
from ...utils import *
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def TrineUniversity_requirement(source):  # Source will contain a dict of 2 URLs
    GRADUATE_URL = source['graduate']
    DOCTOR_URL = source['doctor']

    # Make URL Request
    GRADUATE_PAGE = make_request(GRADUATE_URL)
    DOCTOR_PAGE = make_request(DOCTOR_URL)

    columns = ['Graduate', 'Doctor']
    df = pd.DataFrame(columns=columns)

    graduate_soup = BeautifulSoup(GRADUATE_PAGE.text, 'html.parser')
    h2_tag = graduate_soup.find('h2', string="International Graduate/Master's Degree application")
    text = h2_tag.find_next_sibling("ul").find_next_sibling("ul").find('li').get_text(separator='\n', strip=True)
    df.at[0, 'Graduate'] = text

    doctor_soup = BeautifulSoup(DOCTOR_PAGE.text, 'html.parser')
    text = doctor_soup.find(string='Admission Requirements').find_next('li').get_text(separator='\n', strip=True)
    df.at[0, 'Doctor'] = text

    return df
