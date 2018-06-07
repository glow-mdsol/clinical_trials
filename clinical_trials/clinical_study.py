import datetime
import logging

import six
from glom import glom

from clinical_trials.connector import get_study
from clinical_trials.errors import StudyDefinitionInvalid
from clinical_trials.helpers import process_textblock, process_eligibility
from clinical_trials.schema import get_schema

logging.basicConfig()
logger = logging.getLogger(__name__)


class CTStruct(object):
    REQUIRED = ()

    def is_valid(self):
        for req in self.REQUIRED:
            if getattr(self, req, None) is None:
                raise StudyDefinitionInvalid("Missing required attribute {} from {}".format(req,
                                                                                            self.__class__.__name__))

    @classmethod
    def from_dict(cls, dict_data):
        return cls(**dict_data)


class OversightInfo(CTStruct):
    """
    <xs:element name="has_dmc" type="yes_no_enum" minOccurs="0"/> <!-- data monitoring committee -->
    <xs:element name="is_fda_regulated_drug" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_fda_regulated_device" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_unapproved_device" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_ppsd" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_us_export" type="yes_no_enum" minOccurs="0"/>
    """
    def __init__(self, has_dmc=None, is_fda_regulated_drug=None,
                 is_fda_regulated_device=None, is_unapproved_device=None,
                 is_ppsd=None, is_us_export=None):
        """
        Careful with the NULL flavour
        :param has_dmc:
        :param is_fda_regulated_drug:
        :param is_fda_regulated_device:
        :param is_unapproved_device:
        :param is_ppsd:
        :param is_us_export:
        """
        self.has_dmc = has_dmc == 'Yes' if not has_dmc is None else None
        self.is_fda_regulated_drug = is_fda_regulated_drug == 'Yes' if not is_fda_regulated_drug is None else None
        self.is_fda_regulated_device = is_fda_regulated_device == 'Yes' if not is_fda_regulated_device is None else None
        self.is_unapproved_device = is_unapproved_device == 'Yes' if not is_unapproved_device is None else None
        self.is_ppsd = is_ppsd == 'Yes' if not is_ppsd is None else None
        self.is_us_export = is_us_export == 'Yes' if not is_us_export is None else None


class Address(CTStruct):
    """
    <xs:element name="city" type="xs:string"/>
    <xs:element name="state" type="xs:string"  minOccurs="0"/>
    <xs:element name="zip" type="xs:string"  minOccurs="0"/>
    <xs:element name="country" type="xs:string"/>
    """

    def __init__(self, city=None, state=None, zip=None, country=None):
        self.city = city
        self.state = state
        self.zip = zip
        self.country = country


class Facility(CTStruct):
    """
    <xs:element name="name" type="xs:string" minOccurs="0"/>
    <xs:element name="address" type="address_struct" minOccurs="0"/>
    """

    def __init__(self, name=None, address=None):
        self.name = name
        self.address = Address.from_dict(address) if address is not None else None


class Location(CTStruct):
    """
    <xs:element name="facility" type="facility_struct" minOccurs="0"/>
    <xs:element name="status" type="recruitment_status_enum" minOccurs="0"/>
    <xs:element name="contact" type="contact_struct" minOccurs="0"/>
    <xs:element name="contact_backup" type="contact_struct" minOccurs="0"/>
    <xs:element name="investigator" type="investigator_struct" minOccurs="0" maxOccurs="unbounded"/>
    """

    def __init__(self, facility=None, status=None, contact=None, contact_backup=None, investigator=None):
        self.facility = facility
        self.status = status
        self.contact = Contact.from_dict('location.contact', contact) if contact is not None else None
        self.contact_backup = Contact.from_dict('location.contact_backup', contact_backup) \
            if contact_backup is not None else None
        self.investigator = Investigator.from_dict('location.investigator', investigator) \
            if investigator is not None else None


class ResponsibleParty(CTStruct):

    def __init__(self, name_title=None, organization=None, responsible_party_type=None,
                 investigator_affiliation=None, investigator_full_name=None,
                 investigator_title=None):
        self.name_title = name_title
        self.organization = organization
        self.responsible_party_type = responsible_party_type
        self.investigator_affiliation = investigator_affiliation
        self.investigator_full_name = investigator_full_name
        self.investigator_title = investigator_title


