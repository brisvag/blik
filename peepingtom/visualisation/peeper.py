"""
main class that interfaces visualization, analysis and data manipulation
"""

import napari

from ..base import DataBlock, Particles
from .depictor import ParticleDepictor


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
        if isinstance(datablock, Particles):
            # don't store a reference to it, cause it hooks itself on the datablock
            ParticleDepictor(datablock, peeper=self)

    @property
    def depictors(self):
        return [datablock.depictor for crate in self.crates for datablock in crate]

    def _make_stack(self):
        pass
        # if self.images:
            # image_4d = np.stack([img.data for img in self.images])
            # self.stack_image = Image(image_4d, parent=self.parent, name='stack')
        # if self.particles:
            # coords_4d = []
            # vectors_4d = []
            # add_data_4d = {}
            # for idx, prt in enumerate(self.particles):
                # coords = prt.coords.coords
                # vectors = prt.vectors.vectors
                # properties = prt.coords.properties
                # # get the length of coords as (n, 1) shape
                # n_coords = coords.shape[0]
                # shape = (n_coords, 1)
                # # add a leading, incremental coordinate to points that indicates the index
                # # of the 4th dimension in which to show that volume
                # coords_4d.append(np.concatenate([np.ones(shape) * idx, coords], axis=1))
                # # just zeros for vectors, cause they are projection vectors centered on the origin,
                # # otherwise they would traverse the 4th dimension to another 3D slice
                # vectors_4d.append(np.concatenate([np.zeros(shape), vectors], axis=1))
                # # loop through properties to stack them
                # for k, v in properties.items():
                    # if k not in add_data_4d:
                        # add_data_4d[k] = []
                    # add_data_4d[k].append(v)
            # # concatenate in one big array
            # coords_4d = np.concatenate(coords_4d)
            # vectors_4d = np.concatenate(vectors_4d)
            # for k, v in add_data_4d.items():
                # add_data_4d[k] = np.concatenate(v)
            # self.stack_particles = Particles(coords_4d, vectors_4d, parent=self.parent, name='stack', properties=add_data_4d)

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

    def loop_crate():
        pass

    def update(self):
        for crate in self.crate:
            crate.update()
