from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def McDanielCollege_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "Graduate Academic Schedule",
                        'How to Apply')

    # print(x)
    #
    # y = extract_inner_string(x, 'Graduate Academic Schedule', 'Special Opportunity!')
    #
    # raise ValueError

    return x
