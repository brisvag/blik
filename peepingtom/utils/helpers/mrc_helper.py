from pathlib import Path
from typing import Union, List
import mrcfile

from .iterable_helper import simplify


def data_from_header(*files: Union[List[str, Path], str, Path], attributes: List[str, Path]):
    """

    Parameters
    ----------
    files
    attributes

    Returns dict of format {filename : attributes} for each mrcfile
    -------

    """
    data = {}
    files = [files] if isinstance(files, (str, Path)) else files

    for file in files:
        with mrcfile.open(file, header_only=True, permissive=True) as mrc:
            _attributes = simplify(tuple([getattr(mrc.header, attribute) for attribute in attributes]))
            data[str(file)] = _attributes
    return data


def nx(*files: Union[List[str, Path], str, Path]):
    return simplify(data_from_header(*files, attributes=['nx']))


def ny(*files: Union[List[str, Path], str, Path]):
    return simplify(data_from_header(*files, attributes=['ny']))


def nz(*files: Union[List[str, Path], str, Path]):
    return simplify(data_from_header(*files, attributes=['nz']))


def nxnynz(*files: Union[List[str, Path], str, Path]):
    return simplify(data_from_header(*files, attributes=['nx', 'ny', 'nz']))

