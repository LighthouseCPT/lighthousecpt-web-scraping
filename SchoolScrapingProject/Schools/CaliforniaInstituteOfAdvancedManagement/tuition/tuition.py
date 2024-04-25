from bs4 import BeautifulSoup
from Schools.utils import extract_content


def CaliforniaInstituteOfAdvancedManagement_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')
    x = extract_content(soup, 'Tuition & Fees', 'Application Deadlines')
    return x
