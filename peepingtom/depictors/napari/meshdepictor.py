from .naparidepictor import NapariDepictor


class MeshDepictor(NapariDepictor):
    def depict(self):
        self._make_surface_layer(self.datablock.vertices[:, ::-1],
                                 self.datablock.faces,
                                 name=f'{self.name} - mesh')
