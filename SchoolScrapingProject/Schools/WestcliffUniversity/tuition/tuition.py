from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def WestcliffUniversity_tuition(source):
    soup = BeautifulSoup(source, 'html.parser')

    x1 = extract_content(soup, 'The 2023-2024 Tuition & Fees', 'F-1 Students')
    x2 = extract_content(soup, 'The 2023-2024 Tuition & Fees', 'The 2024-2025 Tuition & Fees')
    x3 = extract_inner_string(x2, 'International (F-1) Students', '$0.00 per $1000', include_end=True)
    x_final = x1 + x3

    y1 = extract_content(soup, 'The 2024-2025 Tuition & Fees', 'F-1 Students')
    y2 = extract_content(soup, 'The 2024-2025 Tuition & Fees', '$0.00 per $1,000', include_end=True)
    y3 = extract_inner_string(y2, 'International (F-1) Students', '$0.00 per $1000', include_end=True)
    y_final = y1 + y3

    final_text = x_final + '\n\n' + y_final

    return final_text
