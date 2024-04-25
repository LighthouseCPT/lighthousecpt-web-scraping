import requests
from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def WestcliffUniversity_requirement(source):
    url1 = source['DBA']
    page1 = requests.get(url1)
    soup1 = BeautifulSoup(page1.text, 'html.parser')
    url2 = source['EdD']
    page2 = requests.get(url2)
    soup2 = BeautifulSoup(page2.text, 'html.parser')

    x1 = extract_content(soup1, 'Doctor of Business Administration (DBA)', 'Start your application today!')
    x2 = extract_content(soup2, 'Doctor of Education in Leadership, Curriculum, and Instruction (EdD)',
                         'Start your application today!')

    y1 = extract_inner_string(x1, 'Admissions Requirements', 'used.', include_end=True)
    y2 = extract_inner_string(x2, 'Admission Requirements', 'used.', include_end=True)
    final_text = y1 + '\n\n' + y2

    return final_text
