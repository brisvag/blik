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

    def __init__(self, *, name=None, volume=None, peeper=None, parent=None):
        self._parent = parent
        if self.parent is self:
            if name is None:
                name = token_hex(8)
            self._name = name
            self._peeper = peeper
            self._volume = volume
            self._depictors = []
            self._alchemists = []

    @property
    def parent(self):
        """
        points to the parent in case of a view, or to self otherwise
        """
        return self._parent or self

    @property
    def peeper(self):
        return self.parent._peeper

    @peeper.setter
    def peeper(self, peeper):
        self.parent._peeper = peeper

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
    def depictors(self):
        return self.parent._depictors

    @depictors.setter
    def depictors(self, depictors):
        self.parent._depictors = depictors

    @property
    def alchemists(self):
        return self.parent._alchemists

    @alchemists.setter
    def alchemists(self, alchemists):
        self.parent._alchemists = alchemists

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

    def __name_repr__(self):
        return f'<{self.name}>'

    def __view_repr__(self):
        view = ''
        if self.parent is not self:
            # if type is different, we're just the contents of a multiblock
            if isinstance(self.parent, type(self)):
                view = '-View'
        return view

    def __shape_repr__(self):
        return ''

    def __repr__(self):
        return (f'{type(self).__name__}{self.__view_repr__()}'
                f'{self.__name_repr__()}{self.__shape_repr__()}')

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
