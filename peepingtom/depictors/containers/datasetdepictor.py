"""
main class that interfaces visualization, analysis and data manipulation
"""

from pathlib import Path

from .viewer import Viewer
from ...utils import DispatchList


class DataSetDepictor:
    def __init__(self, dataset, viewers=None):
        self.dataset = dataset
        if viewers is None:
            viewers = {}
        self.viewers = viewers
        self.crate_viewers = {}

    @property
    def crate_depictors(self):
        return DispatchList(crate.depictor for crate in self.dataset)

    @property
    def block_depictors(self):
        return DispatchList(dep for db in self.dataset.flatten() for dep in db.depictors)

    def _get_viewer(self, viewer_key):
        parent_depictor = self.dataset._parent.depictor
        try:
            viewer = parent_depictor.viewers[viewer_key]
        except KeyError:
            viewer = Viewer()
            parent_depictor.viewers[viewer_key] = viewer
            parent_depictor.crate_viewers[viewer_key] = [crate for crate in parent_depictor.dataset]
        viewer._check()
        return viewer

    def show(self, viewer_key=0):
        self.crate_depictors.show(self._get_viewer(viewer_key))

    def hide(self, viewer_key=0):
        self.crate_depictors.hide(self._get_viewer(viewer_key))

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
