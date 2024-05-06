from bs4 import BeautifulSoup
from Schools.utils import extract_content, make_request, extract_inner_string


def TrineUniversity_deadline(source_dict):
    url1 = source_dict['1']
    page1 = make_request(url1)
    soup1 = BeautifulSoup(page1.text, 'html.parser')
    url2 = source_dict['2']
    page2 = make_request(url2)
    soup2 = BeautifulSoup(page2.text, 'html.parser')

    x1 = extract_content(soup1, "TrineOnline Academic Calendar",
                         'Take the Next Steps')

    x2 = extract_inner_string(x1, 'Summer Term 1', 'May 5– May 10')

    y1 = extract_content(soup2, "International Orientation",
                         'Take the Next Steps', newline_after='year')

    y2 = extract_inner_string(y1, 'Summer 2024', 'Class/Session Start Date: June 9, 2025')

    add_ins = [
        "Rename 'Immigration Check-in & Program Start Date' to 'CPT Start Date'",
        "Only the 'Application Deadline', 'Term Start Date', 'Term End Date', and 'CPT Start Date' are needed",
        "There is no need for the 'Class/Session Start Date'",
        "CRITICAL: The output rows should strictly follow this order: 'CPT Start Date', 'Application Deadline', ",
        "'Term Start Date', and 'Term End Date'. This sequence is mandatory for each term."
    ]

    final_text = (x2 + '\n' + y2)

    return final_text, add_ins
