from abc import ABC
from functools import total_ordering
from secrets import token_hex

from .metablock import MetaBlock
from ...utils import listify


@total_ordering
class DataBlock(ABC, metaclass=MetaBlock):
    """
    Base class for all datablocks.
    """
    _depiction_modes = {}

    def __init__(self, *, name=None, volume=None, datasets=set(), multiblock=None, view_of=None, file_path=''):
        self._multiblock = multiblock
        self._view_of = view_of
        if name is None:
            name = token_hex(8)
        # set even in case of view/multiblock, as fallback
        self._name = name
        self._datasets = datasets
        self._volume = volume
        self._file_path = file_path
        self._depictors = []

    @property
    def view_of(self):
        return self._view_of or self

    @property
    def multiblock(self):
        return self._multiblock or self

    @property
    def parent(self):
        """
        points to the highest authority for this datablock's attributes
        """
        return self.view_of.multiblock

    @property
    def datasets(self):
        return self.parent._datasets

    @property
    def name(self):
        # not settable on purpose, should be immutable
        return self.parent._name

    @property
    def volume(self):
        return self.parent._volume

    @volume.setter
    def volume(self, name):
        self.parent._volume = name

    @property
    def file_path(self):
        return self.parent._file_path

    @file_path.setter
    def file_path(self, path):
        self.parent._file_path = path

    @property
    def depictors(self):
        return self.parent._depictors

    @depictors.setter
    def depictors(self, depictors):
        self.parent._depictors = depictors

    def add_to_same_volume(self, datablocks):
        datablocks = listify(datablocks)
        for db in datablocks:
            db.volume = self.volume
        for dataset in self.datasets:
            dataset.extend(datablocks)

    def __view__(self, **kwargs):
        return type(self)(view_of=self.view_of, **kwargs)

    def is_view(self):
        return self.view_of is not self

    def copy(self, new_name=None):
        from copy import deepcopy
        cp = deepcopy(self)
        if new_name:
            cp.name = new_name
        return cp

    def init_depictor(self, mode='default', new_depictor=False, **kwargs):
        depictor_type = self._depiction_modes.get(mode)
        if depictor_type is None:
            raise ValueError(f'mode must be one of {tuple(self._depiction_modes.keys())}, not "{mode}"')
        if not new_depictor:
            for depictor in self.depictors:
                if isinstance(depictor, depictor_type):
                    depictor.update()
                    return
        self.depictors.append(depictor_type(self, **kwargs))

    def update(self):
        for depictor in self.depictors:
            depictor.update()

    def __name_repr__(self):
        return f'<{self.name}>'

    def __view_repr__(self):
        view = ''
        if self.is_view():
            view = '-View'
        return view

    def __shape_repr__(self):
        return ''

    def __short_repr__(self):
        # needed so this works for lazy multiblocs and simpleblocks
        return (f'{type(self).__name__}{self.__view_repr__()}'
                f'{self.__name_repr__()}{self.__shape_repr__()}')

    def __repr__(self):
        return self.__short_repr__()

    def __lt__(self, other):
        if isinstance(other, type(self)):
            return self.name < other.name
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, type(self)):
            return self.name > other.name
        else:
            return NotImplemented

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and self.file_path == other.file_path
        else:
            return NotImplemented

    def __hash__(self):
        return hash((type(self), self.name, self.file_path))
