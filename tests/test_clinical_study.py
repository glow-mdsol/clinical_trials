import datetime
import glob
import unittest
import os

from mock import mock
from xmlschema import XMLSchema
from clinical_trials.clinical_study import ClinicalStudy, StudyArm

SCHEMA_LOCATION = os.path.join(os.path.dirname(__file__), '..', 'doc', 'schema', 'public.xsd')


def warmup_cache():
    """
    Populate the cache with contents from the fixture files
    :return:
    """
    cache = {}
    fixture_dir = os.path.join(os.path.dirname(__file__), 'fixtures')
    for opt in glob.glob(os.path.join(fixture_dir, '*.xml')):
        with open(opt, 'rb') as fh:
            content = fh.read()
        cache[os.path.splitext(os.path.basename(opt))[0]] = content
    return cache


class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        self.cache = warmup_cache()
        _schema = open(SCHEMA_LOCATION)
        self.schema = XMLSchema(_schema)


class TestSponsor(SchemaTestCase):

    def test_sponsor(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
        sponsor = study.sponsor
        self.assertEqual('Daiichi Sankyo, Inc.', sponsor.get('agency'))

    def test_collaborator(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
        collabs = study.collaborators
        self.assertEqual(1, len(collabs))
        self.assertEqual('Ambit Biosciences Corporation', collabs[0].get('agency'))

    def test_no_collaborator(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
            study = ClinicalStudy.from_nctid('NCT02348489')
        collabs = study.collaborators
        self.assertEqual(0, len(collabs))
        self.assertEqual([], collabs)


class TestInfo(SchemaTestCase):

    def test_study_id(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
        self.assertEqual('2689-CL-2004', study.study_id)

    def test_secondary_id(self):
        with mock.patch("clinical_trials.clinical_study.get_study") as dink:
            with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
                donk.return_value = self.schema
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
        self.assertEqual(['2011-005408-13'], study.secondary_id)

    def test_nct_id(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
        self.assertEqual('NCT01565668', study.nct_id)


class TestGetPeople(SchemaTestCase):

    def test_get_people(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
            self.assertEqual(1, len(study.study_people))


class TestGetMeSHTerms(SchemaTestCase):

    def test_get_people(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                mesh_terms = study.mesh_terms()
            self.assertEqual(3, len(mesh_terms))


class TestLocations(SchemaTestCase):

    def test_location_load(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                locations = study.locations
            self.assertEqual(24, len(locations))


class TestResponsibleParty(SchemaTestCase):

    def test_rp_load(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                rps = study.responsible_parties
            self.assertEqual(1, len(rps))


class TestStudyKeywords(SchemaTestCase):

    def test_rp_load(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                keywords = study.keywords
            self.assertEqual(4, len(keywords))


class TestLocationCountries(SchemaTestCase):

    def test_rp_load(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                countries = study.countries
            self.assertEqual(4, len(countries))
            for country in ('France', 'Italy', 'United Kingdom', 'United States'):
                self.assertIn(country, countries)


class TestOversightInfo(SchemaTestCase):

    def test_load_oversight_no_dmc(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                oversight = study.oversight_info
            # this is asserted
            self.assertFalse(oversight.has_dmc)
            # this is not
            self.assertIsNone(oversight.is_us_export)

    def test_load_oversight_with_dmc(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
                oversight = study.oversight_info
            # this is asserted
            self.assertTrue(oversight.has_dmc)
            # this is not
            self.assertIsNone(oversight.is_us_export)


class TestEligibility(SchemaTestCase):

    def test_parse_eligibility_criteria_gender(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
                eligibility = study.eligibility
            self.assertEqual('All', eligibility.gender)
            self.assertFalse(eligibility.gender_based)

    def test_healthy_volunteers(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
                eligibility = study.eligibility
            self.assertEqual("No", eligibility.healty_volunteers)


class TestArmGroup(SchemaTestCase):

    def test_loads_all_arms(self):
        """
        We can load all the arms
        """
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
                arms = study.arms
            self.assertEqual(2, len(arms))
            for arm in arms:
                self.assertIn(arm.arm_group_label, ('SGI-110 (guadecitabine)', 'Treatment Choice'))
                if arm.arm_group_label == 'Treatment Choice':
                    self.assertEqual('Active Comparator', arm.arm_group_type)
                else:
                    self.assertEqual('Experimental', arm.arm_group_type)


class TestInterventions(SchemaTestCase):

    def test_loads_interventions_with_multiple_labels(self):
        """
        We can load all the interventions
        """
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT01565668')
                study = ClinicalStudy.from_nctid('NCT01565668')
                interventions = study.interventions
            self.assertEqual(1, len(interventions))
            for intervention in interventions:
                self.assertEqual("Drug", intervention.intervention_type)
                self.assertEqual("AC220", intervention.intervention_name)
                self.assertEqual(2, len(intervention.arms))
                self.assertEqual(2, len(intervention.aliases))
                for alias in intervention.aliases:
                    self.assertIn(alias, ('Quizartinib', 'ASP2689'))

    def test_loads_interventions_with_single_labels(self):
        """
        We can load all the interventions
        """
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get('NCT02348489')
                study = ClinicalStudy.from_nctid('NCT02348489')
                interventions = study.interventions
            self.assertEqual(2, len(interventions))
            for intervention in interventions:
                self.assertEqual(intervention.intervention_type, "Drug")
                self.assertIn(intervention.intervention_name, ("SGI-110 (guadecitabine)", "Treatment Choice"))
                self.assertEqual(1, len(intervention.arms))
                self.assertIsNone(intervention.aliases)


class TestStudyPhase(SchemaTestCase):

    def test_study_phases(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            for study_id, phase in (('NCT02348489', 'Phase 3'),
                                    ('NCT01565668', 'Phase 2'),
                                    ('NCT02536534', 'N/A')):
                with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                    dink.return_value = self.cache.get(study_id)
                    study = ClinicalStudy.from_nctid(study_id)
                    self.assertEqual(study.phase, phase)


class TestStudyType(SchemaTestCase):
    def test_study_types(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            for study_id, study_type in (('NCT02348489', 'Interventional'),
                                         ('NCT01565668', 'Interventional'),
                                         ('NCT02536534', 'Observational')):
                with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                    dink.return_value = self.cache.get(study_id)
                    study = ClinicalStudy.from_nctid(study_id)
                    self.assertEqual(study.study_type, study_type)


class TestStudyStatus(SchemaTestCase):

    def test_study_status(self):
        """
        Test the Overall Status
        """
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            for study_id, overall_status in (('NCT02348489', 'Active, not recruiting'),
                                             ('NCT01565668', 'Completed'),
                                             ('NCT02536534', 'Completed')):
                with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                    dink.return_value = self.cache.get(study_id)
                    study = ClinicalStudy.from_nctid(study_id)
                    self.assertEqual(study.status, overall_status)

    def test_last_known_status(self):
        """
        Test the last known status
        """
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            for study_id, overall_status in (('NCT02348489', ''),
                                             ('NCT01565668', ''),
                                             ('NCT02536534', '')):
                with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                    dink.return_value = self.cache.get(study_id)
                    study = ClinicalStudy.from_nctid(study_id)
                    self.assertEqual(study.last_known_status, overall_status)


class TestStudyTrail(SchemaTestCase):

    def test_study_trail_489(self):
        study_id = 'NCT02348489'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
                trail = study.trail
            self.assertFalse(trail.has_results)
            self.assertEqual(trail.study_first_posted.date, datetime.date(year=2015, month=1, day=28))
            self.assertEqual(trail.study_first_posted.date_type, "Estimate")
            #   <study_first_submitted>January 22, 2015</study_first_submitted>
            #   <study_first_submitted_qc>January 22, 2015</study_first_submitted_qc>
            self.assertEqual(trail.study_first_submitted.date, datetime.date(year=2015, month=1, day=22))
            self.assertEqual(trail.study_first_submitted_qc.date, datetime.date(year=2015, month=1, day=22))

    def test_study_trail_668(self):
        study_id = 'NCT01565668'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
                trail = study.trail
            self.assertFalse(trail.has_results)
            # March 29, 2012
            self.assertEqual(trail.study_first_posted.date, datetime.date(year=2012, month=3, day=29))
            self.assertEqual(trail.study_first_posted.date_type, "Estimate")
            #   <study_first_submitted>March 27, 2012</study_first_submitted>
            #   <study_first_submitted_qc>March 27, 2012</study_first_submitted_qc>
            self.assertEqual(trail.study_first_submitted.date, datetime.date(year=2012, month=3, day=27))
            self.assertEqual(trail.study_first_submitted_qc.date, datetime.date(year=2012, month=3, day=27))

    def test_study_trail_534(self):
        study_id = 'NCT02536534'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
                trail = study.trail
            self.assertFalse(trail.has_results)
            self.assertEqual(trail.study_first_posted.date, datetime.date(year=2015, month=9, day=1))
            self.assertEqual(trail.study_first_posted.date_type, "Estimate")
            self.assertEqual(trail.study_first_submitted.date, datetime.date(year=2015, month=8, day=10))
            self.assertEqual(trail.study_first_submitted_qc.date, datetime.date(year=2015, month=8, day=31))
            # <disposition_first_submitted>April 6, 2017</disposition_first_submitted>
            # <disposition_first_submitted_qc>April 6, 2017</disposition_first_submitted_qc>
            # <disposition_first_posted type="Actual">April 10, 2017</disposition_first_posted>
            self.assertIsNone(trail.disposition_first_posted)
            self.assertIsNone(trail.disposition_first_submitted)
            self.assertIsNone(trail.disposition_first_submitted_qc)
            #   <last_update_submitted>December 19, 2017</last_update_submitted>
            #   <last_update_submitted_qc>December 19, 2017</last_update_submitted_qc>
            #   <last_update_posted type="Actual">December 20, 2017</last_update_posted>
            self.assertEqual(trail.last_update_posted.date, datetime.date(year=2017, month=12, day=20))
            self.assertEqual(trail.last_update_posted.date_type, "Actual")
            self.assertEqual(trail.last_update_submitted.date, datetime.date(year=2017, month=12, day=19))
            self.assertEqual(trail.last_update_submitted_qc.date, datetime.date(year=2017, month=12, day=19))


class TestStudyConditions(SchemaTestCase):

    def test_study_conditions(self):
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            for study_id, condition in (('NCT02348489', ['Leukemia, Myeloid, Acute']),
                                             ('NCT01565668', ['Leukemia, Myeloid, Acute']),
                                             ('NCT02536534', ['Hypertension, Pulmonary'])):
                with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                    dink.return_value = self.cache.get(study_id)
                    study = ClinicalStudy.from_nctid(study_id)
                    self.assertEqual(study.conditions(), condition)


class TestLink(SchemaTestCase):

    def test_links(self):
        """
        With links we get links ;-)
        """
        study_id = 'NCT02536534'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
                links = study.links
            self.assertEqual(len(links), 3)

    def test_no_links(self):
        """
        With no links, well you get the picture
        """
        study_id = 'NCT01565668'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
                links = study.links
            self.assertEqual(len(links), 0)


class TestCompletionDate(SchemaTestCase):

    def test_completion_date(self):
        """
        Get the completion date
        """
        study_id = 'NCT01565668'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(study.completion_date.date, datetime.date(month=3, year=2015, day=1))
            self.assertEqual(study.completion_date.date_type, "Actual")

    def test_anticipated_completion_date(self):
        """
        Get the completion date
        """
        study_id = 'NCT02348489'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(study.completion_date.date, datetime.date(month=6, year=2018, day=1))
            self.assertEqual(study.completion_date.date_type, "Anticipated")


class TestPrimaryCompletionDate(SchemaTestCase):

    def test_primary_completion_date(self):
        """
        Get the primary completion date
        """
        study_id = 'NCT01565668'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(study.primary_completion_date.date, datetime.date(month=3, year=2015, day=1))
            self.assertEqual(study.primary_completion_date.date_type, "Actual")

    def test_anticipated_primary_completion_date(self):
        """
        Get the anticipated primary completion date
        """
        study_id = 'NCT02348489'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(study.completion_date.date, datetime.date(month=6, year=2018, day=1))
            self.assertEqual(study.completion_date.date_type, "Anticipated")


class TestEnrollment(SchemaTestCase):

    def test_enrollment(self):
        study_id = 'NCT02348489'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(study.enrollment_info.count, 815)
            self.assertEqual(study.enrollment_info.count_type, "Actual")


class TestOutcomes(SchemaTestCase):

    def test_enrollment_489(self):
        study_id = 'NCT02348489'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(len(study.outcomes.primary), 2)
            self.assertEqual(len(study.outcomes.secondary), 6)
            self.assertEqual(len(study.outcomes.other), 0)

    def test_enrollment_668(self):
        study_id = 'NCT01565668'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(len(study.outcomes.primary), 2)
            self.assertEqual(len(study.outcomes.secondary), 8)
            self.assertEqual(len(study.outcomes.other), 0)


class TestVerificationDate(SchemaTestCase):

    def test_enrollment_489(self):
        study_id = 'NCT02348489'
        with mock.patch('clinical_trials.clinical_study.get_schema') as donk:
            donk.return_value = self.schema
            with mock.patch("clinical_trials.clinical_study.get_study") as dink:
                dink.return_value = self.cache.get(study_id)
                study = ClinicalStudy.from_nctid(study_id)
            self.assertEqual(study.verification_date.date, datetime.date(month=12, day=1, year=2017))

