import pytest

from blik.utils import DispatchList


def test_dispatch_list():
    lst = ['test']
    dl = DispatchList(lst)
    assert dl.upper()._data == ['TEST']
    assert 'test' in dl
    dl[0] = 'test2'
    assert dl[0] == 'test2'
    dl2 = DispatchList([dl])
    assert dl2.flatten()[0] == 'test2'
    assert dl.disp[0]._data == ['t']
    with pytest.raises(AttributeError):
        dl.nope
    dl.append('test3')
    assert 'test3' in dl
    dl[-1:] == ['test3']
