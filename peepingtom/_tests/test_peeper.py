import pytest
import numpy as np

from peepingtom.peeper import Peeper
from peepingtom.datablocks import PointBlock, ImageBlock


pb = PointBlock(volume='test')
ib = ImageBlock(np.random.rand(10, 10, 10), volume='test')
peeper = Peeper([pb, ib])


def test_peeper():
    assert len(peeper) == 2
    assert len(peeper.datablocks) == 2
    assert len(peeper.volumes) == 1


def test_sanitize_peeper():
    with pytest.raises(TypeError):
        peeper.append('wrong')


def test_view():
    view = peeper[:1]
    assert len(view) == 1
    assert view._parent is peeper
    with pytest.raises(TypeError):
        view.append(pb)


def test_pprint():
    brep = peeper.__pretty_repr__('base')
    frep = peeper.__pretty_repr__('full')
    assert len(brep.split('\n')) == 1
    assert len(frep.split('\n')) == 4


def test_depict():
    peeper.datablocks.depict()
    assert len(peeper.napari_layers) == 2
