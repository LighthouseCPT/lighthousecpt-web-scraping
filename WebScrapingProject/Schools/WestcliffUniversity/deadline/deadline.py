from bs4 import BeautifulSoup
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)


def WestcliffUniversity_deadline(source):
    soup = BeautifulSoup(source, 'html.parser')
    div_tag = soup.find('div', id="description2")
    paragraphs = div_tag.find_all('p')
    h3 = div_tag.find_all('h3')
    h3 = [t.contents[0] for t in h3]

    # Initialize lists to store data
    semesters = []
    session_dates = []
    deadlines = []

    # Iterate over paragraphs and extract data
    for p in paragraphs:
        strong_tag = p.find('strong')
        if strong_tag:
            semester_info = strong_tag.text.strip()
            deadline_info = p.text.replace(strong_tag.text, '').strip()[22:]
            semester, session_date = semester_info.split(' - ')
            semesters.append(semester)
            session_dates.append(session_date)
            deadlines.append(deadline_info)

    # Create DataFrame
    data = {'Semester': semesters, 'Session Date': session_dates, 'Application Deadline': deadlines}
    df = pd.DataFrame(data)

    # Add a new column with specified values based on ranges
    ranges_values = {(0, 5): h3[0], (6, 11): h3[1], (12, 17): h3[2]}
    df['Student Type'] = [next((value for (start, end), value in ranges_values.items() if start <= i <= end), None)
                          for i in range(len(df))]
    return df
