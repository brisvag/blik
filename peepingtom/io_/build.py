"""
Functions to construct DataCrates from files
"""

from pathlib import Path
from typing import Union, List
from itertools import zip_longest

from ..core import DataCrate
from .files import mrc_to_imageblock, data_star_to_particleblock


def star_to_crates(star_paths: Union[Path, str, List[str], List[Path]],
                       data_columns: List[str] = [], mode='relion') -> List[DataCrate]:
    """
    Reads an arbitrary number of _data.star type STAR files into a list of DataCrate objects

    Parameters
    ----------
    star_path : Path-like or list of Path-like objects containing file paths for *_data.star type STAR files
    data_columns :
    mode : string containing valid mode for *_data.star type STAR files

    Returns list of DataCrate objects
    -------

    """
    particles = data_star_to_particleblock(star_paths=star_paths, data_columns=data_columns, mode=mode)
    crates = [DataCrate(particle) for particle in particles]
    return crates


def mrc_to_crates(image_paths: Union[Path, str, List[str], List[Path]]) -> List[DataCrate]:
    """
    Reads an arbitrary number of MRC2014 format image files into a list of DataCrate objects

    Parameters
    ----------
    image_paths : Path-like or list of Path-like objects containing file paths for MRC2014 format image files

    Returns list of DataCrate objects
    -------

    """
    return [DataCrate(image) for image in mrc_to_imageblock(image_paths)]


def zip_mrc_star_to_crates(image_paths, star_paths):
    image_crates = mrc_to_crates(image_paths)
    particle_crates = star_to_crates(star_paths)
    output = []
    for image_crate, particle_crate in zip_longest(image_crates, particle_crates, []):
        output.append(image_crate + particle_crate)
