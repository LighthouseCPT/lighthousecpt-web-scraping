from bs4 import BeautifulSoup
from ...base_scraper import BaseScraper
from ...utils import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def WestcliffUniversity_requirement(source):
    DBA_URL = source['DBA']
    EdD_URL = source['EdD']

    # Make URL Request
    DBA_PAGE = make_request(DBA_URL)
    EdD_PAGE = make_request(EdD_URL)

    DBA_soup = BeautifulSoup(DBA_PAGE.text, 'html.parser')
    EdD_soup = BeautifulSoup(EdD_PAGE.text.replace("\n", ""), 'html.parser')

    # Find the specified <a> tag based on its text
    specified_a_tag1 = DBA_soup.find('a', text=lambda
        text: text and 'admission' in text.lower() and 'requirements' in text.lower())
    DBA_areqs = specified_a_tag1.find_next_sibling('div').text.strip().replace('criteria:', 'criteria: ')

    specified_a_tag2 = DBA_soup.find('a', text=lambda
        text: text and 'graduation' in text.lower() and 'requirements' in text.lower())
    # A LOT OF TEXT ON THIS ONE:
    # DBA_greqs = ' '.join(specified_a_tag2.find_next_sibling('div').stripped_strings)
    # SHORT VERSION:
    DBA_greqs = ' '.join([tag.get_text(separator=" ").strip() for tag in
                          specified_a_tag2.find_next_sibling('div').find_all_next('p', limit=2)])

    specified_a_tag3 = EdD_soup.find('a', text=lambda
        text: text and 'admission' in text.lower() and 'requirements' in text.lower())
    EdD_areqs = specified_a_tag3.find_next_sibling('div').text.strip()

    specified_a_tag4 = EdD_soup.find('a', text=lambda
        text: text and 'graduation' in text.lower() and 'requirements' in text.lower())
    EdD_greqs = specified_a_tag4.find_next_sibling('div').text.strip()

    df = pd.DataFrame({
        'Program': ['Doctor of Business Administration (DBA)',
                    'Doctor of Education in Leadership, Curriculum, and Instruction (EdD)'],
        'Admission Requirements': [DBA_areqs, EdD_areqs],
        'Graduation Requirements': [DBA_greqs, EdD_greqs]
    })

    return df
