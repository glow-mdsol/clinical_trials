import logging

SCHEMA_VERSION = "08/22/2018"

__version__ = "0.1"

logging.basicConfig()
logger = logging.getLogger(__name__)

from .clinical_study import ClinicalStudy
