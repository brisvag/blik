from functools import total_ordering
from secrets import token_hex

from ..utils import listify


@total_ordering
class DataBlock:
    """
    Base class for all datablocks.
    """
    _depiction_modes = {}

    def __init__(self, name=None, volume=None, peeper=None, parent=None):
        self._parent = parent
        if name is None and self._parent is None:
            name = token_hex(16)
        self._name = name
        self.depictors = []
        self.alchemists = []
        self._volume = volume
        self.peeper = peeper

    @property
    def parent(self):
        """
        points to the parent in case of a view, or to self otherwise
        """
        return self._parent or self

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

    def add_to_same_volume(self, datablocks):
        datablocks = listify(datablocks)
        self.peeper.extend(datablocks)
        for db in datablocks:
            db.volume = self.volume

    def __view__(self, *args, **kwargs):
        return type(self)(*args, parent=self, **kwargs)

    def copy(self, new_name=None):
        from copy import deepcopy
        cp = deepcopy(self)
        if new_name:
            cp.name = new_name
        return cp

    def depict(self, mode='default', new_depictor=False, **kwargs):
        depictor_type = self._depiction_modes.get(mode)
        if depictor_type is None:
            raise ValueError(f'unknown depiction mode "{mode}"')
        if not new_depictor:
            for depictor in self.depictors:
                if isinstance(depictor, depictor_type):
                    depictor.update()
                    return
        self.depictors.append(depictor_type(self, **kwargs))

    def update(self):
        for depictor in self.depictors:
            depictor.update()
        for alchemist in self.alchemists:
            alchemist.update()

    def __shape_repr__(self):
        return ''

    def __name_repr__(self):
        return f'<{self.name}>'

    def __base_repr__(self):
        view = ''
        if self.parent is not self:
            view = '-View'
        return f'{type(self).__name__}{view}{self.__name_repr__()}{self.__shape_repr__()}'

    def __repr__(self):
        return self.__base_repr__()

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
            return self.name == other.name
        else:
            return NotImplemented

    def __hash__(self):
        return hash(type(self), self.name)
