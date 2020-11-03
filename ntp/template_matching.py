from tomo_viewer import TomoViewer
from gui import make_property_slider
from scipy.spatial import cKDTree
import numpy as np


class TMViewer(TomoViewer):
    def __init__(self, mrc_path, star_path, max_r=10, *args, **kwargs):
        if any([isinstance(x, list) for x in [mrc_path, star_path]]):
            raise ValueError
        super().__init__(mrc_path, star_path, data_columns=['rlnAutopickFigureOfMerit'], *args, **kwargs)
        self.network = self._calculate_distances(max_r)

    def _calculate_distances(self, max_r):
        coords = self.particles[0].coords
        tree = cKDTree(coords)
        adj_matrix = tree.sparse_distance_matrix(tree, max_r).toarray()
        self.adj = adj_matrix
        edges = np.where(adj_matrix > 0)
        weights = adj_matrix[edges]
        edge1_coords = coords[edges[0]]
        edge2_coords = coords[edges[1]]
        edge2_as_vector_projection = edge2_coords - edge1_coords
        network = np.stack([edge1_coords, edge2_as_vector_projection], axis=1)
        return network


    def show(self, *args, **kwargs):
        v = super().show(*args, **kwargs)
        slider = make_property_slider(self.viewer.layers[1], 'rlnAutopickFigureOfMerit')
        self.viewer.window.add_dock_widget(slider)
        self.viewer.add_vectors(self.network)

        return v

    def tmp(self):
        from scipy.ndimage import convolve1d
        from scipy.cluster.vq import kmeans2
        m = self.adj
        j = 20
        shells = [np.sum((m>i*(j/20))&(m<(i*(j/20))+j/20), axis=1) for i in range(j)]
        obs = np.stack(shells, axis=1)
        obs_float = obs.astype(float)
        obs_conv = convolve1d(obs_float, [1,2,3,2,1])
        classes = kmeans2(obs_float, 5, iter=100, minit='points')

        # 10 stands for range of tree matrix
        #good_shells = [np.sum((good_m>i*(10/j))&(good_m<=(i+1*(10/j))), axis=1) for i in range(j)]
