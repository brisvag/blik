from collections import defaultdict
from secrets import token_hex
from math import log10, ceil

import numpy as np

from ..datablocks import DataBlock, ParticleBlock, ImageBlock
from ..utils import DispatchList, listify
from ..gui import Viewer


class DataSet:
    """
    A container for a collection of DataBlocks
    """
    def __init__(self, datablocks=(), name=None, view_of=None):
        self._view_of = view_of
        if name is None:
            name = token_hex(8)
        self._viewer = None
        self._data = []
        self._name = name
        self._extend(datablocks)

    # DATA
    @property
    def view_of(self):
        return self._view_of or self

    @property
    def name(self):
        return self.view_of._name

    @property
    def datablocks(self):
        return DispatchList(self._data)

    @property
    def volumes(self):
        volumes = self._nested()
        volumes.pop('BLIK_OMNI', None)
        return volumes

    @property
    def omni(self):
        return self._nested().get('BLIK_OMNI', DispatchList())

    def is_view(self):
        return self.view_of is not self

    def copy(self, new_name=None):
        cp = DataSet(self, name=new_name)
        return cp

    def _sanitize(self, iterable, deduplicate=True):
        listified = listify(iterable)
        for item in listified:
            if not isinstance(item, DataBlock):
                raise TypeError(f'DataSet can only hold DataBlock objects, not "{type(item).__name__}"')
        if deduplicate:
            deduplicated = []
            while listified:
                el = listified.pop()
                if el in self or el in deduplicated:
                    pass
                else:
                    deduplicated.append(el)
            listified = deduplicated
        return listified

    def _hook_onto_datablocks(self, datablocks):
        if not self.is_view():
            for db in datablocks:
                db.datasets.add(self)

    def _nested(self, as_list=False):
        nested = defaultdict(list)
        i = 0
        length = len(self._data) or 1  # avoid math domain error
        pad = ceil(log10(length))
        for el in self._data:
            if el.volume is None:
                nested[f'None_{i:0{pad}}'].append(el)
                i += 1
            else:
                nested[el.volume].append(el)
        if as_list:
            return list(nested.values())
        return dict(nested)

    def _filter_types(self, block_types):
        """
        return a view containing only the chosen block types
        """
        block_types = tuple(listify(block_types))

        def right_type(item):
            return isinstance(item, block_types)
        filtered = filter(lambda x: isinstance(x, block_types), self)
        return DispatchList(filtered)

    @property
    def particles(self, flatten=False):
        return self._filter_types(ParticleBlock)

    @property
    def images(self, flatten=False):
        return self._filter_types(ImageBlock)

    def __view__(self, *args, **kwargs):
        return DataSet(*args, view_of=self.view_of, **kwargs)

    def __getitems__(self, key):
        out = []
        if isinstance(key, int):
            out.append(self._data[key])
        elif isinstance(key, slice):
            out.extend(self._data[key])
        elif isinstance(key, str):
            for vol, dbs in self.volumes.items():
                if vol == key:
                    out.extend(dbs)
                    break
            else:
                for db in self:
                    if db.name == key:
                        out.append(db)
                        break
        elif isinstance(key, (list, tuple, np.ndarray)):
            if all(isinstance(i, bool) for i in key):
                out.extend(list(np.array(self._data)[key]))
            else:
                for k in key:
                    out.extend(self.__locitem__(k))
        if not out:
            raise KeyError(f'{key}')
        return out

    def __getitem__(self, key):
        items = self.__getitems__(key)
        if len(items) == 1 and isinstance(key, (str, int)):
            # to enforce getting a dataset, you can simply use a 1-tuple as key
            return items[0]
        return self.__view__(items)

    def find_datablocks(self, name=None, volume=None, type=None):
        if name is volume is type is None:
            raise ValueError('at least one of "name", "volume" or "type" must be provided')
        if type is None:
            type = DataBlock
        dbs = self._filter_types(type)
        if name is not None:
            dbs = [db for db in dbs if name in db.name]
        if volume:
            dbs = [db for db in dbs if volume in db.volume]
        if not dbs:
            raise ValueError(f'no datablock corresponds to {name=}, {volume=} and {type=}')
        else:
            return DispatchList(dbs)

    def __iter__(self):
        yield from self._data

    def __contains__(self, item):
        return item in self._data

    def __len__(self):
        return len(self._data)

    def append(self, item):
        self.extend(item)

    def _extend(self, items):
        """
        must be called by init to extend, otherwise views fail
        """
        items = self._sanitize(items)
        self._hook_onto_datablocks(items)
        self._data.extend(items)
        self._data.sort(key=lambda x: x.name)
        if self._viewer is not None:
            self.viewer.update_blik_widget()

    def extend(self, items):
        if self.is_view():
            raise TypeError('DataSet view is immutable')
        self._extend(items)

    def remove(self, item):
        self._data.remove(item)

    def __add__(self, other):
        if isinstance(other, (DataSet, list)):
            return DataSet(self._data + self._sanitize(other))
        else:
            return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, (DataSet, list)):
            self.extend(other)
            return self
        else:
            return NotImplemented

    # REPRESENTATION
    def __shape_repr__(self):
        return f'({len(self._nested())}, {len(self.datablocks)})'

    def __name_repr__(self):
        return f'<{self.name}>'

    def __view_repr__(self):
        view = ''
        if self.is_view():
            view = '-View'
        return view

    def __base_repr__(self):
        return (f'{type(self).__name__}{self.__view_repr__()}'
                f'{self.__name_repr__()}{self.__shape_repr__()}')

    def __pretty_repr__(self, mode):
        modes = ('base', 'flat_compact', 'flat', 'nested_compact', 'nested', 'full')
        if mode not in modes:
            raise ValueError(f'available modes are {", ".join(modes)}; got "{mode}"')
        if mode == 'base':
            return self.__base_repr__()
        contents = []
        for volume, dbs in self._nested().items():
            if mode in ('flat_compact', 'flat'):
                vol_rep = f'{volume}({len(dbs)})'
            else:
                vol_rep = []
                vol_contents = [f'{db.__short_repr__()}' for db in dbs]
                if mode in ('nested_compact', 'nested') and len(vol_contents) > 7:
                    vol_contents = vol_contents[:3] + ['[...]'] + vol_contents[-3:]
                vol_contents_repr = '\n        '.join(vol_contents)
                vol_rep = f'{volume}({len(dbs)}):\n        {vol_contents_repr}'
            contents.append(vol_rep)
        if mode in ('flat_compact', 'nested_compact') and len(contents) > 7:
            contents = contents[:3] + ['[...]'] + contents[-3:]
        contents_rep = '\n    '.join(contents)

        return f'{self.__base_repr__()}:\n    {contents_rep}'

    def __repr__(self):
        return self.__pretty_repr__('nested_compact')

    def pprint(self, mode='full'):
        print(self.__pretty_repr__(mode))

    # VISUALISATION
    @property
    def viewer(self):
        if self.view_of._viewer is None:
            self.view_of._viewer = Viewer(self)
        return self.view_of._viewer

    def show(self, **kwargs):
        self.viewer.show(**kwargs)
        return self.viewer

    @property
    def shown(self):
        return self.viewer.shown

    @property
    def depictors(self):
        return DispatchList(dep for db in self for dep in db.depictors)

    @property
    def napari_layers(self):
        layers = DispatchList()
        for dep in self.depictors:
            layers.extend(getattr(dep, 'layers', []))
        return layers

    def purge_gui(self):
        for dep in self.depictors:
            dep.purge()

    def purge_depictors(self):
        for db in self:
            db.depictors = []

    @property
    def napari_viewer(self):
        return self.viewer.napari_viewer

    @property
    def plots(self):
        plots = DispatchList()
        for dep in self.depictors:
            plot = getattr(dep, 'plot', None)
            if plot:
                plots.append(plot)
        return plots

    # IO
    def read(self, paths, **kwargs):
        """
        read paths into datablocks and append them to the datacrates
        """
        from .io_ import read
        self.extend(read(paths, **kwargs))

    def write(self, paths, **kwargs):
        """
        write datablock contents to disk
        """
        from .io_ import write
        write(self, paths, **kwargs)
