from .plotdepictor import PlotDepictor
from ...utils.colors import distinct_colors


class PropertyPlotDepictor(PlotDepictor):
    def __init__(self, datablock, colors=None, **kwargs):
        super().__init__(datablock)
        self.colors = colors or distinct_colors[:len(datablock.data.columns)]
        self.kwargs = kwargs

    def depict(self):
        for (colname, data), color in zip(self.datablock.items(), self.colors):
            self.add_line(data, name=colname, color=color, **self.kwargs)
