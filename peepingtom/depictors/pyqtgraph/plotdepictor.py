from pyqtgraph import PlotItem

from ..depictor import Depictor


class PlotDepictor(Depictor):
    def __init__(self, datablock):
        self.plot = PlotItem()
        self.plot.addLegend()
        super().__init__(datablock)

    def add_line(self, y, name, x=None, color='w'):
        if x is None:
            x = range(len(y))
        self.plot.plot(x, y, name=name, pen=color)

    def show(self, viewer):
        if self.plot not in viewer.plots.items():
            viewer.plots.addItem(self.plot)
        viewer.plots.show()

    def hide(self, viewer):
        if self.plot in viewer.plots.items():
            viewer.plots.removeItem(self.plot)
            if any(isinstance(item, PlotItem) for item in viewer.plots.items()):
                viewer.plots.hide()
