from pathlib import Path
import re

def _path(path):
    """
    clean up a path
    """
    return Path(path).expanduser().resolve()


def guess_name(thing):
    """
    guess an appropriate name based on the input
    thing: string or stringifiable or list containing such
    """
    name = 'NoName'
    if isinstance(thing, list):
        raise NotImplementedError('no way to guess a name from a list yet')
    elif match := re.search('TS_\d+', str(thing)):
        name = match.group(0)
    return name
