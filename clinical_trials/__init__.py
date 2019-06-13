import logging

SCHEMA_VERSION = "2019.02.14"

__version__ = "0.3"

logging.basicConfig()
logger = logging.getLogger(__name__)

from .clinical_study import ClinicalStudy