class StudyContact(CTStruct):

    def __init__(self, context=None, first_name=None, middle_name=None, last_name=None, degrees=None):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.degrees = degrees
        self.context = context


class Contact(StudyContact):

    def __init__(self, context=None, first_name=None, middle_name=None, last_name=None, degrees=None,
                 phone=None, phone_ext=None, email=None):
        super(Contact, self).__init__(context, first_name, middle_name, last_name, degrees)
        self.phone = phone
        self.phone_ext = phone_ext
        self.email = email


class Investigator(StudyContact):

    def __init__(self, context=None, first_name=None,
                 middle_name=None, last_name=None,
                 degrees=None, role=None, affiliation=None):
        super(Investigator, self).__init__(context, first_name, middle_name, last_name, degrees)
        self.role = role
        self.affiliation = affiliation


class StudyEligibility(CTStruct):
    """
    <xs:element name="study_pop" type="textblock_struct" minOccurs="0"/>
    <xs:element name="sampling_method" type="sampling_method_enum" minOccurs="0"/>
    <xs:element name="criteria" type="textblock_struct" minOccurs="0"/>
    <xs:element name="gender" type="gender_enum"/>
    <xs:element name="gender_based" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="gender_description" type="xs:string" minOccurs="0"/>
    <xs:element name="minimum_age" type="age_pattern"/>
    <xs:element name="maximum_age" type="age_pattern"/>
    <xs:element name="healthy_volunteers" type="xs:string" minOccurs="0"/>
    """
    def __init__(self, study_pop=None, sampling_method=None, criteria=None,
                 gender=None, gender_based=None, gender_description=None,
                 minimum_age=None, maximum_age=None, healthy_volunteers=None):
        self._study_pop = study_pop
        self.sampling_method = sampling_method
        self._criteria = criteria
        self.gender = gender
        self._gender_based = gender_based
        self.gender_description = gender_description
        self.minimum_age = minimum_age
        self.maximum_age = maximum_age
        self.healty_volunteers = healthy_volunteers
        self._inclusion_criteria = None
        self._exclusion_criteria = None

    @property
    def gender_based(self):
        return self._gender_based == "Yes"

    @property
    def study_pop(self):
        return process_textblock(self._study_pop.get('textblock', ''))

    @property
    def inclusion_criteria(self):
        if self._inclusion_criteria is None:
            processed = process_eligibility(self.criteria)
            self._inclusion_criteria = processed.get('inclusion', [])
            self._exclusion_criteria = processed.get('exclusion', [])
        return self._inclusion_criteria

    @property
    def exclusion_criteria(self):
        if self._exclusion_criteria is None:
            processed = process_eligibility(self.criteria)
            self._inclusion_criteria = processed.get('inclusion', [])
            self._exclusion_criteria = processed.get('exclusion', [])
        return self._exclusion_criteria

    @property
    def criteria(self):
        return self._criteria.get('textblock')


class StudyArm(CTStruct):

    def __init__(self, arm_group_label=None, arm_group_type=None, description=None):
        self.arm_group_label = arm_group_label
        self.arm_group_type = arm_group_type
        self.description = description


class StudyIntervention(CTStruct):
    """
    <xs:element name="intervention_type" type="intervention_type_enum"/>
    <xs:element name="intervention_name" type="xs:string"/>
    <xs:element name="description" type="xs:string" minOccurs="0"/>
    <xs:element name="arm_group_label" type="xs:string" minOccurs="0" maxOccurs="unbounded"/>
    <xs:element name="other_name" type="xs:string" minOccurs="0" maxOccurs="unbounded"/> <!-- synonyms for intervention_name -->
    """
    def __init__(self, intervention_type=None, intervention_name=None, description=None, arm_group_label=None, other_name=None):
        self.intervention_type = intervention_type
        self.intervention_name = intervention_name
        self.description = description
        self.arms = arm_group_label
        self.aliases = other_name


