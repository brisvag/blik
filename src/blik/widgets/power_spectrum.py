from typing import TYPE_CHECKING

import dask.array as da
from magicgui import magic_factory
from scipy.fft import fftn, fftshift

if TYPE_CHECKING:
    import napari


@magic_factory(
    auto_call=False,
    call_button="Calculate",
)
def power_spectrum(
    image: "napari.layers.Image",
) -> "napari.types.LayerDataTuple":
    axes = (1, 2) if image.metadata["stack"] else None
    raw = da.compute(image.data)[0]
    power_spectrum = abs(fftshift(fftn(raw, axes=axes)))
    return (
        power_spectrum,
        {"name": f"{image.name} - power spectrum", "scale": image.scale},
        "image",
    )
