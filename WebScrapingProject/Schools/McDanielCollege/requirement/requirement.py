from bs4 import BeautifulSoup
from Schools.utils import (extract_content,
                                              extract_inner_string)


def McDanielCollege_requirement(source):
    soup = BeautifulSoup(source, 'html.parser')
    x = extract_content(soup, 'What You Need to Know About the M.S. in Data Analytics', 'Related Programs')
    y = extract_inner_string(x, 'What You Need to Know About the M.S. in Data Analytics',
                             'outside of the US.',
                             include_end=True)
    return y
