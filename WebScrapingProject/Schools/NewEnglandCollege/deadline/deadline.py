from bs4 import BeautifulSoup
from Schools.utils import extract_content


def NewEnglandCollege_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "On Campus MS Programs",
                        'APPLY NOW')

    return x
