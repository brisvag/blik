"""
main class that interfaces visualization, analysis and data manipulation
"""

from peepingtom.viewable import Viewable, VolumeViewer


class Peeper(Viewable):
    """
    collect and display an arbitrary set of images and/or datasets
    expose the datasets to visualization and analysis tools
    """
    def __init__(self, data_blocks):
        super().__init__()
        self.volumes = [VolumeViewer(db, parent=self) for db in data_blocks]

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

    def show(self, volumes='all', viewer=None, point_kwargs={}, vector_kwargs={}, image_kwargs={}, stack=True):
        super().show(viewer=viewer)
        if volumes == 'all':
            volumes = self.volumes
        for volume in volumes:
            volume.show(viewer=self.viewer, point_kwargs=point_kwargs,
                        vector_kwargs=vector_kwargs, image_kwargs=image_kwargs)

    def hide(self, volumes='all'):
        if volumes == 'all':
            volumes = self.volumes
        for volume in volumes:
            volume.hide()

    def loop_volumes():

    def update(self):
        for volume in self.volumes:
            volume.update()
