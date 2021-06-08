import re


class ParseError(RuntimeError):
    pass


# a list of commonly used base names for starfiles in regex form
common_name_regexes = (
    r'TS_\d+',
    r'\d+',
)


def guess_name(string, name_regex=None):
    """
    guess an appropriate name based on the input string
    and a list of regexes in order of priority
    """
    regexes = list(common_name_regexes)
    if name_regex is not None:
        regexes.insert(0, name_regex)
    for regex in regexes:
        if match := re.search(regex, str(string)):
            return match.group(0)
    else:
        return None
