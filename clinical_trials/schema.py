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
