import re
from pathlib import Path


def _path(path):
    """
    clean up a path
    """
    return Path(path).expanduser().resolve()
