from pathlib import Path
from typing import TYPE_CHECKING, List

from magicgui import magic_factory

from ..reader import read_layers

if TYPE_CHECKING:
    import napari


@magic_factory(
    call_button="Read",
    files={"mode": "rm"},
    name_regex={"widget_type": "ListEdit"},
    names={"widget_type": "ListEdit"},
)
def file_reader(
    files: List[Path],
    name_regex: List[str],
    names: List[str],
    as_dask_array: bool = True,
) -> "napari.types.LayerDataTuple":
    """
    Read files with blik.

    name_regex: a regex string. Matching text will be used as name for the piece of data
    names: only load data matching this comma separated list of names
    """
    return read_layers(
        *files, name_regex=name_regex or None, names=names or None, lazy=as_dask_array
    )
