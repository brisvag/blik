from math import ceil

import numpy as np
from scipy.spatial import cKDTree
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian

from ..peeper import Peeper
from ..core import ParticleBlock
from ..utils import AttributedList, distinct_colors, faded_grey


def deduplicate(collection, exclusion_radius=None):
    if isinstance(collection, Peeper):
        particleblocks = collection._get_datablocks(ParticleBlock)
    elif all(isinstance(pb, ParticleBlock) for pb in collection):
        particleblocks = collection
    else:
        raise ValueError('can only remove duplicates from a peeper or a collection of ParticleBlocks')


    deduplicated = AttributedList()
    for pb in particleblocks:
        kdt = cKDTree(pb.positions.data)
        clusters = kdt.query_ball_point(pb.positions.data, exclusion_radius, n_jobs=-1)
        clusters_sorted = sorted(clusters, key=len, reverse=True)

        duplicates = []
        visited = []
        for cluster in clusters_sorted:
            if len(cluster) == 1:
                break
            duplicates_in_cluster = [el for el in cluster[1:] if el not in visited]
            duplicates.extend(duplicates_in_cluster)
            visited.append(cluster[0])

        duplicates = np.array(sorted(list(set(duplicates)))).astype(int)
        mask = np.ones(pb.n, dtype=bool)
        mask[duplicates] = False

        deduplicated.append(pb[mask])
    return deduplicated
