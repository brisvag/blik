from math import ceil

from seaborn import color_palette

from ....analysis.particles import classify_radial_profile as crp
from ....core import ParticleBlock


def classify_radial_profile(peeper, n_classes=5, class_tag='class_radial', **kwargs):
    centroids, classes = crp(peeper._get_datablocks(ParticleBlock),
                             n_classes=n_classes, class_tag=class_tag, **kwargs)
    # color points
    colors = color_palette('colorblind', n_colors=n_classes)
    for d in peeper.depictors:
        d.point_layer.face_color = class_tag
        d.point_layer.face_color_cycle = [list(x) for x in colors]
    # plot centroids
    centroids_dist = []
    centroids_ori = []
    for centr in centroids:
        half = (len(centr) // 2)
        dist = centr[:half - 1]
        ori = centr[half:]
        centroids_dist.append(dist)
        centroids_ori.append(ori)
    # colors to 255 format:
    colors255 = []
    for color in colors:
        colors255.append(tuple(ceil(c*255) for c in color))
    class_names = [f'class{i}' for i in range(n_classes)]
    peeper.add_plot(centroids_dist, colors255, class_names, f'{class_tag}_dist', show=False)
    peeper.add_plot(centroids_ori, colors255, class_names, f'{class_tag}_ori')
