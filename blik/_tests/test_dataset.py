import pytest
import numpy as np

from blik.dataset import DataSet
from blik.datablocks import PointBlock, ImageBlock


pb = PointBlock(data=(), volume='test')
ib = ImageBlock(data=np.random.rand(10, 10, 10), volume='test')
pb_novolume = PointBlock(data=(), volume=None)
pb_omni = PointBlock(data=(), volume='BLIK_OMNI')
dataset = DataSet([pb, ib, pb_novolume, pb_omni])


def test_dataset():
    assert len(dataset) == 4
    assert len(dataset.datablocks) == 4
    assert len(dataset.volumes) == 2
    assert len(dataset.omni) == 1
    assert len(dataset.images) == 1


def test_sanitize_dataset():
    with pytest.raises(TypeError):
        dataset.append('wrong')


def test_view():
    view = dataset[:1]
    assert len(view) == 1
    assert view._view_of is dataset
    with pytest.raises(TypeError):
        view.append(pb)


def test_pprint():
    brep = dataset.__pretty_repr__('base')
    frep = dataset.__pretty_repr__('full')
    assert len(brep.split('\n')) == 1
    assert len(frep.split('\n')) == 8


def test_depict():
    dataset.datablocks.init_depictor()
    dataset.depictors.depict()
    assert len(dataset.napari_layers) == 4
