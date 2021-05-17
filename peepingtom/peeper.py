from collections import defaultdict
from secrets import token_hex

import numpy as np

from .datablocks import DataBlock, ParticleBlock, ImageBlock
from .analysis import classify_radial_profile, deduplicate_peeper
from .utils import DispatchList, inherit_signature, listify
from .gui import Viewer


class Peeper:
    """
    A container for a collection of DataBlocks
    """
    def __init__(self, datablocks=(), name=None, parent=None):
        self._parent = parent
        if name is None:
            name = token_hex(8)
        self._name = name
        self._data = []
        self._extend(datablocks)
        self._viewer = None

    # DATA
    @property
    def parent(self):
        return self._parent or self

    @property
    def name(self):
        return self.parent._name

    @property
    def datablocks(self):
        return DispatchList(self._data)

    @property
    def volumes(self):
        volumes = self._nested()
        volumes.pop('PT_OMNI', None)
        return volumes

    @property
    def omni(self):
        return self._nested().get('PT_OMNI', DispatchList())

    @property
    def ndim(self):
        ndims = [getattr(db, 'ndim', 0) for db in self]
        return max(ndims)

    def isview(self):
        return self.parent is not self

    def _sanitize(self, iterable, deduplicate=True):
        listified = listify(iterable)
        for item in listified:
            if not isinstance(item, DataBlock):
                raise TypeError(f'Peeper can only hold DataBlock objects, not "{type(item).__name__}"')
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
        if not self.isview():
            for db in datablocks:
                # TODO: this is broken. Needs to be fixed, if possible.
                # if db.peeper is not None:
                    # raise RuntimeError('Datablocks cannot be assigned to a new Peeper.')
                db.peeper = self

    def _nested(self, as_list=False):
        sublists = defaultdict(list)
        for el in self._data:
            sublists[el.volume].append(el)
        no_volume = sublists.pop(None, None)
        if no_volume is not None:
            sublists['unassigned'] = no_volume
        if as_list:
            return list(sublists.values())
        return dict(sublists)

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
        return Peeper(*args, parent=self.parent, **kwargs)

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
            # to enforce getting a peeper, you can simply use a 1-tuple as key
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
            return dbs

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

    def extend(self, items):
        if self.isview():
            raise TypeError('Peeper view is immutable')
        self._extend(items)

    def remove(self, item):
        self._data.remove(item)

    # TODO: adding peeper needs some more work. Name clashing and similar issues need to be solved.
    # def __add__(self, other):
        # if isinstance(other, Peeper):
            # return Peeper(self._data + self._sanitize(other))
        # else:
            # return NotImplemented

    # REPRESENTATION
    def __shape_repr__(self):
        return f'({len(self._nested())}, {len(self.datablocks)})'

    def __name_repr__(self):
        return f'<{self.name}>'

    def __base_repr__(self):
        view = ''
        if self.isview():
            view = '-View'
        return f'{type(self).__name__}{view}{self.__name_repr__()}{self.__shape_repr__()}'

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
                vol_contents = [f'{db}' for db in dbs]
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
        return self.__pretty_repr__('flat_compact')

    def pprint(self, mode='full'):
        print(self.__pretty_repr__(mode))

    # VISUALISATION
    @property
    def viewer(self):
        if self.parent._viewer is None:
            self.parent._viewer = Viewer(self)
        return self.parent._viewer

    def show(self, **kwargs):
        self.viewer.show(**kwargs)
        return self.viewer

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

    # ANALYSIS
    @inherit_signature(classify_radial_profile, ignore_args='peeper')
    def classify_radial_profile(self, *args, **kwargs):
        classify_radial_profile(self, *args, **kwargs)
        tag = kwargs.get('class_tag', 'class_radial')
        plot_block = self[f'{tag}_centroids']
        plot_block.init_depictor()
        for p in self.particles:
            p.depictors[0].color_by_categorical_property(tag)

    @inherit_signature(deduplicate_peeper, ignore_args='peeper')
    def deduplicate(self, *args, **kwargs):
        return deduplicate_peeper(self, *args, **kwargs)
