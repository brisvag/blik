from pathlib import Path
import starfile

from micrograph import Micrograph


def star_import(starfile_path):
    """
    load data from a .star file and return a ready-to-go Micrograph object
    """
    df = starfile.read(starfile_path)

    split_micrographs = df.groupby('rlnMicrographName')

    micrographs = []
    for name, df in split_micrographs:
        micrographs.append(Micrograph(df, name=Path(name).stem))

    return micrographs