class VariableDateStruct(CTStruct):

    def __init__(self, date_str=None, date_type=None):
        self.date_type = date_type
        self.raw_date_str = date_str

    @property
    def date(self):
        """
        "(Unknown|((January|February|March|April|May|June|July|August|September|October|November|December) (([12]?[0-9]|30|31)\, )?[12][0-9]{3}))"
        :return:
        """
        if self.raw_date_str == 'Unknown':
            return self.raw_date_str
        else:
            try:
                _date = datetime.datetime.strptime(self.raw_date_str, "%B %d, %Y")
            except ValueError:
                try:
                    _date = datetime.datetime.strptime(self.raw_date_str, "%B %Y")
                except ValueError:
                    logger.error("Unable to parse date: {}".format(self.raw_date_str))
                    return None
            return _date.date()

    def __eq__(self, other):
        return self.date == other


def parse_date(field):
    if field is None:
        # not supplied
        return field
    else:
        if isinstance(field, (six.string_types,)):
            # type variable_date_type
            return VariableDateStruct(date_str=field)
        elif isinstance(field, (dict,)):
            # type variable_date_struct
            return VariableDateStruct(date_str=field.get('$'),
                                      date_type=field.get('@type'))
        else:
            logger.error("Unexpected value: {} {}".format(field, type(field)))


class StudyTrail:

    def __init__(self, study_first_submitted=None, study_first_submitted_qc=None, study_first_posted=None,
                 last_update_submitted=None, last_update_submitted_qc=None, last_update_posted=None,
                 results_first_submitted=None, results_first_submitted_qc=None, results_first_posted=None,
                 disposition_first_submitted=None, disposition_first_submitted_qc=None, disposition_first_posted=None):
        self.study_first_submitted = parse_date(study_first_submitted)
        self.study_first_submitted_qc = parse_date(study_first_submitted_qc)
        self.study_first_posted = parse_date(study_first_posted)
        self.last_update_submitted = parse_date(last_update_submitted)
        self.last_update_submitted_qc = parse_date(last_update_submitted_qc)
        self.last_update_posted = parse_date(last_update_posted)
        self.results_first_submitted = parse_date(results_first_submitted)
        self.results_first_submitted_qc = parse_date(results_first_submitted_qc)
        self.results_first_posted = parse_date(results_first_posted)
        self.disposition_first_submitted = parse_date(disposition_first_submitted)
        self.disposition_first_submitted_qc = parse_date(disposition_first_submitted_qc)
        self.disposition_first_posted = parse_date(disposition_first_posted)

    @property
    def has_results(self):
        return self.results_first_submitted is not None


class Link(CTStruct):

    def __init__(self, url=None, description=None):
        self.url = url
        self.description = description


class EnrolmentStruct(CTStruct):

    def __init__(self, count, count_type):
        self.count = int(count)
        self.count_type = count_type

    @classmethod
    def from_dict(cls, message):
        return cls(count=message.get('$', ''), count_type=message.get('@type', ''))


class OutcomeStruct(CTStruct):

    def __init__(self, measure=None, time_frame=None, description=None):
        self.measure = measure
        self.time_frame = time_frame
        self.description = description


class StudyOutcomes:
    def __init__(self):
        self.primary = []
        self.secondary = []
        self.other = []

    def add_outcome(self, outcome_type, outcome_dict):
        if outcome_type == "primary":
            self.primary.append(OutcomeStruct.from_dict(outcome_dict))
        elif outcome_type == "secondary":
            self.secondary.append(OutcomeStruct.from_dict(outcome_dict))
        else:
            self.other.append(OutcomeStruct.from_dict(outcome_dict))


