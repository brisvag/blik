"""
Analysis functions that operate on collections of data object
"""

from multiprocessing import Pool

import numpy as np
from scipy.spatial import distance_matrix
from scipy.spatial import distance
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian


def calculate_distance_matrix(particleblock, use_old=True):
    """
    compute a (n, n) matrix with relative euclidean distances between particle positions
    """
    if use_old and 'dist_matrix' in particleblock.metadata:
        dist_matrix = particleblock.metadata['dist_matrix']
    else:
        positions = particleblock.positions.data
        dist_matrix = distance_matrix(positions, positions)
        particleblock.metadata['dist_matrix'] = dist_matrix
    return dist_matrix


def calculate_orientation_matrix(particleblock, use_old=True):
    """
    compute a (n, n) matrix with relative cosine distances between particle orientations
    """
    if use_old and 'ori_matrix' in particleblock.metadata:
        ori_matrix = particleblock.metadata['ori_matrix']
    else:
        ori_vectors = particleblock.orientations.oriented_vectors('z').reshape(-1, 3)
        ori_matrix = distance.cdist(ori_vectors, ori_vectors, 'cosine')
        particleblock.metadata['ori_matrix'] = ori_matrix
    return ori_matrix


def calculate_radial_profile(particleblock, max_dist, n_shells=100, convolve=True, cv_window=None,
                             std=None, use_old=True, **kwargs):
    """
    calculate the radial profile of distances and orientations of a particleblock
    """
    radial_dist_profile, radial_ori_profile = None, None
    if use_old:
        try:
            radial_dist_profile, radial_ori_profile = particleblock.metadata['radial_profile'][max_dist]
        except KeyError:
            pass
    if radial_dist_profile is None or radial_ori_profile is None:
        shell_width = max_dist / n_shells

        dist_matrix = calculate_distance_matrix(particleblock, **kwargs)
        ori_matrix = calculate_orientation_matrix(particleblock, **kwargs)

    # calculate shell extents (n_shells + 1 so we can easily use them as ranges)
    shells = np.arange(n_shells + 1).reshape(-1, 1, 1) / n_shells * max_dist
    # > and <=, to exclude self from neighbours
    neighbours = (dist_matrix > shells[:-1]) & (dist_matrix <= shells[1:])
    # sum all the true values to get a count of the neighbour for each index per shell
    neighbour_count = neighbours.sum(axis=1)
    neighbour_ori = np.where(neighbours, ori_matrix, 0)
    neighbour_count = np.where(neighbour_count, neighbour_count, 1)   # TODO: any number should be fine?
    # TODO: fix empty shells have 0 here
    neighbour_ori_avg = neighbour_ori.sum(axis=1) / neighbour_count

    radial_dist_profile = neighbour_count.T
    radial_ori_profile = neighbour_ori_avg.T

    if convolve:
        # some "sane" defaults
        if cv_window is None:
            cv_window = n_shells / 5
        if std is None:
            std = cv_window / 7
        radial_dist_profile = convolve1d(radial_dist_profile, gaussian(cv_window, std))
        radial_ori_profile = convolve1d(radial_ori_profile, gaussian(cv_window, std))

    # TODO: make this less ugly
    if 'radial_profile' not in particleblock.metadata:
        particleblock.metadata['radial_profile'] = {}
    particleblock.metadata['radial_profile'][max_dist] = (radial_dist_profile, radial_ori_profile)
    return radial_dist_profile, radial_ori_profile


def classify_radial_profile(particleblocks, n_classes=5, class_tag='class_radial', max_dist=None, **kwargs):
    """
    classify particles based on their radial distance and orientation profile
    """
    if max_dist is None:
        max_dist = max(pb.positions.data.max() for pb in particleblocks)
    data = []
    for pb in particleblocks:
        radial_dist_profile, radial_ori_profile = calculate_radial_profile(pb, max_dist=max_dist, **kwargs)
        dp = radial_dist_profile / np.linalg.norm(radial_dist_profile, np.inf)
        op = radial_ori_profile / np.linalg.norm(radial_ori_profile, np.inf)
        data.append(np.concatenate([dp, op], axis=1))
    data = np.concatenate(data, axis=0)
    centroids, classes = kmeans2(data, n_classes, minit='points')

    start = 0
    end = 0
    for part in particleblocks:
        n = part.positions.data.shape[0]
        end += n
        sliced_classes = classes[start:end]
        part.properties[class_tag] = sliced_classes
        start += n

        part.metadata[f'{class_tag}_centroids'] = centroids
        part.metadata[f'{class_tag}_params'] = {
            'n_classes': n_classes,
            **kwargs,
        }

    return centroids, classes
