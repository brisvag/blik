import pytest
import numpy as np

from peepingtom.peeper import Peeper
from peepingtom.datablocks import PointBlock, ImageBlock


pb = PointBlock(data=(), volume='test')
ib = ImageBlock(data=np.random.rand(10, 10, 10), volume='test')
pb_novolume = PointBlock(data=(), volume=None)
pb_omni = PointBlock(data=(), volume='PT_OMNI')
peeper = Peeper([pb, ib, pb_novolume, pb_omni])


def test_peeper():
    assert len(peeper) == 4
    assert len(peeper.datablocks) == 4
    assert len(peeper.volumes) == 2
    assert len(peeper.omni) == 1
    assert len(peeper.images) == 1


def test_sanitize_peeper():
    with pytest.raises(TypeError):
        peeper.append('wrong')


def test_view():
    view = peeper[:1]
    assert len(view) == 1
    assert view._view_of is peeper
    with pytest.raises(TypeError):
        view.append(pb)


def test_pprint():
    brep = peeper.__pretty_repr__('base')
    frep = peeper.__pretty_repr__('full')
    assert len(brep.split('\n')) == 1
    assert len(frep.split('\n')) == 8


def test_depict():
    peeper.datablocks.init_depictor()
    peeper.depictors.depict()
    assert len(peeper.napari_layers) == 4
