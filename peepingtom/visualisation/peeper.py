"""
main class that interfaces visualization, analysis and data manipulation
"""

from .depictor import Depictor, CrateDepictor


class Peeper(Depictor):
    """
    collect and display an arbitrary set of images and/or datasets
    expose the datasets to visualization and analysis tools
    """
    def __init__(self, crates, **kwargs):
        super().__init__(**kwargs)
        self.crates = crates
        self.crate_depictors = [CrateDepictor(crate) for crate in crates]

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

    def peep(self, crate_depictors='all', viewer=None):
        super().peep(viewer=viewer)
        if crate_depictors == 'all':
            crate_depictors = self.crate_depictors
        for crate_depictor in crate_depictors:
            crate_depictor.peep(viewer=self.viewer)

    def hide(self, crate_depictors='all'):
        if crate_depictors == 'all':
            crate_depictors = self.crate_depictors
        for crate_depictor in crate_depictors:
            crate_depictor.hide()

    def loop_crate_depictors():
        pass

    def update(self):
        for crate_depictor in self.crate_depictors:
            crate_depictor.update()
