from bs4 import BeautifulSoup
from Schools.utils import extract_content, extract_inner_string


def MonroeCollege_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')

    x = extract_content(soup, "Spring 2024 Academic Calendar",
                        'Course Catalog', include_end=True)

    add_ins = [
        f"The end date of the program/class and session is the Last Day of Classes. Ignore Finals Week, "
        f"Semester Ends / Grades Due, Semester Break or anything else that comes after the Last Day of Classes; "
        f"they are not part of the program/class and session. "
    ]

    return x, add_ins
