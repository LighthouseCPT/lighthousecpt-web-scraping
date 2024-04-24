from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def NewEnglandCollege_requirement(source):
    soup = BeautifulSoup(source, 'html.parser')
    x = extract_content(soup, 'On-Campus MS Programs',
                        'Your Future Starts at NEC')
    y = extract_inner_string(x, 'You have completed a bachelor’s degree',
                             'being denied.',
                             include_end=True)
    return y
