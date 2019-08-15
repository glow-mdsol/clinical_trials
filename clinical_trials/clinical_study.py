import os

from glom import glom

from clinical_trials.connector import get_study, get_study_documents
from clinical_trials.helpers import process_textblock, yes_no_enum
from clinical_trials.schema import get_schema, get_local_schema
from clinical_trials.structs import (
    StudyDesignInfo,
    OversightInfo,
    Facility,
    Location,
    ResponsibleParty,
    Contact,
    Investigator,
    StudyEligibility,
    StudyArm,
    StudyIntervention,
    parse_date,
    StudyTrail,
    ExpandedAccessInfo,
    Link,
    EnrolmentStruct,
    StudyOutcomes,
    PatientData,
    Reference,
    StudyDocument, ProvidedDocument)


class ClinicalStudy:
    def __init__(self, data, has_results=False):
        self.has_results = has_results
        self._data = data
        self._people = None
        self._locations = None
        self._responsible_parties = None
        self._oversight_info = None
        self._eligibility = None
        self._arms = None
        self._interventions = None
        self._drug_names = []
        self._trail = None
        self._outcomes = None
        self._cities = None
        self._officials = None
        self._study_documents = None
        self._primary_outcomes = []
        self._facilities = []
        self._provided_docs = None

    @property
    def provided_docs(self):
        if "provided_document_section" in self._data:
            self._provided_docs = [ProvidedDocument.from_dict(x) for x in
                                   glom(self._data, "provided_document_section.provided_document")]
        return self._provided_docs or []

    @property
    def biospec_retention(self):
        return glom(self._data, "biospec_retention", default="")

    @property
    def biospec_description(self):
        content = glom(self._data, "biospec_descr.textblock", default="")
        return process_textblock(content)

    @property
    def number_of_arms(self):
        return int(glom(self._data, "number_of_arms", default=0))

    @property
    def number_of_groups(self):
        return int(glom(self._data, "number_of_groups", default=0))

    @property
    def target_duration(self):
        return glom(self._data, "target_duration", default=None)

    @property
    def study_design(self):
        if glom(self._data, "study_design_info", default=None):
            return StudyDesignInfo.from_dict(glom(self._data, "study_design_info"))

    @property
    def has_study_documents(self):
        return self.study_documents != []

    @property
    def study_documents(self):
        if self._study_documents is None:
            if glom(self._data, "study_docs", default=None):
                self._study_documents = [StudyDocument.from_dict(x) for x in glom(self._data, "study_docs.study_doc")]
            else:
                # get from the website
                self._study_documents = self._get_documents()
        return self._study_documents

    @property
    def has_expanded_access(self):
        return yes_no_enum(glom(self._data, "has_expanded_access", default="No"))

    @property
    def expanded_access_info(self):
        if glom(self._data, "expanded_access_info", default=None):
            return ExpandedAccessInfo.from_dict(
                glom(self._data, "expanded_access_info")
            )

    @property
    def acronym(self):
        return glom(self._data, "acronym", default=None)

    @property
    def references(self):
        if glom(self._data, "reference", default=None):
            return [Reference.from_dict(x) for x in glom(self._data, "reference")]
        return []

    @property
    def results_references(self):
        if glom(self._data, "results_reference", default=None):
            return [
                Reference.from_dict(x) for x in glom(self._data, "results_reference")
            ]
        return []

    @property
    def overall_contact(self):
        if glom(self._data, "overall_contact", default=None):
            return Contact.from_dict(glom(self._data, "overall_contact"))

    @property
    def overall_contact_backup(self):
        if glom(self._data, "overall_contact_backup", default=None):
            return Contact.from_dict(glom(self._data, "overall_contact_backup"))

    @property
    def patient_data(self):
        _patient_data = glom(self._data, "patient_data", default=None)
        if _patient_data:
            return PatientData.from_dict(glom(self._data, "patient_data"))

    @property
    def removed_countries(self):
        return glom(self._data, "removed_countries.country", default=[])

    @property
    def verification_date(self):
        verification_date = glom(self._data, "verification_date")
        return parse_date(verification_date)

    @property
    def outcomes(self):
        """
        Get the study outcomes
        :rtype: clinical_trials.structs.StudyOutcomes
        """
        if self._outcomes is None:
            self.add_outcomes()
        return self._outcomes

    @property
    def enrollment_info(self):
        return EnrolmentStruct.from_dict(glom(self._data, "enrollment"))

    @property
    def completion_date(self):
        return parse_date(glom(self._data, "completion_date"))

    @property
    def primary_completion_date(self):
        return parse_date(glom(self._data, "primary_completion_date"))

    @property
    def links(self):
        return [Link.from_dict(x) for x in glom(self._data, "link", default=[])]

    @property
    def trail(self):
        """
        Get the study trail
        :rtype: clinical_trials.structs.StudyTrail
        """
        if self._trail is None:
            self.add_study_trail()
        return self._trail

    @property
    def phase(self):
        return glom(self._data, "phase", default="N/A")

    @property
    def why_stopped(self):
        # TODO: check for overall_status, if stopped and missing then return UNK or similar
        return glom(self._data, "why_stopped", default="N/A").strip()

    @property
    def last_known_status(self):
        return glom(self._data, "last_known_status", default="")

    @property
    def status(self):
        return glom(self._data, "overall_status", default="")

    @property
    def study_type(self):
        return glom(self._data, "study_type", default="")

    @property
    def brief_summary(self):
        content = glom(self._data, "brief_summary.textblock", default="")
        return process_textblock(content)

    @property
    def detailed_description(self):
        content = glom(self._data, "detailed_description.textblock", default="")
        return process_textblock(content)

    @property
    def eligibility(self):
        """
        Get the study Elibility Struct
        :rtype: clinical_trials.structs.StudyEligibility
        """
        if self._eligibility is None:
            self._eligibility = StudyEligibility.from_dict(
                glom(self._data, "eligibility")
            )
        return self._eligibility

    @property
    def oversight_info(self):
        """
        Get the oversight information
        :rtype: clinical_trials.structs.OversightInfo
        """
        if self._oversight_info is None:
            self._oversight_info = OversightInfo.from_dict(
                glom(self._data, "oversight_info")
            )
        return self._oversight_info

    @property
    def countries(self):
        return glom(self._data, "location_countries.country", default=[])

    @property
    def keywords(self):
        """
        Get the Study Keywords
        :rtype: list(str)
        """
        return glom(self._data, "keyword", default=[])

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
    def source(self):
        return self._data["source"]

    @property
    def sponsor(self):
        return self._data["sponsors"]["lead_sponsor"]

    @property
    def collaborators(self):
        return self._data["sponsors"].get("collaborator", [])

    @property
    def nct_id(self):
        return glom(self._data, "id_info.nct_id")

    @property
    def study_id(self):
        return glom(self._data, "id_info.org_study_id")

    @property
    def secondary_id(self):
        return glom(self._data, "id_info.secondary_id", default=[])

    @property
    def locations(self):
        if self._locations is None:
            self.add_locations()
        return self._locations

    @property
    def facilities(self):
        return [x.facility for x in self.locations]

    @property
    def cities(self):
        if self._cities is None:
            self._cities = []
            for facility in self.facilities:
                if facility.address:
                    if facility.address.city:
                        if facility.address.city not in self._cities:
                            self._cities.append(facility.address.city)
        return self._cities

    @property
    def arms(self):
        if self._arms is None:
            self._add_arms()
        return self._arms

    @property
    def overall_officials(self):
        if self._officials is None:
            self._officials = []
            for official in glom(self._data, "overall_official", default=[]):
                self._officials.append(Investigator.from_dict(official))
        return self._officials

    def add_outcomes(self):
        """
        Add the study outcomes
        :return:
        """
        study_outcomes = StudyOutcomes()
        for outcome_type in ("primary", "secondary", "other"):
            for protocol_outcome in glom(
                    self._data, "{}_outcome".format(outcome_type), default=[]
            ):
                study_outcomes.add_outcome(outcome_type, protocol_outcome)
        self._outcomes = study_outcomes

    def add_study_trail(self):
        """
        Add the study trail
        """
        trail = StudyTrail(
            study_first_submitted=glom(
                self._data, "study_first_submitted", default=None
            ),
            study_first_submitted_qc=glom(
                self._data, "study_first_submitted_qc", default=None
            ),
            study_first_posted=glom(self._data, "study_first_posted", default=None),
            last_update_submitted=glom(
                self._data, "last_update_submitted", default=None
            ),
            last_update_submitted_qc=glom(
                self._data, "last_update_submitted_qc", default=None
            ),
            last_update_posted=glom(self._data, "last_update_posted", default=None),
            results_first_submitted=glom(
                self._data, "results_first_submitted", default=None
            ),
            results_first_submitted_qc=glom(
                self._data, "results_first_submitted_qc", default=None
            ),
            results_first_posted=glom(self._data, "results_first_posted", default=None),
            disposition_first_submitted=glom(
                self._data, "disposition_first_submitted", default=None
            ),
            disposition_first_submitted_qc=glom(
                self._data, "disposition_first_submitted_qc", default=None
            ),
            disposition_first_posted=glom(
                self._data, "disposition_first_posted", default=None
            ),
        )
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

    def _get_documents(self):
        """
        Look for Study Documents
        :return:
        """
        documents = []
        docs = get_study_documents(self.nct_id)
        for doc_type, link in docs.items():
            doc_id = "_".join(link.split("/")[2:])
            document = StudyDocument.from_dict(dict(doc_id=doc_id,
                                                    doc_type=doc_type,
                                                    doc_url=link,
                                                    doc_comment="Retrieved from clinicaltrials.gov manually"))
            documents.append(document)
        return documents

    def _add_interventions(self):
        """
        Add the interventions
        :return:
        """
        self._interventions = []
        for inv_spec in glom(self._data, "intervention", default=[]):
            self._interventions.append(StudyIntervention(**inv_spec))

    def _add_arms(self):
        """
        Add the arm_groups
        :rtype: list(StudyArm)
        :return:
        """
        self._arms = []
        for arm_spec in glom(self._data, "arm_group", default=[]):
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
        if facility not in self._facilities:
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
        self._locations.append(location)

    def add_responsible_parties(self):
        """
        Add the reponsible_parties
        :return:
        """
        self._add_responsible_party(glom(self._data, "responsible_party", default={}))

    def add_locations(self):
        """
        Add the locations
        clinical_study.location
        :return:
        """
        for location in glom(self._data, "location", default=[]):
            self._add_location(location)

    @property
    def study_people(self):
        """
        Get the people involved (at the study level)
        contact_struct -> location_struct.contact, location_struct.contact_backup, clinical_study.overall_contact,
          clinical_study.overall_contact_backup
        investigator_struct -> location_struct.investigator, clinical_study.overall_official
        :return:
        """
        if not self._people:
            self._people = []
            # add the overall_contact
            if self.overall_contact:
                self._people.append(self.overall_contact)
            if self.overall_contact_backup:
                self._people.append(self.overall_contact_backup)
            if self.overall_officials:
                for official in self.overall_officials:
                    self._people.append(official)
            for location in self.locations:
                # load the location people
                if location.investigators:
                    for investigator in location.investigators:
                        if investigator not in self.study_people:
                            self._people.append(investigator)
                if location.contact and location.contact not in self.study_people:
                    self._people.append(location.contact)
                if (
                        location.contact_backup
                        and location.contact_backup not in self.study_people
                ):
                    self._people.append(location.contact_backup)
        return self._people

    @property
    def mesh_terms(self):
        """
        Return the assigned MeSH terms
        :return:
        """
        terms = {}
        for stat in ("condition", "intervention"):
            for term in glom(
                    self._data, "{}_browse.mesh_term".format(stat), default=[]
            ):
                terms.setdefault(stat, []).append(term)
        return terms

    def conditions(self):
        """
        Return the assigned Conditions
        :return:
        """
        return glom(self._data, "condition", default=[])

    @classmethod
    def from_nctid(cls, nct_id, local_schema=False):
        """
        Build a ClinicalStudy representation from a NCT ID (the API will pull the content)
        :param str nct_id: The NCT identifier
        :param bool local_schema: Use the local copy of the public.xsd document
        :rtype: ClinicalStudy
        :return: The parsed Clinical Study representation
        """
        if local_schema:
            schema = get_local_schema()
        else:
            schema = get_schema()
        content = get_study(nct_id)
        has_results = b"Results are available for this study" in content
        return cls(schema.to_dict(content.decode("utf-8")), has_results)

    @classmethod
    def from_file(cls, filename, local_schema=False):
        """
        Build a ClinicalStudy representation from a file
        :param str filename: Path to the XML from clinicaltrials.gov
        :param bool local_schema: Use the local copy of the public.xsd document
        :rtype: ClinicalStudy
        :return: The parsed Clinical Study representation
        """
        if os.path.exists(filename):
            if local_schema:
                schema = get_local_schema()
            else:
                schema = get_schema()
            with open(filename, "rb") as fh:
                content = fh.read()
            has_results = b"Results are available for this study" in content
            return cls(schema.to_dict(content.decode("utf-8")), has_results)
        else:
            raise ValueError("File {} not found".format(filename))

    @classmethod
    def from_content(cls, content, local_schema=False):
        """
        Build a ClinicalStudy representation from a block of content
        :param str content: Byte encoded Content containing XML from clinicaltrials.gov
        :param bool local_schema: Use the local copy of the public.xsd document
        :rtype: ClinicalStudy
        :return: The parsed Clinical Study representation
        """
        if local_schema:
            schema = get_local_schema()
        else:
            schema = get_schema()
        has_results = b"Results are available for this study" in content
        return cls(schema.to_dict(content.decode("utf-8")), has_results)
