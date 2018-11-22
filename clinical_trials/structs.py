import datetime

from six import string_types

from clinical_trials import logger
from clinical_trials.errors import StudyDefinitionInvalid
from clinical_trials.helpers import process_textblock, process_eligibility, yes_no_enum


def parse_date(field):
    if field is None:
        # not supplied
        return field
    else:
        if isinstance(field, (string_types,)):
            # type variable_date_type
            return VariableDateStruct(date_str=field)
        elif isinstance(field, (dict,)):
            # type variable_date_struct
            return VariableDateStruct(
                date_str=field.get("$"), date_type=field.get("@type")
            )
        else:
            logger.error("Unexpected value: {} {}".format(field, type(field)))


class CTStruct(object):
    REQUIRED = ()

    def is_valid(self):
        for req in self.REQUIRED:
            if getattr(self, req, None) is None:
                raise StudyDefinitionInvalid(
                    "Missing required attribute {} from {}".format(
                        req, self.__class__.__name__
                    )
                )

    @classmethod
    def from_dict(cls, dict_data):
        return cls(**dict_data)


class Outcome(CTStruct):
    """
    <xs:element name="measure" type="xs:string"/>
    <xs:element name="time_frame" type="xs:string" minOccurs="0"/>
    <xs:element name="description" type="xs:string" minOccurs="0"/>
    """

    OUTCOME_TYPE = "N/A"

    def __init__(self, measure=None, time_frame=None, description=None):
        self.outcome_type = self.OUTCOME_TYPE
        self.measure = measure
        self.time_frame = time_frame
        self.description = description


class PrimaryOutcome(Outcome):
    OUTCOME_TYPE = "PRIMARY"


class SecondaryOutcome(Outcome):
    OUTCOME_TYPE = "SECONDARY"


class OtherOutcome(Outcome):
    OUTCOME_TYPE = "OTHER"


class Sponsor(CTStruct):
    """
    <xs:element name="agency" type="xs:string"/>
    <xs:element name="agency_class" type="agency_class_enum" minOccurs="0"/>
    """

    def __init__(self, agency=None, agency_class=None):
        self.agency = agency
        self.agency_class = agency_class


class StudyDesignInfo(CTStruct):
    """
    <xs:element name="allocation" type="xs:string" minOccurs="0"/>
    <xs:element name="intervention_model" type="xs:string" minOccurs="0"/>
    <xs:element name="intervention_model_description" type="xs:string" minOccurs="0"/>
    <xs:element name="primary_purpose" type="xs:string" minOccurs="0"/>
    <xs:element name="observational_model" type="xs:string" minOccurs="0"/>
    <xs:element name="time_perspective" type="xs:string" minOccurs="0"/>
    <xs:element name="masking" type="xs:string" minOccurs="0"/>
    <xs:element name="masking_description" type="xs:string" minOccurs="0"/>
    """

    def __init__(
        self,
        allocation=None,
        intervention_model=None,
        intervention_model_description=None,
        primary_purpose=None,
        observational_model=None,
        time_perspective=None,
        masking=None,
        masking_description=None,
    ):
        self.allocation = allocation
        self.intervention_model = intervention_model
        self.intervention_model_description = intervention_model_description
        self.primary_purpose = primary_purpose
        self.observational_model = observational_model
        self.time_perspective = time_perspective
        self.masking = masking
        self.masking_description = masking_description


class OversightInfo(CTStruct):
    """
    <xs:element name="has_dmc" type="yes_no_enum" minOccurs="0"/> <!-- data monitoring committee -->
    <xs:element name="is_fda_regulated_drug" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_fda_regulated_device" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_unapproved_device" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_ppsd" type="yes_no_enum" minOccurs="0"/>
    <xs:element name="is_us_export" type="yes_no_enum" minOccurs="0"/>
    """

    def __init__(
        self,
        has_dmc=None,
        is_fda_regulated_drug=None,
        is_fda_regulated_device=None,
        is_unapproved_device=None,
        is_ppsd=None,
        is_us_export=None,
    ):
        """
        Careful with the NULL flavour
        :param has_dmc:
        :param is_fda_regulated_drug:
        :param is_fda_regulated_device:
        :param is_unapproved_device:
        :param is_ppsd:
        :param is_us_export:
        """
        self.has_dmc = has_dmc == "Yes" if not has_dmc is None else None
        self.is_fda_regulated_drug = (
            is_fda_regulated_drug == "Yes"
            if not is_fda_regulated_drug is None
            else None
        )
        self.is_fda_regulated_device = (
            is_fda_regulated_device == "Yes"
            if not is_fda_regulated_device is None
            else None
        )
        self.is_unapproved_device = (
            is_unapproved_device == "Yes" if not is_unapproved_device is None else None
        )
        self.is_ppsd = is_ppsd == "Yes" if not is_ppsd is None else None
        self.is_us_export = is_us_export == "Yes" if not is_us_export is None else None


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

    def __init__(
        self,
        facility=None,
        status=None,
        contact=None,
        contact_backup=None,
        investigator=None,
    ):
        self.facility = Facility.from_dict(facility) if facility is not None else None
        self.status = status
        self.contact = Contact.from_dict(contact) if contact is not None else None
        self.contact_backup = (
            Contact.from_dict(contact_backup) if contact_backup is not None else None
        )
        self.investigators = []
        if investigator is not None:
            for _inv in investigator:
                self.investigators.append(Investigator.from_dict(_inv))


