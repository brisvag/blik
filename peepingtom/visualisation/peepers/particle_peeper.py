from seaborn import color_palette
from ...io_ import data_star_to_crate
from ...analysis.particles import classify_radial_distance
from ..peeper import Peeper


class ParticlePeeper(Peeper):
    """
    Peeper class for Particles objects
    """
    def __init__(self, star_paths, **kwargs):
        crates = data_star_to_crate(star_paths)
        super().__init__(crates, **kwargs)

    def classify_radial_distance(self, **kwargs):
        n_classes = kwargs.get('n_classes', 5)
        class_tag = kwargs.get('class_tag', 'class_radial')
        colors = [list(x) for x in color_palette('colorblind', n_colors=n_classes)]
        classify_radial_distance(self.particles)
        for d in self.depictors:
            d.point_layer.face_color = class_tag
            d.point_layer.face_color_cycle = colors
