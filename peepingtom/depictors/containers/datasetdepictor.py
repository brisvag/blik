"""
main class that interfaces visualization, analysis and data manipulation
"""

from pathlib import Path

import napari
import pyqtgraph as pg

from ...core import DataSet, DataCrate, DataBlock, ImageBlock, ParticleBlock, PointBlock, LineBlock
from ..depictors import ImageDepictor, ParticleDepictor, PointDepictor, LineDepictor
from ...utils import listify, wrapper_method, distinct_colors, faded_grey
from ...io_ import read, write
from ...analysis import classify_radial_profile, deduplicate_dataset


class DataSetDepictor:
    def __init__(self, dataset, viewers=None):
        if viewers is None:
            viewers = []
        self.viewers = viewers
        self.dataset = dataset

    def show(self, viewer_idx=0):
        self._init_viewer(viewer_idx)
        self.depictors.draw()

    def hide(self):
        self.depictors.hide()

    def update(self):
        self.depictors.update()

    def add_plot(self, arrays, colors, names=None, title=None, legend=True, show=True):
        if names is None:
            names = [f'data_{i}' for i in range(arrays)]
        plot_widget = self.plots.addPlot(title=title)
        if legend:
            plot_widget.addLegend()
        for data, color, name in zip(arrays, colors, names):
            plot_widget.plot(data, pen=color, name=name)
        if show:
            self.show_plots()

    def show_plots(self):
        if not self._plots_widget:
            self._plots_widget = self.viewer.window.add_dock_widget(self.plots)
        self._plots_widget.show()

    def hide_plots(self):
        self._plots_widget.hide()

    def read(self, paths, **kwargs):
        """
        read paths into datablocks and append them to the datacrates
        """
        self.extend(read(paths, **kwargs))

    def write(self, paths, **kwargs):
        """
        write datablock contents to disk
        """
        write(self.datablocks, paths, **kwargs)

#    @wrapper_method(classify_radial_profile)
    def classify_radial_profile(self, *args, **kwargs):
        centroids, _ = classify_radial_profile(self, *args, **kwargs)
        colors = distinct_colors[:kwargs['n_classes']]
        if kwargs['if_properties'] is not None:
            colors.append(faded_grey)
        for d in self.depictors:
            if d is not None:
                d.point_layer.face_color = kwargs['class_tag']
                d.point_layer.face_color_cycle = [list(x) for x in colors]
        if kwargs['if_properties'] is not None:
            colors.pop()
        class_names = [f'class{i}' for i in range(kwargs['n_classes'])]
        self.add_plot(centroids, colors, class_names, f'{kwargs["class_tag"]}')

#    @wrapper_method(deduplicate_dataset)
    def deduplicate(self, *args, **kwargs):
        deduplicate_dataset(self.blocks, *args, **kwargs)


def peep(objects, force_mode=None, **kwargs):
    """
    load datablock(s), datacrate(s), or path(s) into a Peeper object and display them in napari
    """
    objects = listify(objects)
    if all(isinstance(el, (str, Path)) for el in objects):
        peeper = Peeper(read(objects, mode=force_mode, **kwargs))
    elif all(isinstance(el, DataCrate) for el in objects):
        peeper = Peeper(objects)
    elif all(isinstance(el, DataBlock) for el in objects):
        peeper = Peeper([DataCrate(el) for el in objects])
    elif isinstance(objects[0], Peeper):
        peeper = peeper
    peeper.peep()
    return peeper
