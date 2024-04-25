from bs4 import BeautifulSoup
from Schools.utils import extract_content


def WestcliffUniversity_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "Application Deadlines",
                        'F-1 Students (Living in the US)')

    return x
