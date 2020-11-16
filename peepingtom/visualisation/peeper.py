"""
main class that interfaces visualization, analysis and data manipulation
"""

import napari

from ..core import DataBlock, ImageBlock, ParticleBlock, PointBlock, LineBlock
from .depictors import ImageDepictor, ParticleDepictor, PointDepictor, LineDepictor


class Peeper:
    """
    collect and display an arbitrary set of images and/or datasets
    expose the datasets to visualization and analysis tools
    """
    def __init__(self, crates, viewer=None):
        self.crates = crates
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
        for b_type, d_type in depictor_type.items():
            if isinstance(datablock, b_type):
                # don't store a reference to it, cause it hooks itself on the datablock
                d_type(datablock, peeper=self)

    @property
    def datablocks(self):
        return [datablock for crate in self.crates for datablock in crate]

    @property
    def depictors(self):
        return [datablock.depictor for datablock in self.datablocks]

    @property
    def depictor_layers(self):
        return [depictor.layers for depictor in self.depictors]

    def _get_datablocks(self, block_type=DataBlock):
        return [datablock for datablock in self.datablocks if isinstance(datablock, block_type)]

    @property
    def particles(self):
        return self._get_datablocks(ParticleBlock)

    def peep(self, viewer=None):
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

        for depictor in self.depictors:
            depictor.draw()

    def hide(self, crates='all'):
        for depictor in self.depictors:
            depictor.hide()

    def update(self):
        for depictor in self.depictors:
            depictor.update()