class ResponsibleParty(CTStruct):
    def __init__(
        self,
        name_title=None,
        organization=None,
        responsible_party_type=None,
        investigator_affiliation=None,
        investigator_full_name=None,
        investigator_title=None,
    ):
        self.name_title = name_title
        self.organization = organization
        self.responsible_party_type = responsible_party_type
        self.investigator_affiliation = investigator_affiliation
        self.investigator_full_name = investigator_full_name
        self.investigator_title = investigator_title


class StudyContact(CTStruct):
    def __init__(self, first_name=None, middle_name=None, last_name=None, degrees=None):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.degrees = degrees


class Contact(StudyContact):
    def __init__(
        self,
        first_name=None,
        middle_name=None,
        last_name=None,
        degrees=None,
        phone=None,
        phone_ext=None,
        email=None,
    ):
        super(Contact, self).__init__(first_name, middle_name, last_name, degrees)
        self.phone = phone
        self.phone_ext = phone_ext
        self.email = email


class Investigator(StudyContact):
    def __init__(
        self,
        first_name=None,
        middle_name=None,
        last_name=None,
        degrees=None,
        role=None,
        affiliation=None,
    ):
        super(Investigator, self).__init__(first_name, middle_name, last_name, degrees)
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

    def __init__(
        self,
        study_pop=None,
        sampling_method=None,
        criteria=None,
        gender=None,
        gender_based=None,
        gender_description=None,
        minimum_age=None,
        maximum_age=None,
        healthy_volunteers=None,
    ):
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
        return process_textblock(self._study_pop.get("textblock", ""))

    @property
    def inclusion_criteria(self):
        if self._inclusion_criteria is None:
            processed = process_eligibility(self.criteria)
            self._inclusion_criteria = processed.get("inclusion", [])
        return self._inclusion_criteria

    @property
    def exclusion_criteria(self):
        if self._exclusion_criteria is None:
            processed = process_eligibility(self.criteria)
            self._exclusion_criteria = processed.get("exclusion", [])
        return self._exclusion_criteria

    @property
    def criteria(self):
        return self._criteria.get("textblock")


class StudyArm(CTStruct):
    """
    <xs:element name="arm_group_label" type="xs:string"/>
    <xs:element name="arm_group_type" type="xs:string" minOccurs="0"/>
    <xs:element name="description" type="xs:string" minOccurs="0"/>
    """
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

    def __init__(
        self,
        intervention_type=None,
        intervention_name=None,
        description=None,
        arm_group_label=None,
        other_name=None,
    ):
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
        if self.raw_date_str == "Unknown":
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


class StudyDocument(CTStruct):
    """
    <xs:element name="doc_id" type="xs:string" minOccurs="0"/>
    <xs:element name="doc_type" type="xs:string" minOccurs="0"/>
    <xs:element name="doc_url" type="xs:string" minOccurs="0"/>
    <xs:element name="doc_comment" type="xs:string" minOccurs="0"/>
    """
    def __init__(self, doc_id=None, doc_type=None, doc_url=None, doc_comment=None):
        self.doc_id = doc_id
        self.doc_type = doc_type
        self.doc_url = doc_url
        self.doc_comment = doc_comment


class StudyTrail:
    def __init__(
        self,
        study_first_submitted=None,
        study_first_submitted_qc=None,
        study_first_posted=None,
        last_update_submitted=None,
        last_update_submitted_qc=None,
        last_update_posted=None,
        results_first_submitted=None,
        results_first_submitted_qc=None,
        results_first_posted=None,
        disposition_first_submitted=None,
        disposition_first_submitted_qc=None,
        disposition_first_posted=None,
    ):
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


class ExpandedAccessInfo(CTStruct):
    def __init__(
        self,
        expanded_access_type_individual=None,
        expanded_access_type_intermediate=None,
        expanded_access_type_treatment=None,
    ):
        self.individual = yes_no_enum(expanded_access_type_individual)
        self.intermediate = yes_no_enum(expanded_access_type_intermediate)
        self.treatment = yes_no_enum(expanded_access_type_treatment)


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
        return cls(count=message.get("$", ""), count_type=message.get("@type", ""))


class ProtocolOutcomeStruct(CTStruct):
    """
    protocol_outcome_struct
    """

    def __init__(
        self, measure=None, time_frame=None, description=None, outcome_type=None
    ):
        self.outcome_type = outcome_type
        self.measure = measure
        self.time_frame = time_frame
        self.description = description


class StudyOutcomes:
    """
    results_outcome_struct
    """

    def __init__(self):
        self.primary = []
        self.secondary = []
        self.other = []

    def add_outcome(self, outcome_type, outcome_dict):
        outcome_dict.update(dict(outcome_type=outcome_type))
        if outcome_type == "primary":
            self.primary.append(ProtocolOutcomeStruct.from_dict(outcome_dict))
        elif outcome_type == "secondary":
            self.secondary.append(ProtocolOutcomeStruct.from_dict(outcome_dict))
        else:
            self.other.append(ProtocolOutcomeStruct.from_dict(outcome_dict))


class PatientData(CTStruct):
    """
    patient_data_struct
    """

    def __init__(self, sharing_ipd=None, ipd_description=None):
        self.sharing_ipd = sharing_ipd
        self.ipd_description = ipd_description


class Reference(CTStruct):
    def __init__(self, citation=None, PMID=None):
        self.citation = citation
        self.pubmed_id = PMID
