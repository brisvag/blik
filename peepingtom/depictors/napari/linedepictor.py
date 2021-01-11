from .blockdepictor import BlockDepictor


class LineDepictor(BlockDepictor):
    def depict(self):
        # default keyword arguments
        pkwargs = {'size': 3,
                   'face_color': 'cornflowerblue'}
        bkwargs = {'edge_color': 'orangered',
                   'edge_width': 1}

        # get points data in napari expected order
        points_data = self.datablock.as_zyx()

        # get smooth backbone data in napari expected order
        backbone_data = self.datablock.smooth_backbone[:, ::-1]

        # draw points layer in napari
        self.make_points_layer(points_data,
                               name=f'{self.name} - points',
                               **pkwargs)

        # draw line as path in napari
        self.make_shapes_layer(backbone_data,
                               shape_type='path',
                               name=f'{self.name} - line',
                               **bkwargs)

    @property
    def points_layer(self):
        return self.layers[0]

    @property
    def backbone_layer(self):
        return self.layers[1]

    def update(self):
        backbone_data = self.datablock.smooth_backbone[:, ::-1]
        self.backbone_layer.selected_data = {0}
        self.backbone_layer.remove_selected()
        self.backbone_layer.add(backbone_data, shape_type='path')

    def changed(self, event):
        self.datablock.data = self.points_layer.data[:, ::-1]
