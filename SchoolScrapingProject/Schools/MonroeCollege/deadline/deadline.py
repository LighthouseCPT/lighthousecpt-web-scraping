from bs4 import BeautifulSoup
from Schools.utils import extract_content


def MonroeCollege_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "Spring 2024 Academic Calendar",
                        'Course Catalog')

    return x
