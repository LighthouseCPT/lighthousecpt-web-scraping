import requests
from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def TrineUniversity_requirement(source_dict):  # Source will contain a dict of 2 URLs
    url1 = source_dict['1']
    page1 = requests.get(url1)
    soup1 = BeautifulSoup(page1.text, 'html.parser')
    url2 = source_dict['2']
    page2 = requests.get(url2)
    soup2 = BeautifulSoup(page2.text, 'html.parser')

    x1 = extract_content(soup1, "International Graduate/Master's Degree application",
                         'Take the Next Steps')
    x2 = extract_content(soup2, 'Doctor of Information Technology',
                         'Take the Next Steps')

    y1 = extract_inner_string(x1, "International Graduate/Master's Degree application",
                              'Seated classes')

    y2 = extract_inner_string(x2, 'Learn More', 'intend to enroll.', include_end=True)
    y2 = "Doctor of Information Technology Doctorate\n" + y2
    final_text = y1 + '\n\n' + y2

    return final_text
