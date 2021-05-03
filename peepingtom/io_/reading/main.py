import re
from collections import defaultdict
from itertools import zip_longest
import logging

from ..utils import _path, ParseError
from ...utils import listify
from .star import read_star
from .mrc import read_mrc
from .em import read_em
from .tbl import read_tbl
from .box import read_box
from .cbox import read_cbox

from ...peeper import Peeper
from ...datablocks import ParticleBlock, ImageBlock


logger = logging.getLogger(__name__)

# a mapping of file extensions to readers, tuple map to tuples (don't forget trailing comma!):
#   - multiple extensions values in the keys use the same readers
#   - multiple readers are called in order from highest to lowers in case previous ones fail
# TODO: put this directly in the readers to make it plug and play?
readers = {
    ('.star',): (read_star,),
    ('.mrc', '.mrcs', '.map'): (read_mrc,),
    ('.em',): (read_em,),
    ('.tbl',): (read_tbl,),
    ('.box',): (read_box,),
    ('.cbox',): (read_cbox,),
}


def read_file(file_path, **kwargs):
    """
    read a single file with the appropriate parser and return a list of datablocks
    """
    for ext, funcs in readers.items():
        if file_path.suffix in ext:
            for func in funcs:
                try:
                    datablocks = listify(func(file_path, **kwargs))
                    return datablocks
                except ParseError:
                    # this will be raised by individual readers when the file can't be read.
                    # Keep trying until all options are exhausted
                    continue
    raise ParseError(f'could not read {file_path}')


def find_files(paths, filters=None, recursive=False, max=None):
    """
    take a path or iterable thereof and find all the contained readable files
    filters: a regex-like strings or iterable thereof used to match filenames
    max: max number of files to read
    """
    # sanitize input
    paths = listify(paths)
    paths = [_path(path) for path in paths]
    filters = listify(filters)

    # extract files
    files = []
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(f'{path} does not exist')

        # find all the readable files, if any
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            basedir = '.'
            if recursive:
                basedir = '**'
            known_formats = [ext for formats in readers for ext in formats]
            for ext in known_formats:
                files.extend(file for file in path.glob(f'{basedir}/*{ext}'))
        if not files:
            raise FileNotFoundError(f'{path} does not contain any files of a know type')

    # filter files if requested
    files = [file for file in files if all(re.search(regex, str(file)) for regex in filters)]

    if max is None:
        max = len(files) + 1
    return files[:max]


def read(paths,
         mode=None,
         name_regex=None,
         pixel_size=None,
         rescale_particles=False,
         filters=None,
         recursive=False,
         strict=False,
         max=None,
         mmap=False,
         lazy=True,
         **kwargs):
    r"""
    Read generic path(s) and construct a Peeper accordingly.

    Peeper and Datablock construction arguments:
        mode: how to arrange DataBlocks into volumes
            - lone: each datablock in a separate volume
            - zip_by_type: one of each datablock type per volume
            - bunch: all datablocks in a single volume
        name_regex: a regex used to infer DataBlock names from paths. For example:
                    'Protein_\d+' will match 'MyProtein_10.star' and 'MyProtein_001.mrc'
                    and name the respective DataBlocks 'Protein_10' and 'Protein_01'
        pixel_size: manually set the pixel size (overrides the one read from file)
        rescale_particles: if particle positions are normalized between 0 and 1, (e.g: Warp template matching),
                           attempt to rescale them based on image sizes
    File reading arguments:
        filters: a regex string or iterable thereof used to select filenames [default: '.*']
        recursive: navigate directories recursively to find files
        strict: if set to true, immediately fail if a matched filename cannot be read by PeepingTom
        max: max number of files to read
    Performance arguments:
        mmap: open file in memory map mode (if possible)
        lazy: read data lazily (if possible)
    """
    # if changing the signature of this function, change the one in `__main__.cli` as well!
    modes = ('lone', 'zip_by_type', 'bunch')

    if mode is not None and mode not in modes:
        raise ValueError(f'mode can only be one of {modes}')

    datablocks = []
    for file in find_files(paths, filters=filters, recursive=recursive, max=max):
        try:
            logger.info(f'attempting to read "{file}"')
            datablocks.extend(read_file(file, name_regex=name_regex, pixel_size=pixel_size,
                                        mmap=mmap, lazy=lazy, **kwargs))
        except ParseError as e:
            logger.info(f'failed to read "{file}": {e}')
            if strict:
                raise
    if not datablocks:
        raise ParseError(f'could not read any data from {paths}')

    datablocks_by_type = defaultdict(list)
    for db in datablocks:
        datablocks_by_type[type(db)].append(db)

    if mode is None:
        # check if there are multiple types and lengths are all the same
        if len(datablocks_by_type) > 1:
            count_per_type = [len(db_type) for db_type in datablocks_by_type.values()]
            if len(set(count_per_type)) == 1:
                mode = 'zip_by_type'
            else:
                mode = 'lone'
        else:
            mode = 'lone'

    if mode == 'lone':
        for db in datablocks:
            db.volume = db.name
    elif mode == 'bunch':
        pass
    elif mode == 'zip_by_type':
        # TODO: this is quite finnicky. We need a smarter way of handling volumes
        for lst in datablocks_by_type.values():
            lst.sort()
        for dbs in zip_longest(*datablocks_by_type.values()):
            particles_to_rescale = []
            image = None
            for db in dbs:
                db.volume = dbs[0].name

                # rescale template matching data from warp. TODO: this will break if particles actually are in that range only
                if isinstance(db, ParticleBlock):
                    particles_to_rescale.append(db)
                elif isinstance(db, ImageBlock):
                    image = db
            # must be "is not None" or it breaks lazy loading
            if image is not None and particles_to_rescale and rescale_particles:
                logger.info('rescaling particles with coordinates between 0 and 1')
                # important to only access `db.data` here, or we mess up the lazy loading of datablocks
                for p in particles_to_rescale:
                    if 0 <= p.positions.data.min() <= p.positions.data.max() <= 1:
                        p.positions.data *= image.data.shape[::-1]

    return Peeper(datablocks)
