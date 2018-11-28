from six import string_types


def process_eligibility(content):
    """
    Process the eligibility block
    NOTE: does not handle nested criteria (at all)
    :param content:
    :return:
    """
    lines = content.split("\n")
    cleaned = [x.strip() for x in lines]
    stack = []
    contents = dict(inclusion=[], exclusion=[])
    gather = None
    for line in cleaned:
        if "Inclusion Criteria" in line:
            gather = "inclusion"
            continue
        elif "Exclusion Criteria" in line:
            gather = "exclusion"
        elif line == "":
            if stack:
                contents[gather].append(" ".join(stack))
                stack = []
        else:
            stack.append(line)
    return contents


def process_textblock(textblock):
    """
    Deblocks a a text block
    :param str textblock: content of the block
    :return:
    """
    return (" ".join(x.strip() for x in textblock.split("\n") if x)).strip()


def yes_no_enum(content):
    """
    Maps a yes_no_enum to a boolean
    :param str content: content of element
    :return:
    """
    if isinstance(content, string_types):
        return content.strip().lower() == "yes"
    elif content is None:
        return False
    else:
        raise ValueError("Unable to process value of type {0!s}".format(type(content)))
