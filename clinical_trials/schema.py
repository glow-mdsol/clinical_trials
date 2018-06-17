import os
import sys

import xmlschema

SCHEMA_LOCATION = "https://clinicaltrials.gov/ct2/html/images/info/public.xsd"


def get_schema():
    """
    Get the schema
    :rtype: xmlschema.XMLSchema
    :return:
    """
    schema = xmlschema.XMLSchema(SCHEMA_LOCATION)
    return schema


def get_local_schema():
    """
    Get the schema from a local store
    :rtype: xmlschema.XMLSchema
    :return:
    """
    if os.path.exists(os.path.join(sys.prefix, 'config', 'public.xsd')):
        schema = xmlschema.XMLSchema(os.path.join(sys.prefix, 'config', 'public.xsd'))
    elif os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'doc', 'schema', 'public.xsd')):
        schema = xmlschema.XMLSchema(os.path.join(os.path.dirname(__file__), '..', 'doc', 'schema', 'public.xsd'))
    else:
        raise ValueError("Unable to locate schema document")
    return schema
