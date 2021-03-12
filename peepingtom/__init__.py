try:
    from ._version import version as __version__
except ImportError:
    __version__ = "not-installed"

from .io_ import read, write
from .functions import peep
from .peeper import Peeper
