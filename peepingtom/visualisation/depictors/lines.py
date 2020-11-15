from ..base import Depictor


class LineDepictor(Depictor):
    def draw(self, point_kwargs={}, backbone_kwargs={}, **kwargs):
        super().draw(**kwargs)

        # default keyword arguments
        pkwargs = {'size': 3,
                   'face_color': 'cornflowerblue'}
        bkwargs = {'edge_color': 'orangered',
                     'edge_width': 1}

        # update keyword arguments from passed dictionaries
        pkwargs.update(point_kwargs)
        bkwargs.update(backbone_kwargs)

        # get points data in napari expected order
        points_data = self.datablock.as_zyx()

        # get smooth backbone data in napari expected order
        backbone_data = self.datablock.smooth_backbone[:, ::-1]

        # draw points layer in napari
        points = self.viewer.add_points(points_data,
                                        name=f'{self.name} - points',
                                        **pkwargs)

        self.layers.append(points)

        # draw line as path in napari
        backbone = self.viewer.add_shapes(backbone_data,
                                          shape_type='path',
                                          name=f'{self.name} - line',
                                          **bkwargs)

        self.layers.append(backbone)

    @property
    def points_layer(self):
        return self.layers[0]

    @property
    def backbone_layer(self):
        return self.layers[1]