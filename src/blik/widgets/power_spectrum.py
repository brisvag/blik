from typing import TYPE_CHECKING

import dask.array as da
import numpy as np
from magicgui import magic_factory
from scipy.fft import fftn, fftshift, ifftshift

if TYPE_CHECKING:
    import napari


@magic_factory(
    auto_call=False,
    call_button="Calculate",
)
def power_spectrum(
    image: "napari.layers.Image",
    is_2D_data: bool = False,
) -> "napari.types.LayerDataTuple":
    """
    Power spectrum (log scale) of the image.

    First centers in real space on the origin to remove shift effects.
    """
    axes = (-2, -1) if is_2D_data else None
    raw = da.compute(image.data)[0]
    power_spectrum = np.abs(
        fftshift(fftn(ifftshift(raw, axes=axes), axes=axes), axes=axes)
    )
    return (
        np.log(power_spectrum + 1),
        {"name": f"{image.name} - power spectrum", "scale": image.scale},
        "image",
    )
