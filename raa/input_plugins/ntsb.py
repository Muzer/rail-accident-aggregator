import raa.accident as accident

from bs4 import BeautifulSoup
import dateutil.parser
import re
import requests
import urllib.parse

NTSB_URL = "http://www.ntsb.gov/investigations/AccidentReports" \
        "/Pages/railroad.aspx"

def get_site_as_string():
    r = requests.get(NTSB_URL)
    if r.status_code != 200:
        raise ConnectionError(
                'Got status code {} not 200.'.format(r.status_code))
    return (r.url, r.text)

def get_accidents():
    url, text = get_site_as_string()
    soup = BeautifulSoup(text)
    table = soup.find('table', id='ntsb-tbl')
    accidents = []
    for row in table.find_all('tr', recursive=False):
        tds = row.find_all('td', recursive=False)
        # No ID means preliminary report (I think)
        if tds[0].get_text().strip() == '':
            continue
        language = 'en'
        # No PDF? No point!
        a = tds[8].a
        if a is None:
            continue
        pdf_url = urllib.parse.urljoin(url, a.get('href'))
        country = 'us'
        desc = tds[1].get_text()
        org = 'NTSB'
        # Stupid Americans
        date = dateutil.parser.parse(tds[2].get_text(), dayfirst=False)
        published = dateutil.parser.parse(tds[3].get_text(), dayfirst=False)
        location = tds[4].get_text() + ", " + tds[5].get_text()
        # WTF? Why is there a country field?
        alturls = {'landing': urllib.parse.urljoin(url, tds[1].a.get('href'))}
        new_accident = accident.Accident(language, pdf_url, country, desc, org)
        new_accident.location = location
        new_accident.date = date
        new_accident.published = published
        new_accident.alturls = alturls
        print(new_accident.__dict__)
        accidents.append(new_accident)
    return accidents
