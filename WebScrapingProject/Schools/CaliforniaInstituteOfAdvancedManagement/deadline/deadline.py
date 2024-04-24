from bs4 import BeautifulSoup
from Schools.utils import remove_duplicate_terms, extract_content


def CaliforniaInstituteOfAdvancedManagement_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "Application Deadlines",
                        'Application FAQs')

    x = remove_duplicate_terms(x)

    return x


