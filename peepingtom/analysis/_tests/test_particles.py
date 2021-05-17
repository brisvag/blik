import numpy as np

from peepingtom.datablocks import ParticleBlock
from peepingtom.peeper import Peeper
from peepingtom.analysis import classify_radial_profile, deduplicate_peeper


p = Peeper(ParticleBlock(positions_data=np.stack([np.arange(10)] * 3, axis=1),
                         orientations_data=np.tile(np.identity(3), (10, 1, 1)),
                         properties_data={'a': np.zeros(10)}))


def test_classify_radial_distance():
    centroids, classes = classify_radial_profile(p, mode='d', n_classes=1)
    assert isinstance(centroids, np.ndarray)
    assert len(centroids) == 1
    assert isinstance(classes, np.ndarray)
    assert 'dist_matrix' in p[0].metadata
    assert p['class_radial_centroids'] is not None


def test_classify_radial_orientation():
    centroids, classes = classify_radial_profile(p, mode='o', n_classes=1)
    assert isinstance(centroids, np.ndarray)
    assert len(centroids) == 1
    assert isinstance(classes, np.ndarray)
    assert 'ori_matrix' in p[0].metadata
    assert p['class_radial_centroids'] is not None


def test_deduplicate_peeper():
    p_ded1 = deduplicate_peeper(p, exclusion_radius=20)
    p_ded2 = deduplicate_peeper(p, exclusion_radius=0)
    assert p_ded1[0].n == 1
    assert p_ded2[0].n == p[0].n
