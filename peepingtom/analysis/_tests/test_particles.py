import numpy as np

from peepingtom.datablocks import ParticleBlock
from peepingtom.dataset import DataSet
from peepingtom.analysis import classify_radial_profile, deduplicate_dataset


ds = DataSet(ParticleBlock(np.stack([np.arange(10)] * 3, axis=1), np.zeros((10, 3, 3)), {'a': np.zeros(10)}))


def test_classify_radial_distance():
    centroids, classes = classify_radial_profile(ds, n_classes=1)
    assert isinstance(centroids, np.ndarray)
    assert len(centroids) == 1
    assert isinstance(classes, np.ndarray)
    assert len(classes) == len(ds[0])
    added_props = ['class_radial']
    added_metadata = ['class_radial_centroids', 'class_radial_params']
    assert all([x in ds[0].properties for x in added_props])
    assert all([x in ds[0].metadata for x in added_metadata])


def test_deduplicate_dataset():
    ds_ded1 = deduplicate_dataset(ds, exclusion_radius=20)
    ds_ded2 = deduplicate_dataset(ds, exclusion_radius=0)
    assert len(ds_ded1[0]) == 1
    assert len(ds_ded2[0]) == len(ds[0])
