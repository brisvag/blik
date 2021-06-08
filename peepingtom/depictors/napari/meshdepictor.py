from .naparidepictor import NapariDepictor


class MeshDepictor(NapariDepictor):
    def depict(self):
        self._make_surface_layer(self.datablock.vertices.data,
                                 self.datablock.faces.data,
                                 name=f'{self.name} - mesh')
