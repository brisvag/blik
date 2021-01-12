from ...utils import DispatchList


class DataCrateDepictor:
    def __init__(self, datacrate):
        self.datacrate = datacrate

    @property
    def depictors(self):
        return DispatchList(depictor for db in self.datacrate for depictor in db.depictors)

    @property
    def layers(self):
        return DispatchList(layer for depictor in self.depictors for layer in depictor.layers)

    def show(self, viewer):
        for db in self.datacrate:
            if not db.depictors:
                db.depict()
        self.depictors.show(viewer)

    def hide(self, viewer):
        self.depictors.hide(viewer)
