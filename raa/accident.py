class Accident:
    """
    Class representing a rail accident.

    language: language of report
    url: URL to report (usually PDF)
    country: country of report
    desc: short description of accident
    org: organisation publishing report
    location: (optional) place in/near which accident occurred
    longdesc: (optional) long description of accident
    date: (optional) date on which accident occurred
    published: (optional) date on which the report was published
    alturls: (optional) dictionary of alternative URLs, with the file formats
             as the keys and the URLs as the values. Special key 'landing'
             describes a URL to an HTML landing page containing summary and
             human-accessible download options.
    """
    def __init__(self, language, url, country, desc, org):
        self.language = language
        self.url = url
        self.country = country
        self.desc = desc
        self.org = org
        self.location = None
        self.longdesc = None
        self.date = None
        self.published = None
        self.alturls = None
