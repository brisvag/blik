from .plotdepictor import PlotDepictor


class PropertyPlotDepictor(PlotDepictor):
    def __init__(self, datablock, property, **kwargs):
        self.kwargs = kwargs
        self.property = property
        super().__init__(datablock)

    def depict(self):
        data = self.datablock.properties[self.property]
        self.add_line(data, name=f'{self.name} - {self.property}', **self.kwargs)
