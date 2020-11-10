"""
Analysis functions that operate on collections of data object
"""

import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian


def classify(particles, class_tag='classes', max_r=50, n_shells=100, n_classes=5, convolve=True,
             cv_window=20, std=5, inplace=True):
    shell_thickness = max_r / n_shells
    binned = []
    for part in particles:
        tree = cKDTree(part.positions.data)
        adj_matrix = tree.sparse_distance_matrix(tree, max_r).toarray()
        shells = [np.sum((adj_matrix > i * shell_thickness) & (adj_matrix <= (i + 1) * shell_thickness), axis=1)
                for i in range(n_shells)]
        binned.append(np.stack(shells, axis=1).astype(float))
    binned = np.concatenate(binned)
    if convolve:
        binned = convolve1d(binned, gaussian(cv_window, std))
    centroids, classes = kmeans2(binned, n_classes, iter=100, minit='points')

    if inplace:
        start = end = 0
        for part in particles:
            end += part.positions.data.shape[0]
            sliced_classes = classes[start:end]
            part.properties[class_tag] = sliced_classes
            start += part.positions.data.shape[0]

    return centroids, classes
