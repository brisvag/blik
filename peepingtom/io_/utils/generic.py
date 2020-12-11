import re
from pathlib import Path
from collections.abc import Iterable


def _path(path):
    """
    clean up a path
    """
    return Path(path).expanduser().resolve()


# a list of commonly used base names for starfiles in regex form
common_name_regexes = (
    'TS_\d+',
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


def listify(obj):
    """
    transform input into an appropriate list, unless already list-like
    """
    if isinstance(obj, (list, tuple)):
        return obj
    if obj is None:
        return []
    return [obj]
