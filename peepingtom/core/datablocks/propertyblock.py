from .base import SimpleBlock


class PropertyBlock(SimpleBlock):
    """
    PropertyBlock is a simple dictionary wrapper for arbitrary data
    """
    def _data_setter(self, data):
        return dict(data)

    def items(self):
        return self.data.items()

    @staticmethod
    def _merge_data(datablocks):
        # TODO: this is probably gonna break
        return {k: v for db in datablocks for k, v in db.items()}

    @staticmethod
    def _stack_data(datablocks):
        return {}
