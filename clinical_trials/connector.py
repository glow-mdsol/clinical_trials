
from six.moves.urllib.parse import urlencode, urljoin
from six.moves.html_parser import HTMLParser

import requests


BASE_URL = "https://clinicaltrials.gov/ct2/show/"


def get_study(nct_id):
    """
    Pull the XML for the study
    :param nct_id:
    :return:
    """
    t = urljoin(BASE_URL, nct_id)
    full_url = t + "?" + urlencode(dict(displayxml=True))
    response = requests.get(full_url)
    if not response.status_code == 200:
        raise ValueError("Unable to load study {}".format(nct_id))
    return response.content


class ClinicalTrialsHtmlParser(HTMLParser):
    """
    Pluck out the Documents
    TODO: Get results?
    """
    def __init__(self):
        super(ClinicalTrialsHtmlParser, self).__init__()
        self.docs = {}

    def handle_starttag(self, tag, attrs):
        _attr = dict(attrs)
        if tag == "a":
            if _attr.get('href', '').startswith("/ProvidedDocs"):
                self.docs[_attr['title']] = _attr['href']


def get_study_documents(nct_id):
    """
    Inspect the NCT Page to determine
    :param nct_id:
    :return:
    """
    t = urljoin(BASE_URL, nct_id)
    response = requests.get(t)
    docs = {}
    if 'ProvidedDocs' in response.text:
        # extract the content
        parser = ClinicalTrialsHtmlParser()
        parser.feed(response.text)
        docs = parser.docs
    return docs

