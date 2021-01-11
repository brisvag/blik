from ..containers import DispatchList


class DataCrateDepictor:
    def __init__(self, datacrate):
        self.datacrate = datacrate

    @property
    def depictors(self):
        return DispatchList(depictor for db in self.datacrate for depictor in db.depictors)

    def show(self, viewer):
        self.depictors.show(viewer)

    def hide(self, viewer):
        self.depictors.hide(viewer)
