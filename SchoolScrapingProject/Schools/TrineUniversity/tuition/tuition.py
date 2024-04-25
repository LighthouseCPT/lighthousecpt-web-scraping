from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def TrineUniversity_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    x = extract_content(soup, 'International Tuition and Fees - Graduate Degrees', 'Take the Next Steps')
    y = extract_inner_string(x, "Students are responsible", "visa denial.", include_end=True)
    return y
