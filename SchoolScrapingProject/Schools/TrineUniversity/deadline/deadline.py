from bs4 import BeautifulSoup
from Schools.utils import extract_content


def TrineUniversity_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "TrineOnline Academic Calendar",
                        'Take the Next Steps')

    return x
