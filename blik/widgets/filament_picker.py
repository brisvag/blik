from __future__ import annotations

from magicgui import magic_factory
import numpy as np
import napari
from tomogeom.filament.helical_filament import HelicalFilament

from ..reader import read_particles


@magic_factory(
    auto_call=True,
    call_button='Run',
)
def filament_model(source_layer: napari.layers.Points, rise: float = 10, twist: float = 0, radius: float = 0) -> napari.types.LayerDataTuple:
    if source_layer is None:
        return []

    try:
        if not hasattr(filament_model, 'helix'):
            filament_model.helix = HelicalFilament(
                points=source_layer.data,
                rise=rise,
                twist=twist,
                radius=radius,
            )
        else:
            if np.all(source_layer.data != filament_model.helix.points):
                filament_model.helix.points = source_layer.data
            filament_model.helix.rise = rise
            filament_model.helix.twist = twist
            filament_model.helix.radius = radius
    except TypeError:
        return []

    layers = read_particles(filament_model.helix.particles)
    for _, meta, _ in layers:
        meta['scale'] = source_layer.scale
    return layers
