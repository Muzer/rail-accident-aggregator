import raa.accident as accident

from bs4 import BeautifulSoup
import dateutil.parser
import re
import requests

TAIC_URL = "http://www.taic.org.nz/ReportsandSafetyRecs/RailReports" \
        "/tabid/85/language/en-US/Default.aspx"

TAIC_URL_MAGIC_ARG = \
        "__EVENTTARGET=dnn$ctr483$ViewOccurrenceReport$fileDownloadLink"

requests_session = requests.Session()

# Now, this one's a tricky one. The site is absolutely horrific.

def get_site_as_string(url):
    r = requests_session.get(url)
    if r.status_code != 200:
        raise ConnectionError(
                'Got status code {} not 200.'.format(r.status_code))
    return (r.url, r.text)

def get_accidents():
    url, text = get_site_as_string(TAIC_URL)
    soup = BeautifulSoup(text)
    divs = soup.find('div', id='dnn_ctr483_ModuleContent')
    accidents = []
    # I was going to attempt to implement pages, but they seriously make very
    # little sense on this. All attempts at programmatic access have failed, so
    # for now at least, page 1 only.
    for div in divs.find_all('div', {'id': None, 'class': None},
            recursive=False):
        language = 'en'
        country = 'nz'
        desc = div.find('span', id=re.compile('.*lblTitle')).get_text()
        org = 'TAIC'
        longdesc = div.find('span', id=re.compile('.*lblAbstract')).get_text()
        # Date parsing
        date = None
        regex = \
            re.compile(
            ".* ([0-9]?[0-9](st|nd|rd|th)? [^ ]* [0-9][0-9][0-9][0-9]).*")
        matches = regex.match(desc)
        if not matches is None:
            date = dateutil.parser.parse(matches.group(1))
        published = dateutil.parser.parse(
                div.find('span', id=re.compile(
                    '.*lblPublishedDate')).get_text().replace(
                        'Published on ', ''))
        # Extract URL fr om insanity
        insanity = div.find('a', id=re.compile('.*reportButton')).get('href')
        regex = re.compile('.*"(http[^"]*)"')
        matches = regex.match(insanity)
        landing = matches.group(1)
        # Now we're going to be evil and assume that there is already an
        # argument, because I'm getting lazy at this stage and it's too
        # much work to use urllib to do it properly
        pdf_url = landing + '&' + TAIC_URL_MAGIC_ARG
        new_accident = accident.Accident(language, pdf_url, country, desc,
                org)
        new_accident.longdesc = longdesc
        new_accident.date = date
        new_accident.published = published
        new_accident.alturls = { 'landing': landing }
        print(new_accident.__dict__)
        accidents.append(new_accident)
