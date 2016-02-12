import raa.accident as accident

from bs4 import BeautifulSoup
import dateutil.parser
import feedparser
import re
import urllib.parse

# Workaround things being broken
feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')

RAIB_ATOM_URL = \
    "https://www.gov.uk/government/announcements.atom" \
    "?departments[]=rail-accident-investigation-branch"


def get_pdf_link(html, relative_to = None):
    soup = BeautifulSoup(html)
    attachment = soup.find('section', class_='attachment')
    if attachment is None:
        return None
    details = attachment.find('div', class_='attachment-details')
    if details is None:
        return None
    if relative_to == None:
        return details.h2.a.get('href')
    else:
        return urllib.parse.urljoin(relative_to, details.h2.a.get('href'))


def get_longdesc(html):
    soup = BeautifulSoup(html)
    summary = soup.find(id='summary')
    if summary is None:
        return None
    sumtag = summary.name
    summary_text = ''
    for sibling in summary.next_siblings:
        if sibling.name == sumtag:
            break
        if sibling.name != 'p':
            continue
        summary_text += sibling.get_text() + '\n\n'
    return summary_text.strip()


def is_report_or_bulletin(entry):
    # We have to use some rather horrible heuristics
    if not [x for x in entry.tags if x.term == 'Press release']:
        return False
    # Now, it's a press release. Could still be an announcement about RAIB.
    # We need to go deeper! Parse the content as HTML.
    return not (get_pdf_link(entry.content[0].value) is None)


def get_accidents():
    feed = feedparser.parse(RAIB_ATOM_URL)
    accidents = []
    page = 1
    while feed.entries:
        for entry in feed.entries:
            if not is_report_or_bulletin(entry):
                continue
            new_accident = accident.Accident(
                    'en', get_pdf_link(entry.content[0].value, feed.href),
                    # Strip "Press release: "
                    'gb', ': '.join(entry.title.split(": ")[1:]), "RAIB")
            # Location is too hard to parse for now
            new_accident.longdesc = get_longdesc(entry.content[0].value)
            # Company is not provided (usually)
            # Let's parse the date with regex!
            regex = \
                re.compile(
                ".* ([0-9]?[0-9](st|nd|rd|th)? [^ ]* [0-9][0-9][0-9][0-9]).*")
            matches = regex.match(entry.summary)
            if not matches is None:
                new_accident.date = dateutil.parser.parse(matches.group(1))
            new_accident.published = dateutil.parser.parse(entry.published)
            new_accident.alturls = {'landing': entry.link}
            accidents.append(new_accident)
        page += 1
        feed = feedparser.parse(RAIB_ATOM_URL + "&page={}".format(page))
