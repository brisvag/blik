"""
main class that interfaces visualization, analysis and data manipulation
"""

from .viewer import Viewer
from ...utils import DispatchList


class DataSetDepictor:
    def __init__(self, dataset, viewers=None, parent=None):
        self.dataset = dataset
        if viewers is None:
            viewers = {}
        self.viewers = viewers
        self._parent = parent

    @property
    def block_depictors(self):
        return DispatchList(dep for db in self.dataset for dep in db.depictors)

    def _get_viewer(self, viewer_key):
        try:
            viewer = self.viewers[viewer_key]
        except KeyError:
            viewer = Viewer()
            parent = self._parent or self
            parent.viewers[viewer_key] = viewer
        viewer._check()
        return viewer

    def show(self, viewer_key=0):
        for db in self.dataset:
            if not db.depictors:
                db.depict()
        self.block_depictors.show(self._get_viewer(viewer_key))

    def hide(self, viewer_key=0):
        self.block_depictors.hide(self._get_viewer(viewer_key))
