"""
Functions to construct DataCrates from paths
"""

from collections import defaultdict
from itertools import zip_longest

from ...core import DataCrate
from ..read import read


def build(path, mode=None):
    """
    reads files and return a collection of datacrates
    modes:
        - lone: each datablock in a separate crate
        - zip: crates with one of each datablock type
        - bunch: all datablocks in a single crate
    """
    modes = ('lone', 'zip', 'bunch')

    if mode is not None and mode not in modes:
        raise ValueError(f'mode can only be one of {modes}')

    datablocks = read(path)
    datablocks_by_type = defaultdict(list)
    for db in datablocks:
        datablocks_by_type[type(db)].append(db)

    if mode is None:
        # check if the lengths are all the same
        if len(set(len(datablocks_by_type.values()))) == 1:
            mode = 'zip'
        else:
            mode = 'lone'

    crates = []
    if mode == 'lone':
        crates.extend([DataCrate(db) for db in datablocks])
    elif mode == 'bunch':
        crates.append(DataCrate(datablocks))
    elif mode == 'zip':
        for dbs in zip_longest(datablocks_by_type.values()):
            crates.append(DataCrate(dbs))
        # TODO: add rescaling?
