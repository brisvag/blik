from pyqtgraph import PlotItem

from ..depictor import Depictor


class PlotDepictor(Depictor):
    def __init__(self, datablock):
        super().__init__(datablock)
        self.plot = PlotItem()
        self.plot.addLegend()

    def add_line(self, y, name, x=None, color='w'):
        if x is None:
            x = range(len(y))
        self.plot.plot(x, y, name=name, pen=color)

    def purge(self):
        self.plot = PlotItem()
