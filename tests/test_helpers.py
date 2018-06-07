import unittest

from mock import mock

from clinical_trials.clinical_study import ClinicalStudy
from clinical_trials.helpers import process_eligibility
from tests.test_clinical_study import SchemaTestCase


class TestEligibility(SchemaTestCase):
    def test_parsed_inclusion_668(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
            content = study.eligibility.criteria
            processed = process_eligibility(content)
            self.assertEqual(6, len(processed.get('inclusion')))

    def test_parsed_exclusion_668(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
            content = study.eligibility.criteria
            processed = process_eligibility(content)
            self.assertEqual(18, len(processed.get('exclusion')))
            criterion = '-  Subject has any medical, psychiatric, addictive or other kind of disorder which compromises ' \
                        'the ability of the subject to give written informed consent and/or to comply with procedures'
            self.assertEqual(criterion, processed.get('exclusion')[-1])

    def test_parsed_inclusion_489(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
            content = study.eligibility.criteria
            processed = process_eligibility(content)
            self.assertEqual(15, len(processed.get('inclusion')))

    def test_parsed_exclusion_489(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
            content = study.eligibility.criteria
            processed = process_eligibility(content)
            self.assertEqual(9, len(processed.get('exclusion')))

    def test_parsed_inclusion_534(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02536534')
                study = ClinicalStudy.from_nctid('NCT02536534')
            content = study.eligibility.criteria
            processed = process_eligibility(content)
            self.assertEqual(10, len(processed.get('inclusion')))

    def test_parsed_exclusion_534(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02536534')
                study = ClinicalStudy.from_nctid('NCT02536534')
            content = study.eligibility.criteria
            processed = process_eligibility(content)
            self.assertEqual(4, len(processed.get('exclusion')))


class TestTextBlock(SchemaTestCase):

    def test_brief_summary(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02536534')
                study = ClinicalStudy.from_nctid('NCT02536534')
            desc = 'Evaluate the correlation between activity level (monitored by Fitbit Flex remote activity tracker) ' \
                   'and 6-minute walk distance (6MWD) (performed by investigator) in patients with Pulmonary Arterial ' \
                   'Hypertension (PAH) or Chronic Thromboembolic Pulmonary Hypertension (CTEPH) over 6 months in ' \
                   'routine clinical practice settings.'
            content = study.brief_summary
            self.assertEqual(desc, content)

    def test_detailed_description(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02536534')
                study = ClinicalStudy.from_nctid('NCT02536534')
            desc = "Remote patient monitoring can lead to improved patient outcomes, including improved quality of " \
                   "life, reduced readmissions, earlier treatment for symptoms detected prior to schedule in-office " \
                   "follow-up visits, improved communications with care providers, increased participation in " \
                   "self-management of disease, and an improved knowledge of their medical conditions . In patients " \
                   "with PAH, daily activity level, as measured using a physical activity monitor for seven " \
                   "consecutive days, correlated with 6-minute walk distance (6MWD). The monitor used in the " \
                   "aforementioned PAH study was positioned on the patients' right upper arm with an armband, " \
                   "as opposed to the more popular and more comfortable wristbands used today, such as the Fitbit " \
                   "Flex. Although the aforementioned PAH study did show a correlation between activity level " \
                   "monitoring and 6MWD, the patients were monitored for only seven days. " \
                   "It is still unknown whether " \
                   "this correlation would exist over a longer trial period and whether patients, their caregivers, " \
                   "and clinicians would find activity level monitoring useful in helping manage PH."
            content = study.detailed_description
            self.assertEqual(desc, content)


if __name__ == '__main__':
    unittest.main()
