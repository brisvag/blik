class DataBlock:
    """
    Base class for all simple and complex datablocks.
    Provides common methods and easy type inference
    """
    _depiction_modes = {}

    def __init__(self, name=None):
        self._name = name
        self.depictors = []
        self.alchemists = []

    def __newlike__(self, *args, **kwargs):
        # this makes sure that operators get the right output in case
        # _merge or _stack return notimplemented
        if args and args[0] is NotImplemented:
            return NotImplemented
        cls = type(self)
        return cls(*args, **kwargs)

    def depict(self, mode='default', **kwargs):
        depictor_type = self._depiction_modes.get(mode)
        if depictor_type is None:
            raise ValueError(f'unknown depiction mode "{mode}"')
        self.depictors.append(depictor_type(self, **kwargs))

    def update(self):
        for depictor in self.depictors:
            depictor.update()
        for alchemist in self.alchemists:
            alchemist.transform()

    @property
    def name(self):
        return self._name or f'#{hash(self)}'

    @name.setter
    def name(self, value):
        self._name = value

    def __shape_repr__(self):
        return ''

    def __name_repr__(self):
        if self.name is None:
            return ''
        else:
            return f'<{self.name}>'

    def __base_repr__(self):
        return f'{type(self).__name__}{self.__name_repr__()}{self.__shape_repr__()}'

    def __repr__(self):
        return self.__base_repr__()

    def __and__(self, other):
        # avoid circular import
        from ..containers import DataCrate
        if isinstance(other, DataBlock):
            return DataCrate([self, other])
        elif isinstance(other, DataCrate):
            return DataCrate(self) + other
        else:
            return NotImplemented

    def __iand__(self, other):
        return NotImplemented

    @staticmethod
    def _merge_data(datablocks):
        """
        convenience method to merge the data of several datablocks
        of the same type into one, within the same ndimensional space
        used by merge and imerge.
        """
        return NotImplemented

    @staticmethod
    def _stack_data(datablocks):
        """
        convenience method to stack the data of several datablocks into one.
        If dimensionality is the same, add a new dimension; otherwise,
        use the next available dimension for the datablocks with smaller dimensionality
        used by stack and istack.
        """
        return NotImplemented

    def _merge(self, datablocks):
        """
        merge several datablocks and return a `newlike` object
        self is not part of merged objects
        """
        return NotImplemented

    def _stack(self, datablocks):
        """
        stack several datablocks and return a `newlike` object
        self is not part of stacked objects
        """
        return NotImplemented

    def _imerge(self, datablocks):
        """
        like merge, but inplace. Self is part of merged objects.
        """
        return NotImplemented

    def _istack(self, datablocks):
        """
        like stack, but inplace. Self is part of stacked objects.
        """
        return NotImplemented

    def __add__(self, other):
        if isinstance(other, type(self)):
            return self._merge([self, other])
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, type(self)):
            self._imerge([other])
            return self
        else:
            return NotImplemented

    def __or__(self, other):
        if isinstance(other, type(self)):
            return self._stack([self, other])
        else:
            return NotImplemented

    def __ior__(self, other):
        if isinstance(other, type(self)):
            self._istack([other])
            return self
        else:
            return NotImplemented
