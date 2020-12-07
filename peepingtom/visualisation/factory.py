from .peepers import Peeper
from ..io_.read import read


def peep(paths):
    crates = read(paths)
    peeper = Peeper(crates)
    peeper.peep()
    return peeper
