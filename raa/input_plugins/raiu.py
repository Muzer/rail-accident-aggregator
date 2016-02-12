import raa.accident as accident

from bs4 import BeautifulSoup
import dateutil.parser
import re
import requests
import urllib.parse

RAIU_PUBS_URL = "http://raiu.ie/publications/"

requests_session = requests.Session()

def get_site_as_string():
    r = requests_session.get(RAIU_PUBS_URL)
    if r.status_code != 200:
        raise ConnectionError(
                'Got status code {} not 200.'.format(r.status_code))
    return (r.url, r.text)

def get_accidents():
    url, text = get_site_as_string()
    soup = BeautifulSoup(text)
    completed = soup.find('h2', id='completedinvestigations')
    if completed is None:
        return None
    ul = completed.find_next_sibling('ul')
    if ul is None:
        return None
    accidents = []
    for li in ul.find_all('li'):
        report_url = urllib.parse.urljoin(url, li.a.get('href'))
        text = li.a.get_text()
        new_accident = accident.Accident('en', report_url, 'ie', text, 'RAIU')
        regex = \
            re.compile(
            ".* ([0-9]?[0-9](st|nd|rd|th)? [^ ]* [0-9][0-9][0-9][0-9]).*")
        matches = regex.match(text)
        if not matches is None:
            new_accident.date = dateutil.parser.parse(matches.group(1))
        # We don't technically need a published date, but it makes it more
        # useful if we have one. Let's try to make a best guess based on the
        # modified date of the PDF reported by HTTP. It seems to work well
        # enough until you go back too far.
        published = dateutil.parser.parse(requests_session.head(
            report_url).headers['last-modified'])
        new_accident.published = published
        accidents.append(new_accident)
    return accidents

