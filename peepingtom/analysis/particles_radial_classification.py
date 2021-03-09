"""
Analysis functions that operate on collections of data object
"""

from math import ceil

import numpy as np
import scipy.spatial
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian


def distance_matrix(particleblock, use_old=True):
    """
    compute a (n, n) matrix with relative euclidean distances between particle positions
    """
    if use_old and 'dist_matrix' in particleblock.metadata:
        dist_matrix = particleblock.metadata['dist_matrix']
    else:
        positions = particleblock.positions.data
        dist_matrix = scipy.spatial.distance_matrix(positions, positions)
        particleblock.metadata['dist_matrix'] = dist_matrix
    return dist_matrix


def orientation_matrix(particleblock, use_old=True):
    """
    compute a (n, n) matrix with relative cosine distances between particle orientations
    """
    if use_old and 'ori_matrix' in particleblock.metadata:
        ori_matrix = particleblock.metadata['ori_matrix']
    else:
        ori_vectors = particleblock.orientations.oriented_vectors('z').reshape(-1, 3)
        ori_matrix = scipy.spatial.distance.cdist(ori_vectors, ori_vectors, 'cosine')
        particleblock.metadata['ori_matrix'] = ori_matrix
    return ori_matrix


def neighbour_shells(particleblock, n_shells, max_dist):
    """
    assign particles to radial neighbouring shells based on distance
    """
    dist_matrix = distance_matrix(particleblock)

    # calculate shell extents (n_shells + 1 so we can easily use them as ranges)
    shells = np.arange(n_shells + 1).reshape(-1, 1, 1) / n_shells * max_dist
    # > and <=, to exclude self from neighbours
    neighbours = (dist_matrix > shells[:-1]) & (dist_matrix <= shells[1:])
    return neighbours


def radial_distance_profile(particleblock, max_dist, n_shells=50, convolve=True, cv_window_ratio=5,
                            std_ratio=7):
    """
    calculate the radial distance profile of a particleblock
    """
    neighbours = neighbour_shells(particleblock, n_shells, max_dist)

    # sum all the true values to get a count of the neighbour for each index per shell
    neighbour_count = neighbours.sum(axis=1)

    radial_dist_profile = neighbour_count.T

    if convolve:
        cv_window = ceil(n_shells / cv_window_ratio)
        std = cv_window / std_ratio
        radial_dist_profile = convolve1d(radial_dist_profile, gaussian(cv_window, std))

    return radial_dist_profile.astype(np.float64)


def radial_orientation_profile(particleblock, max_dist, n_shells=50, convolve=True, cv_window_ratio=5,
                               std_ratio=7, **kwargs):
    """
    calculate the radial orientation profile of a particleblock
    """
    neighbours = neighbour_shells(particleblock, n_shells, max_dist)
    ori_matrix = orientation_matrix(particleblock, **kwargs)

    # reduce resolution of ori_matrix to reduce memory impact (resolution: 0 to 255)
    ori_matrix = np.around(ori_matrix / 2 * 255).astype(np.uint8)

    # sum all the true values to get a count of the neighbour for each index per shell
    neighbour_count = neighbours.sum(axis=1)
    # TODO: fix empty shells have 0 here
    neighbour_count = np.where(neighbour_count, neighbour_count, 1)   # TODO: any number should be fine?

    neighbour_ori = np.where(neighbours, ori_matrix, 0)
    neighbour_ori_avg = neighbour_ori.sum(axis=1) / neighbour_count

    radial_ori_profile = neighbour_ori_avg.T

    if convolve:
        cv_window = ceil(n_shells / cv_window_ratio)
        std = cv_window / std_ratio
        radial_ori_profile = convolve1d(radial_ori_profile, gaussian(cv_window, std))

    return radial_ori_profile.astype(np.float64) / 255 * 180


def classify_radial_profile(dataset, n_classes=5, mode='d', class_tag='class_radial',
                            max_dist=None, if_properties=None, **kwargs):
    """
    classify particles based on their radial distance and orientation profile
    mode: one of:
        - d: distance
        - o: orientation
    if_properties: passed to ParticleBlock.if_properties() to select starting particles
    """
    modes = {
        'd': radial_distance_profile,
        'o': radial_orientation_profile,
    }
    if mode in modes:
        func = modes[mode]
    else:
        raise ValueError(f'mode can only be one of {[m for m in modes]}, got {mode}')

    original = dataset.particles.flatten()
    particleblocks = original
    indexes = [pb.properties.data.index for pb in particleblocks]
    if if_properties is not None:
        pb_and_idx = particleblocks.if_properties(if_properties, index=True)
        particleblocks, indexes = zip(*pb_and_idx)

    if max_dist is None:
        max_dist = max(pb.positions.data.values.max() for pb in particleblocks)

    data = []
    for pb in particleblocks:
        radial_profile = func(pb, max_dist=max_dist, **kwargs)
        data.append(radial_profile)
    data = np.concatenate(data, axis=0)
    centroids, classes = kmeans2(data, n_classes, minit='points')

    # update classes inplace
    start = 0
    end = 0
    for pb, orig, orig_idx in zip(particleblocks, original, indexes):
        n = pb.positions.data.shape[0]
        end += n
        sliced_classes = classes[start:end]
        orig.properties.data.loc[orig_idx, class_tag] = sliced_classes
        orig.properties.data[class_tag] = orig.properties.data[class_tag].fillna(1000000).astype(int)
        # must trigger update manually because we bypassed __setitem__
        orig.properties.update()
        start += n

        orig.metadata[f'{class_tag}_centroids'] = centroids
        orig.metadata[f'{class_tag}_params'] = {
            'n_classes': n_classes,
            'mode': mode,
            **kwargs,
        }

    return centroids, classes
