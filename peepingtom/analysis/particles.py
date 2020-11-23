"""
Analysis functions that operate on collections of data object
"""

import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian


def classify_radial_distance(particles, class_tag='class_radial', max_r=50, n_shells=100,
                             n_classes=5, convolve=True, cv_window=20, std=5, inplace=True,
                             use_old_matrix=True):
    """
    classify particles based on the number of neighbors in radial shells
    """
    shell_width = max_r / n_shells
    binned = []
    # calculate adjacency matrix or reuse old one
    for part in particles:
        redo = True
        if f'{class_tag}_params' in part.properties:
            old_max_r = part.properties[f'{class_tag}_params']['max_r']
            if max_r <= old_max_r:
                adj_matrix = part.properties[f'{class_tag}_adj_matrix']
                redo = False
        if not use_old_matrix or redo:
            tree = cKDTree(part.positions.data)
            adj_matrix = tree.sparse_distance_matrix(tree, max_r).toarray()
            if inplace:
                part.properties[f'{class_tag}_adj_matrix'] = adj_matrix

        # calculate shells

        shells = [np.sum((adj_matrix > i * shell_width) & (adj_matrix <= (i + 1) * shell_width), axis=1)
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

            part.properties[f'{class_tag}_centroids'] = centroids
            part.properties[f'{class_tag}_params'] = {
                'max_r': max_r
            }

    return centroids, classes
