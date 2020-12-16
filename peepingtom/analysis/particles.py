"""
Analysis functions that operate on collections of data object
"""

import numpy as np
from scipy.spatial import distance_matrix
from scipy.spatial import distance
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian


def calculate_distance_matrix(particleblock, use_old_matrix=True):
    """
    compute a (n, n) matrix with relative euclidean distances between particle positions
    """
    if use_old_matrix and 'dist_matrix' in particleblock.metadata:
        dist_matrix = particleblock.metadata['dist_matrix']
    else:
        positions = particleblock.positions.data
        dist_matrix = distance_matrix(positions, positions)
        particleblock.metadata[f'dist_matrix'] = dist_matrix
    return dist_matrix


def calculate_orientation_matrix(particleblock, use_old_matrix=True):
    """
    compute a (n, n) matrix with relative cosine distances between particle orientations
    """
    if use_old_matrix and 'ori_matrix' in particleblock.metadata:
        ori_matrix = particleblock.metadata['ori_matrix']
    else:
        ori_vectors = particleblock.orientations.oriented_vectors('z').reshape(-1, 3)
        ori_matrix = distance.cdist(ori_vectors, ori_vectors, 'cosine')
        particleblock.metadata[f'ori_matrix'] = ori_matrix
    return ori_matrix


def calculate_radial_profile(particleblocks, n_shells=100, max_dist=None, convolve=True, cv_window=None,
                             std=None, **kwargs):
    """
    calculate the radial profile of distances and orientations of a list of particleblocks
    """
    if max_dist is None:
        max_dist = max(pb.positions.data.max() for pb in particleblocks)
    shell_width = max_dist / n_shells

    for part in particleblocks:
        print(f'####### doing: {part}')
        dist_matrix = calculate_distance_matrix(part, **kwargs)
        ori_matrix = calculate_orientation_matrix(part, **kwargs)
        for i in range(n_shells):
            print(f'shell {i} of {n_shells}')
            inner = i * shell_width
            outer = (i + 1) * shell_width
            neighbours = (dist_matrix > inner) & (dist_matrix <= outer)
            neighbour_count = np.sum(neighbours, axis=1)
            neighbour_ori = np.where(neighbours, ori_matrix, 0)
            neighbour_ori_avg = np.sum(neighbour_ori, axis=1) / neighbour_count

    if convolve:
        # some "sane" defaults
        if cv_window is None:
            cv_window = n_shells / 5
        if std is None:
            std = cv_window / 7
        print('####### convolution')
        radial_dist_profile = convolve1d(neighbour_count, gaussian(cv_window, std))
        radial_ori_profile = convolve1d(neighbour_ori_avg, gaussian(cv_window, std))

    return radial_dist_profile, radial_ori_profile


def classify_radial_profile(particleblocks, n_classes=5, class_tag='class_radial', **kwargs):
    """
    classify particles based on their radial distance and orientation profile
    """
    data = np.concatenate(calculate_radial_profile(particleblocks, **kwargs))
    print('####### classification')
    data = np.nan_to_num(data)
    centroids, classes = kmeans2(data, n_classes, minit='points')

    start = end = 0
    for part in particleblocks:
        end += part.positions.data.shape[0]
        sliced_classes = classes[start:end]
        part.properties[class_tag] = sliced_classes
        start += part.positions.data.shape[0]

        part.metadata[f'{class_tag}_centroids'] = centroids
        part.metadata[f'{class_tag}_params'] = {
            'n_classes': n_classes,
            **kwargs,
        }

    return centroids, classes
