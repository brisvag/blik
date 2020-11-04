from scipy.spatial import cKDTree
import numpy as np
from scipy.ndimage import convolve1d
from scipy.cluster.vq import kmeans2
from scipy.signal.windows import gaussian

def classify(dataset, max_r=50, n_shells=100, n_classes=5, convolve=False, std=5):
    shell_thickness = max_r / n_shells
    binned = []
    for particles in dataset.particles:
        tree = cKDTree(particles.coords)
        adj_matrix = tree.sparse_distance_matrix(tree, max_r).toarray()
        shells = [np.sum((adj_matrix > i * shell_thickness) & (adj_matrix <= (i + 1) * shell_thickness), axis=1)
                for i in range(n_shells)]
        binned.append(np.stack(shells, axis=1).astype(float))
    binned = np.concatenate(binned)
    if convolve:
        binned = convolve1d(binned, gaussian(n_shells//2, std))
    classes = kmeans2(binned, n_classes, iter=100, minit='points')

    return classes
