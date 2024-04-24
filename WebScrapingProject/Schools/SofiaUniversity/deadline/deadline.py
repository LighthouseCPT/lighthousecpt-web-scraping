from bs4 import BeautifulSoup
from Schools.utils import extract_content


def SofiaUniversity_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "Upcoming Start Dates:",
                        'Speak with an Admissions Counselor today to apply.')

    return x
