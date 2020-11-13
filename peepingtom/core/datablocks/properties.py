from ..base import DataBlock


class PropertyBlock(DataBlock):
    """
    PropertyBlock is a simple dictionary wrapper for arbitrary data
    """
    def __init__(self, properties, **kwargs):
        super().__init__(**kwargs)
        self.data = properties

    def _data_setter(self, properties):
        return properties

    def dump(self):
        kwargs = super().dump()
        kwargs.update({'properties': self.data})
        return kwargs

    def items(self):
        return self.data.items()
