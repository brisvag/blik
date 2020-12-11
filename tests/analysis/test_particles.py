import numpy as np

from peepingtom.core.datablocks import ParticleBlock, PointBlock, OrientationBlock, PropertyBlock
from peepingtom.analysis.particles import classify_radial_distance


pt = PointBlock(np.zeros((10, 3)))
ori = OrientationBlock(np.zeros((10, 3, 3)))
prop = PropertyBlock({})


def test_classify_radial_distance():
    p = ParticleBlock(pt, ori, prop)
    centroids, classes = classify_radial_distance([p], n_classes=1, inplace=False)
    assert isinstance(centroids, np.ndarray)
    assert len(centroids) == 1
    assert isinstance(classes, np.ndarray)
    assert len(classes) == len(pt)


def test_classify_radial_distance_inplace():
    p = ParticleBlock(pt, ori, prop)
    classify_radial_distance([p], n_classes=1)
    added_props = ['class_radial', 'class_radial_params']
    assert all([x in p.properties for x in added_props])
