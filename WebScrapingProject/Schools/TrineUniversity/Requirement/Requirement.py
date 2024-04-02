import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
columns = ['Graduate', 'Doctor']
df = pd.DataFrame(columns=columns)
TABLE = 'Requirement'

graduate_url = 'https://www.trine.edu/international/graduate/international-apply.aspx'
graduate_page = requests.get(graduate_url)

with open('graduate.html', 'w', encoding='utf-8') as file:
    file.write(graduate_page.text)

with open('graduate.html', 'r', encoding='utf-8') as file:
    content = file.read()

graduate_soup = BeautifulSoup(content, 'html.parser')

h2_tag = graduate_soup.find('h2', string="International Graduate/Master's Degree application")

text = h2_tag.find_next_sibling("ul").find_next_sibling("ul").find('li').get_text(separator='\n', strip=True)
df.at[0, 'Graduate'] = text

doctor_url = 'https://www.trine.edu/online/degrees/engineering-technology/online-doctor-information-technology.aspx'
doctor_page = requests.get(doctor_url)

with open('doctor.html', 'w', encoding='utf-8') as file:
    file.write(doctor_page.text)

with open('doctor.html', 'r', encoding='utf-8') as file:
    content = file.read()

doctor_soup = BeautifulSoup(content, 'html.parser')

text = doctor_soup.find(string='Admission Requirements').find_next('li').get_text(separator='\n', strip=True)
df.at[0, 'Doctor'] = text
df.to_csv(TABLE + '.csv')
