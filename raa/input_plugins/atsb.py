import raa.accident as accident

from bs4 import BeautifulSoup
import dateutil.parser
import requests
import urllib.parse

# Optional caching module.
try:
    import requests_cache
    requests_session = requests_cache.core.CachedSession(cache_name='atsb')
except:
    requests_session = requests.Session()

ATSB_URL = "https://www.atsb.gov.au/publications" \
        "/safety-investigation-reports/?s=1&mode=Rail" \
        "&sort=OccurrenceReleaseDate&sortAscending=descending" \
        "&reportStatus=Final&printAll=true&occurrenceClass=&typeOfOperation=" \
        "&initialTab=2"

requests_uncached_session = requests.Session()

def get_site_as_string(url, session):
    r = session.get(url)
    if r.status_code != 200:
        raise ConnectionError(
                'Got status code {} not 200.'.format(r.status_code))
    return (r.url, r.text)

def get_subpage_info(landing):
    url, text = get_site_as_string(landing, requests_session)
    soup = BeautifulSoup(text)
    pdf_class = soup.find('div', class_='pdf')
    # Some investigations don't result in reports (eg external)
    if pdf_class is None:
        pdf_url = None
    else:
        pdf_url = urllib.parse.urljoin(url,
                soup.find('div', class_='pdf').find('a').get('href'))
    word_class = soup.find('div', class_='alternate_file')
    if word_class is None:
        word_url = None
    else:
        word_url = urllib.parse.urljoin(url, word_class.find('a').get('href'))
    location = soup.find('td', { 'headers': 'cell_Location' }).get_text()
    return (pdf_url, location, word_url)

def get_accidents():
    url, text = get_site_as_string(ATSB_URL, requests_uncached_session)
    soup = BeautifulSoup(text)
    table = soup.find('table', class_='selectable_grid')
    if table is None:
        return None
    accidents = []
    for tr in table.find_all('tr', class_=lambda x : x != 'header'):
        language = 'en'
        country = 'au'
        desc = tr.find_all('td')[1].get_text()
        org = 'ATSB'
        date = dateutil.parser.parse(tr.find_all('td')[2].get_text())
        published = dateutil.parser.parse(tr.find_all('td')[4].get_text())
        landing = urllib.parse.urljoin(url,
                tr.find('td', class_='investigation_number').a.get('href'))
        pdf_url, location, word_url = get_subpage_info(landing)
        # If there isn't a PDF, don't bother
        if pdf_url is None:
            continue
        new_accident = accident.Accident(language, pdf_url, country, desc, org)
        new_accident.date = date
        new_accident.published = published
        new_accident.location = location
        if word_url is None:
            new_accident.alturls = { 'landing': landing }
        else:
            new_accident.alturls = { 'landing': landing, 'word': word_url }
        accidents.append(new_accident)
    return accidents
