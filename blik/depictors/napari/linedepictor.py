from .naparidepictor import NapariDepictor


class LineDepictor(NapariDepictor):
    def depict(self):
        # default keyword arguments
        pkwargs = {'size': 3,
                   'face_color': 'cornflowerblue'}
        bkwargs = {'edge_color': 'orangered',
                   'edge_width': 1}

        # get points data in napari expected order
        points_data = self.datablock.as_zyx

        # get smooth backbone data in napari expected order
        backbone_data = self.datablock.smooth_backbone[:, ::-1]

        # draw points layer in napari
        self._make_points_layer(points_data,
                                name=f'{self.name} - points',
                                **pkwargs)

        # draw line as path in napari
        self._make_shapes_layer(backbone_data,
                                shape_type='path',
                                name=f'{self.name} - line',
                                **bkwargs)

    @property
    def points(self):
        return self.layers[0]

    @property
    def backbone(self):
        return self.layers[1]

    def update(self):
        if self.layers:
            backbone_data = self.datablock.smooth_backbone[:, ::-1]
            self.backbone.selected_data = {0}
            self.backbone.remove_selected()
            self.backbone.add(backbone_data, shape_type='path')

    def changed(self, event):
        self.datablock.data = self.points.data[:, ::-1]
