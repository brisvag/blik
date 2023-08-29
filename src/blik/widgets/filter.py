from typing import TYPE_CHECKING

import numpy as np
from magicgui import magic_factory
from scipy.signal.windows import gaussian
from skimage.filters import butterworth

if TYPE_CHECKING:
    import napari


@magic_factory(
    auto_call=False,
    call_button=True,
    low={"widget_type": "FloatSlider", "min": 0, "max": 0.5},
    high={"widget_type": "FloatSlider", "min": 0, "max": 0.5},
)
def bandpass_filter(
    image: "napari.layers.Image", low: float = 0.1, high: float = 0.4
) -> "napari.types.LayerDataTuple":
    channel_axis = 0 if image.metadata["stack"] else None
    high_pass = butterworth(
        np.asarray(image.data), low, high_pass=True, channel_axis=channel_axis
    )
    low_pass = butterworth(high_pass, high, channel_axis=channel_axis)
    return low_pass, {"name": f"filtered {image.name}", "scale": image.scale}, "image"


def gaussian_kernel(size, sigma):
    window = gaussian(size, sigma)
    kernel = np.outer(window, window)
    return kernel / kernel.sum()


@magic_factory(
    auto_call=True,
    sigma={"widget_type": "FloatSlider", "min": 0.1, "max": 5, "step": 0.1},
    kernel_size={"widget_type": "Slider", "min": 3, "max": 20},
)
def gaussian_filter(
    image: "napari.layers.Image",
    sigma: float = 1,
    kernel_size: int = 3,
) -> None:
    image.interpolation2d = "custom"
    image.custom_interpolation_kernel_2d = gaussian_kernel(kernel_size, sigma)
