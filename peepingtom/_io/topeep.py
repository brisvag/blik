from read import zip_data_to_blocks
from peepingtom.viewable import VolumeViewer
from peepingtom.peeper import Peeper


def zip2peep(mrc_paths=[], star_paths=[], sort=True, data_columns=None):
    """
    Creates a Peeper with n volumes each containing 1 image and 1 particles
    """
    blocks = zip_data_to_blocks(mrc_paths, star_paths, sort, data_columns)
    return Peeper(blocks)
