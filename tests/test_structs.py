import os
from unittest import mock

import pytest
from xmlschema import XMLSchema

from clinical_trials import ClinicalStudy
from clinical_trials.structs import ProvidedDocument

SCHEMA_LOCATION = os.path.join(os.path.dirname(__file__), '..', 'doc', 'schema', 'public.xsd')


@pytest.fixture()
def schema():
    _schema = open(SCHEMA_LOCATION)
    return XMLSchema(_schema)


def get_study(nctid):
    fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    opt = os.path.join(fixture_dir, '{}.xml'.format(nctid))
    with open(opt, 'rb') as fh:
        content = fh.read()
    return content


def test_provided_documents_no_docs(schema):
    nct_id = "NCT03723057"
    with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
        donk.return_value = schema
        with mock.patch("clinical_trials.clinical_study.get_study") as dink:
            dink.return_value = get_study(nct_id)
            study = ClinicalStudy.from_nctid(nct_id)
        assert study.provided_docs == []


def test_provided_documents_with_docs(schema):
    nct_id = "NCT03982511"
    with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
        donk.return_value = schema
        with mock.patch("clinical_trials.clinical_study.get_study") as dink:
            dink.return_value = get_study(nct_id)
            study = ClinicalStudy.from_nctid(nct_id)
        assert len(study.provided_docs) == 1
        provided_doc = study.provided_docs[0]   # type: ProvidedDocument
        assert provided_doc.type == "Informed Consent Form"
        assert provided_doc.has_icf is True
        assert provided_doc.has_protocol is False
        assert provided_doc.has_sap is False
        assert provided_doc.date == "February 22, 2019"
        assert provided_doc.url == "https://ClinicalTrials.gov/ProvidedDocs/11/NCT03982511/ICF_000.pdf"


def test_fetch_provided_docs(schema, tmpdir):
    nct_id = "NCT03982511"
    with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
        donk.return_value = schema
        with mock.patch("clinical_trials.clinical_study.get_study") as dink:
            dink.return_value = get_study(nct_id)
            study = ClinicalStudy.from_nctid(nct_id)
        assert len(study.provided_docs) == 1
        provided_doc = study.provided_docs[0]   # type: ProvidedDocument
        with mock.patch('clinical_trials.structs.requests.get') as mock_get:
            mock_get.return_value = mock.MagicMock(status_code=200, content=b"some content")
            provided_doc.fetch_document(tmpdir)
            assert len(tmpdir.listdir()) == 1
            assert os.path.basename(tmpdir.listdir()[0]) == "ICF_000.pdf"

