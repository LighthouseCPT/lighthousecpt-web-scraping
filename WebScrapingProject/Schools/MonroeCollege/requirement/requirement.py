from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def MonroeCollege_requirement(source):
    soup = BeautifulSoup(source, 'html.parser')
    x = extract_content(soup, 'Apply as an International Student',
                        'Foreign Transcript Evaluation Companies')
    y1 = extract_inner_string(x, '1. Application',
                              'Early Childhood Education',
                              include_end=True)
    y2 = extract_inner_string(x, 'Graduate Admissions for Master’s Degrees:',
                              'English transcripts.', include_end=True)
    final_text = y1 + '\n\n' + y2
    return final_text
