from typing import TYPE_CHECKING

from magicgui import magic_factory
from skimage.filters import butterworth, gaussian
import numpy as np

if TYPE_CHECKING:
    import napari


@magic_factory(
    auto_call=False,
    call_button=True,
    low=dict(widget_type='FloatSlider', min=0, max=1),
    high=dict(widget_type='FloatSlider', min=0, max=1),
)
def bandpass_filter(image: 'napari.layers.Image', low: float = 0.1, high: float = 0.7) -> 'napari.types.LayerDataTuple':
    channel_axis = 0 if image.metadata['stack'] else None
    high_pass = butterworth(np.asarray(image.data), low, high_pass=True, channel_axis=channel_axis)
    low_pass = butterworth(high_pass, high, channel_axis=channel_axis)
    return low_pass, dict(name=f'filtered {image.name}', scale=image.scale), 'image'


@magic_factory(
    auto_call=False,
    call_button=True,
    sigma=dict(widget_type='FloatSlider', min=0, max=10),
)
def gaussian_filter(image: 'napari.layers.Image', sigma: float = 1) -> 'napari.types.LayerDataTuple':
    channel_axis = 0 if image.metadata['stack'] else None
    filtered = gaussian(np.asarray(image.data), sigma=sigma, channel_axis=channel_axis)
    return filtered, dict(name=f'filtered {image.name}', scale=image.scale), 'image'
