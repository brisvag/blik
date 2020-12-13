from pathlib import Path

from peepingtom.io_.read.star import read_star

external_star_files = Path() / 'test_data' / 'external' / 'star'


def test_read_relion30_3d():
    star_path = external_star_files / 'HIV_15.00Apx_rln3.0.star'
    particleblocks = read_star(star_path)

    assert(len(particleblocks) == 5)
    assert(sum([block.positions.data.shape[0] for block in particleblocks]) == 27950)


def test_read_relion31_31():
    star_path = external_star_files / 'chemoreceptor_array_7.5Apx_rln3.1.star'
    particleblocks = read_star(star_path)

    assert len(particleblocks) == 100
    assert sum([block.positions.data.shape[0] for block in particleblocks]) == 9089

