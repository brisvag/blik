from pathlib import Path

from peepingtom.io_.read.tbl import read_tbl

external_table_files = Path() / 'test_data' / 'external' / 'tbl'


def test_read_tbl():
    table_path = external_table_files / 'HIV_15.00Apx.tbl'
    particleblocks = read_tbl(table_path)

    assert len(particleblocks) == 5
    assert sum([block.positions.data.shape[0] for block in particleblocks]) == 27950
