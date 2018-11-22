from unittest import TestCase

import requests_mock

from clinical_trials.connector import get_study_documents


class TestGetStudyDocuments(TestCase):

    def test_no_study_docs(self):
        with requests_mock.Mocker() as m:
            m.get("https://clinicaltrials.gov/ct2/show/some_nct_id", status_code=200, text="<html></html>")
            docs = get_study_documents("some_nct_id")
            self.assertEqual({}, docs)

    def test_a_study_doc(self):
        text = """<span class="header2">&nbsp; Study Documents (Full-Text)</span>

  <div class="indent2">
    <br/>
    Documents provided by Helse Stavanger HF:
        <div class="indent2" style="margin-top:2ex">
      <a class='study-link' href="/ProvidedDocs/43/NCT03741543/Prot_000.pdf" title="Study Protocol" onclick="openNewWindow('/ProvidedDocs/43/NCT03741543/Prot_000.pdf'); return false">Study Protocol</a>&nbsp; [PDF] May 10, 2017
    </div>
       <br/>
  </div>
  </div>
    

"""
        with requests_mock.Mocker() as m:
            m.get("https://clinicaltrials.gov/ct2/show/some_nct_id", status_code=200, text=text)
            docs = get_study_documents("some_nct_id")
            self.assertEqual({"Study Protocol": "/ProvidedDocs/43/NCT03741543/Prot_000.pdf"}, docs)
