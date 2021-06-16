try:
    from ._version import version as __version__
except ImportError:
    __version__ = "not-installed"

from .io_ import read, write
from .dataset import DataSet
