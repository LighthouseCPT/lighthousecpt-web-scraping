from bs4 import BeautifulSoup
from Schools.utils import extract_content


def McDanielCollege_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    x = extract_content(soup, 'Graduate Tuition & Fees', 'Connect With Us')
    return x