class ClinicalStudy:

    def __init__(self, data):
        self._data = data
        self._people = None
        self._facilities = None
        self._locations = None
        self._responsible_parties = None
        self._oversight_info = None
        self._eligibility = None
        self._arms = None
        self._interventions = None
        self._drug_names = []
        self._trail = None
        self._outcomes = None

    @property
    def verification_date(self):
        verification_date = glom(self._data, 'verification_date')
        logger.info("Verification Date: {}".format(verification_date))
        return parse_date(verification_date)

    @property
    def outcomes(self):
        """
        Get the study outcomes
        :rtype: StudyOutcomes
        """
        if self._outcomes is None:
            self.add_outcomes()
        return self._outcomes

    @property
    def enrollment_info(self):
        return EnrolmentStruct.from_dict(glom(self._data, 'enrollment'))

    @property
    def completion_date(self):
        return parse_date(glom(self._data, 'completion_date'))

    @property
    def primary_completion_date(self):
        return parse_date(glom(self._data, 'primary_completion_date'))

    @property
    def links(self):
        return [Link.from_dict(x) for x in glom(self._data, 'link', default=[])]

    @property
    def trail(self):
        """
        Get the study trail
        :rtype: StudyTrail
        """
        if self._trail is None:
            self.add_study_trail()
        return self._trail

    @property
    def phase(self):
        return glom(self._data, 'phase', default='N/A')

    @property
    def last_known_status(self):
        return glom(self._data, 'last_known_status', default='')

    @property
    def status(self):
        return glom(self._data, 'overall_status', default='')

    @property
    def study_type(self):
        return glom(self._data, 'study_type', default='')

    @property
    def brief_summary(self):
        content = glom(self._data, 'brief_summary.textblock', default='')
        return process_textblock(content)

    @property
    def detailed_description(self):
        content = glom(self._data, 'detailed_description.textblock', default='')
        return process_textblock(content)

    @property
    def eligibility(self):
        """
        Get the study Elibility Struct
        :rtype: StudyEligibility
        """
        if self._eligibility is None:
            self._eligibility = StudyEligibility.from_dict(glom(self._data, 'eligibility'))
        return self._eligibility

    @property
    def oversight_info(self):
        """
        Get the oversight information
        :rtype: OversightInfo
        """
        if self._oversight_info is None:
            self._oversight_info = OversightInfo.from_dict(glom(self._data, 'oversight_info'))
        return self._oversight_info

    @property
    def countries(self):
        return glom(self._data, 'location_countries.country', default=[])

    @property
    def keywords(self):
        """
        Get the Study Keywords
        :rtype: list(str)
        """
        return glom(self._data, 'keyword', default=[])

    @property
    def study_people(self):
        """
        Return all the Contacts associated with the study, intended for bundling
        :rtype: list(StudyContact)
        """
        if self._people is None:
            # If none defined, load the core people
            self.get_people()
        return self._people

    @property
    def interventions(self):
        """
        Get the Interventions
        :rtype: list(StudyIntervention)
        """
        if self._interventions is None:
            self._add_interventions()
        return self._interventions

    @property
    def responsible_parties(self):
        if self._responsible_parties is None:
            self.add_responsible_parties()
        return self._responsible_parties

    @property
    def sponsor(self):
        return self._data['sponsors']['lead_sponsor']

    @property
    def collaborators(self):
        return self._data['sponsors'].get('collaborator', [])

    @property
    def nct_id(self):
        return glom(self._data, 'id_info.nct_id')

    @property
    def study_id(self):
        return glom(self._data, 'id_info.org_study_id')

    @property
    def secondary_id(self):
        return glom(self._data, 'id_info.secondary_id', default=[])

    @property
    def locations(self):
        if self._locations is None:
            self.add_locations()
        return self._locations

    @property
    def facilities(self):
        return self._facilities if self._facilities else []

    @property
    def arms(self):
        if self._arms is None:
            self._add_arms()
        return self._arms

    def add_outcomes(self):
        """
        Add the study outcomes
        :return:
        """
        study_outcomes = StudyOutcomes()
        for outcome_type in ('primary', 'secondary', 'other'):
            for protocol_outcome in glom(self._data, '{}_outcome'.format(outcome_type), default=[]):
                study_outcomes.add_outcome(outcome_type, protocol_outcome)
        self._outcomes = study_outcomes

    def add_study_trail(self):
        """
        Add the study trail
        """
        trail = StudyTrail(study_first_submitted=glom(self._data, 'study_first_submitted', default=None),
                           study_first_submitted_qc=glom(self._data, 'study_first_submitted_qc', default=None),
                           study_first_posted=glom(self._data, 'study_first_posted', default=None),
                           last_update_submitted=glom(self._data, 'last_update_submitted', default=None),
                           last_update_submitted_qc=glom(self._data, 'last_update_submitted_qc', default=None),
                           last_update_posted=glom(self._data, 'last_update_posted', default=None),
                           results_first_submitted=glom(self._data, 'results_first_submitted', default=None),
                           results_first_submitted_qc=glom(self._data, 'results_first_submitted_qc', default=None),
                           results_first_posted=glom(self._data, 'results_first_posted', default=None),
                           disposition_first_submitted=glom(self._data,
                                                                 'disposition_first_submitted', default=None),
                           disposition_first_submitted_qc=glom(self._data,
                                                                    'disposition_first_submitted_qc', default=None),
                           disposition_first_posted=glom(self._data, 'disposition_first_posted', default=None))
        self._trail = trail

    def get_arm_by_label(self, arm_label):
        """
        Get the arm
        :param str arm_label: Label for the arm
        :return:
        """
        for arm in self.arms:
            if arm.arm_group_label == arm_label:
                return arm
        return None

    def _add_interventions(self):
        """
        Add the interventions
        :return:
        """
        self._interventions = []
        for inv_spec in glom(self._data, 'intervention', default=[]):
            self._interventions.append(StudyIntervention(**inv_spec))

    def _add_arms(self):
        """
        Add the arm_groups
        :rtype: list(StudyArm)
        :return:
        """
        self._arms = []
        for arm_spec in glom(self._data, 'arm_group', default=[]):
            self._arms.append(StudyArm(**arm_spec))

    def _add_responsible_party(self, responsible_party):
        """
        Add a responsible party
        :return:
        """
        if self._responsible_parties is None:
            self._responsible_parties = []
        rp = ResponsibleParty.from_dict(responsible_party)
        self._responsible_parties.append(rp)
        return rp

    def _add_facility(self, facility_data):
        """
        Add a facility
        :return:
        """
        facility = Facility(**facility_data)
        if not facility in self._facilities:
            self._facilities.append(facility)
        return facility

    def _add_location(self, location_data):
        """
        Add a location
        :return:
        """
        location = Location(**location_data)
        if self._locations is None:
            self._locations = []
        if not location.investigator in self.study_people:
            self._people.append(location.investigator)
        if not location.contact:
            self._people.append(location.contact)
        if not location.contact_backup:
            self._people.append(location.contact_backup)
        self._locations.append(location)

    def add_responsible_parties(self):
        """
        Add the reponsible_parties
        :return:
        """
        self._add_responsible_party(glom(self._data, 'responsible_party', default={}))

    def add_locations(self):
        """
        Add the locations
        clinical_study.location
        :return:
        """
        for location in glom(self._data, 'location', default=[]):
            self._add_location(location)

    def _add_person(self, context, contact):
        """
        Add a person to the people collection
        :param context:
        :param contact:
        :return:
        """
        # Munge to a list
        if not isinstance(contact, list):
            _contact = [contact]
        else:
            _contact = contact
        for _overall in _contact:
            _overall.update(dict(context=context))
            if context in ('location.investigator',
                           'clinical_study.overall_official'):
                self._people.append(Investigator(**_overall))
            elif context in ('location.contact', 'location.contact_backup',
                             'clinical_study.overall_contact',
                             'clinical_study.overall_contact_backup'):
                self._people.append(Contact(**_overall))

    def get_people(self):
        """
        Get the people involved (at the study level)
        contact_struct -> location_struct.contact, location_struct.contact_backup, clinical_study.overall_contact,
          clinical_study.overall_contact_backup
        investigator_struct -> location_struct.investigator, clinical_study.overall_official
        :return:
        """
        if not self._people:
            self._people = []
            # Overall - children
            for contact in ('overall_official', 'overall_contact', 'overall_contact_backup'):
                overall = glom(self._data, contact, default=None)
                if overall:
                    self._add_person('clinical_study.{}'.format(contact), overall)

    def mesh_terms(self):
        """
        Return the assigned MeSH terms
        :return:
        """
        return glom(self._data, 'condition_browse.mesh_term', default=[])

    def conditions(self):
        """
        Return the assigned Conditions
        :return:
        """
        return glom(self._data, 'condition', default=[])

    @classmethod
    def from_nctid(cls, nct_id):
        """
        Create a Study Using the NCT ID
        :param str nct_id: the NCT ID
        :rtype: ClinicalStudy
        :return:
        """
        schema = get_schema()
        content = get_study(nct_id)
        return cls(schema.to_dict(content))
