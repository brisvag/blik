from pyqtgraph import PlotItem


class PlotDepictor:
    def __init__(self, datablock):
        self.datablock = datablock
        self.plot = PlotItem()
        self.plot.addLegend()
        self.depict()

    def name(self):
        return self.datablock.name

    def add_line(self, y, name, x=None, color='w'):
        if x is None:
            x = range(len(y))
        self.plot.plot(x, y, name=name, pen=color)
