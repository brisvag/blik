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


class Peeper(DataSet):
    """
    collect and display an arbitrary set of images and/or datasets
    expose the dataset to visualization and analysis tools
    """
    def __init__(self, data, viewer=None, **kwargs):
        super().__init__(data, **kwargs)
        self.viewer = viewer
        # initialise depictors
        for datablock in self.blocks:
            self._init_depictor(datablock)
        self.plots = pg.GraphicsLayoutWidget()
        self._plots_widget = None

    def __new__(cls, data, **kwargs):
        if isinstance(data, DataSet):
            data = data._data
        return super().__new__(cls, data)

    def _init_depictor(self, datablock):
        depictor_type = {
            ParticleBlock: ParticleDepictor,
            ImageBlock: ImageDepictor,
            PointBlock: PointDepictor,
            LineBlock: LineDepictor,
        }
        try:
            # don't store a reference to it, cause it hooks itself on the datablock
            depictor_type[type(datablock)](datablock, peeper=self)
        except KeyError:
            raise TypeError(f'cannot find a Depictor for datablock of type {type(datablock)}')

    @property
    def depictors(self):
        return self.blocks.depictor

    def _init_viewer(self, viewer=None):
        # create a new viewer if necessary
        if viewer is not None:
            self.viewer = viewer
        elif self.viewer is None:
            self.viewer = napari.Viewer(ndisplay=3)

        # random check to make sure viewer was not closed
        try:
            self.viewer.window.qt_viewer.actions()
        except RuntimeError:
            self.viewer = napari.Viewer(ndisplay=3)

    def peep(self, viewer=None):
        self._init_viewer(viewer)
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
