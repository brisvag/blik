from napari.layers import Image
from peepingtom.peeper import ImageDepictor

from ...test_data.blocks import imageblock


def test_image_depictor():
    image_depictor = ImageDepictor(imageblock, peeper=None)
    assert image_depictor.datablock is imageblock
    image_depictor.init_layers()
    assert len(image_depictor.layers) == 1
    assert isinstance(image_depictor.layers[0], Image)
