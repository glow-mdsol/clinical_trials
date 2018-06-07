
from six.moves.urllib.parse import urlencode, urljoin

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

