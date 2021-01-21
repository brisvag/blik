from .plotdepictor import PlotDepictor
from ...utils import distinct_colors, faded_grey


class ClassPlotDepictor(PlotDepictor):
    def __init__(self, datablock, class_tag, **kwargs):
        self.kwargs = kwargs
        self.class_tag = class_tag
        super().__init__(datablock)

    def depict(self):
        centroids = self.datablock.metadata[f'{self.class_tag}_centroids']
        n_classes = self.datablock.metadata[f'{self.class_tag}_params']['n_classes']
        colors = distinct_colors[:n_classes]
        for i, (centroid, color) in enumerate(zip(centroids, colors)):
            self.add_line(centroid, name=f'{self.class_tag} {i}', color=color, **self.kwargs)
