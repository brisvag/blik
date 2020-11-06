"""
Analysis functions that operate on collections of data object
"""

import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian

from peepingtom.components.data import Particles

def classify(data_blocks, max_r=50, n_shells=100, n_classes=5, convolve=True, cv_window=20, std=5, rerun=False):
    shell_thickness = max_r / n_shells
    binned = []
    particles = [p for block in data_blocks for p in block if isinstance(p, Particles)]
    for part in particles:
        tree = cKDTree(part.coords)
        adj_matrix = tree.sparse_distance_matrix(tree, max_r).toarray()
        shells = [np.sum((adj_matrix > i * shell_thickness) & (adj_matrix <= (i + 1) * shell_thickness), axis=1)
                for i in range(n_shells)]
        binned.append(np.stack(shells, axis=1).astype(float))
    binned = np.concatenate(binned)
    if convolve:
        binned = convolve1d(binned, gaussian(n_shells//5, std))
    centroids, classes = kmeans2(binned, n_classes, iter=100, minit='points')

    # TODO: slice classes and put them in properties!

    return classes
