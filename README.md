Clinical Trials dot Gov Simple Parser
=====================================

This is a simple parser for XML generated by clinicaltrials.gov.  This was started for usage as part of the Boston FHIR Dev Days 

Installation
------------
Using pip

`pip install -e git+https://github.com/glow-mdsol/clinical_trials#egg=glow_mdsol_clinical_trials`

Usage
-----

```python

from clinical_trials import ClinicalStudy

study = ClinicalStudy.from_nctid('NCT02348489')
print(study.study_id)
'NCT02348489'
```

Status
------
Current status of Schema Support

| *Section* | *Status* |
| --------------------- | -------- |
| required_header | [x] |
| id_info | [x] |
| brief_title | [x] |
| acronym | [x] |
| official_title | [x] |
| sponsors | [x] |
| source | [x] |
| oversight_info | [x] |
| brief_summary | partial - textblock needs better processing |
| detailed_description | partial - textblock needs better processing |
| overall_status | [x] |
| last_known_status | [x] |
| why_stopped | [x] |
| start_date | [x] |
| completion_date | [x] |
| primary_completion_date | [x] |
| phase | [x] |
| study_type | [x] |
| has_expanded_access | [x] |
| expanded_access_info | [x] |
| study_design_info | [x] |
| target_duration | [x] |
| primary_outcome | [x] |
| secondary_outcome | [x] |
| other_outcome | [x] |
| number_of_arms | [x] |
| number_of_groups | [x] |
| enrollment | [x] |
| condition | [x] |
| arm_group | [x] |
| intervention | [x] |
| biospec_retention | [x] |
| biospec_descr | [x] |
| eligibility | [x] |
| overall_official | [x] |
| overall_contact | [x] |
| overall_contact_backup | [x] |
| location | [x] |
| location_countries | [x] |
| removed_countries | [x] |
| link | [x] |
| reference | [x] |
| results_reference | [x] |
| verification_date | [x] |
| study_first_submitted | [x] |
| study_first_submitted_qc | [x] |
| study_first_posted | [x] |
| results_first_submitted | [x] |
| results_first_submitted_qc | [x] |
| results_first_posted | [x] |
| disposition_first_submitted | [x] |
| disposition_first_submitted_qc | [x] |
| disposition_first_posted | [x] |
| last_update_submitted | [x] |
| last_update_submitted_qc | [x] |
| last_update_posted | [x] |
| responsible_party | [x] |
| keyword | [x] |
| condition_browse | [x] |
| intervention_browse | [x] |
| patient_data | [x] |
| study_docs | [x] |
| pending_results | [] |
| clinical_results | [] |