from .datablock import DataBlock


class DataCrate(list):
    """
    A container of DataBlock objects which exist within the same n-dimensional reference space
    """
    # TODO: add napari-like indexing by attribute or by type
    def __init__(self, iterable=()):
        super().__init__(iterable)
        if not all([isinstance(i, DataBlock) for i in iterable]):
            raise Exception('DataBlock can only collect BaseData objects')
