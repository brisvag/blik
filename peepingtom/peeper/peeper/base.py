"""
main class that interfaces visualization, analysis and data manipulation
"""

import napari

from ...core import ImageBlock, ParticleBlock, PointBlock, LineBlock
from ..depictors import ImageDepictor, ParticleDepictor, PointDepictor, LineDepictor
from ...utils import AttributedList
from ...io_ import read, write


class Peeper:
    """
    collect and display an arbitrary set of images and/or datasets
    expose the datasets to visualization and analysis tools
    """
    def __init__(self, crates, viewer=None):
        self.crates = AttributedList(crates)
        self.viewer = viewer
        # initialise depictors
        for crate in crates:
            for datablock in crate:
                self._init_depictor(datablock)

    def _init_depictor(self, datablock):
        depictor_type = {
            ParticleBlock: ParticleDepictor,
            ImageBlock: ImageDepictor,
            PointBlock: PointDepictor,
            LineBlock: LineDepictor,
        }
        try:
            # don't store a reference to it, cause it hooks itself on the datablock
            depictor_type[type(datablock)](datablock, peeper=self)
        except KeyError:
            raise TypeError(f'cannot find a Depictor for datablock of type {type(datablock)}')

    @property
    def datablocks(self):
        return AttributedList(datablock for crate in self.crates for datablock in crate)

    @property
    def depictors(self):
        return self.datablocks.depictor

    @property
    def depictor_layers(self):
        return self.depictors.layers

    def _get_datablocks(self, block_type):
        return AttributedList(datablock for datablock in self.datablocks if isinstance(datablock, block_type))

    def _init_viewer(self, viewer=None):
        # create a new viewer if necessary
        if viewer is not None:
            self.viewer = viewer
        elif self.viewer is None:
            self.viewer = napari.Viewer(ndisplay=3)

        # random check to make sure viewer was not closed
        try:
            self.viewer.window.qt_viewer.actions()
        except RuntimeError:
            self.viewer = napari.Viewer(ndisplay=3)

    def peep(self, viewer=None):
        self._init_viewer(viewer)
        self.depictors.draw()

    def hide(self):
        self.depictors.hide()

    def update(self):
        self.depictors.update()

    def read(self, paths, **kwargs):
        """
        read paths into datablocks and append them to the datacrates
        """
        self.crates.append(read(paths, **kwargs))

    def write(self, paths, **kwargs):
        """
        write datablock contents to disk
        """
        write(self.datablocks, paths, **kwargs)


def peep(paths, force_mode=None, **kwargs):
    """
    load path(s) as DataCrates into a Peeper object and display them in napari
    """
    peeper = Peeper(read(paths, mode=force_mode, **kwargs))
    peeper.peep()
    return peeper
