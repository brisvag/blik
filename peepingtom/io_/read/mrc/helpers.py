from pathlib import Path
from typing import Union, List

import mrcfile


def data_from_header(*files: Union[List[str, Path], str, Path], attributes: List[str]):
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
            _attributes = {attribute: getattr(mrc.header, attribute) for attribute in attributes}
            data[str(file)] = _attributes
    return data


def nx(*files: Union[List[str, Path], str, Path]):
    data = data_from_header(*files, attributes=['nx'])
    return {name: data[name]['nx'] for name in data.keys()}


def ny(*files: Union[List[str, Path], str, Path]):
    data = data_from_header(*files, attributes=['ny'])
    return {name: data[name['ny']] for name in data.keys()}


def nz(*files: Union[List[str, Path], str, Path]):
    data = data_from_header(*files, attributes=['nz'])
    return {name: data[name]['nz'] for name in data.keys()}


def nxnynz(*files: Union[List[str, Path], str, Path]):
    return data_from_header(*files, attributes=['nx', 'ny', 'nz'])
