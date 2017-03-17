import raa.accident as accident

from bs4 import BeautifulSoup
import dateutil.parser
import feedparser
import re
import urllib.parse

# Workaround things being broken
try:
    feedparser.PREFERRED_XML_PARSERS.remove('drv_libxml2')
except:
    pass

TSB_RSS_URL = "http://www.tsb.gc.ca/eng/fils-feeds/TSB%20Rail.xml"


def get_pdf_link(link):
    return link.replace('.asp', '.pdf')

def get_html_attrs(html):
    soup = BeautifulSoup(html)
    desc = soup.get_text()
    if len(desc.split('\n')) >= 5:
        # Sometimes we're lucky
        location = desc.split('\n')[-2]
        # Remember to replace NBSPs which sometimes sneak in!
        date = dateutil.parser.parse(desc.split('\n')[-1].replace('\xa0',' '))
        desc = '\n'.join(desc.split('\n')[:-2])
    else:
        # Sometimes we're not. In the case of no useful linebreaks, sacrifice
        # location for the greater good.
        location = None
        # Let's parse the date with regex!
        regex = \
            re.compile(
            ".* ([0-9]?[0-9](st|nd|rd|th)? [^ ]* [0-9][0-9][0-9][0-9]).*")
        matches = regex.match(desc)
        if matches is None:
            date = None
        else:
            date = dateutil.parser.parse(matches.group(1))
    return desc, location, date


def is_report(entry):
    return entry.title.startswith('Railway Investigation Report ')


def get_accidents():
    feed = feedparser.parse(TSB_RSS_URL)
    accidents = []
    for entry in feed.entries:
        if not is_report(entry):
            continue
        desc, location, date = get_html_attrs(entry.description)
        new_accident = accident.Accident(
                'en', get_pdf_link(entry.link), 'ca', desc, "TSB")
        new_accident.location = location
        new_accident.date = date
        new_accident.published = dateutil.parser.parse(entry.published)
        new_accident.alturls = {'landing': entry.link}
        accidents.append(new_accident)
    return accidents
