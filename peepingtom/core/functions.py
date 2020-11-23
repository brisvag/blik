def merge(datablocks):
    """
    merges a list of datablocks into a single datablock
    """
    cls = type(datablocks[0])
    if not all(isinstance(db, cls) for db in datablocks):
        raise TypeError('cannot merge datablocks of different types')
    return datablocks[0]._merge(datablocks)


def stack(datablocks):
    """
    stacks a list of datablocks into a single datablock
    """
    cls = type(datablocks[0])
    if not all(isinstance(db, cls) for db in datablocks):
        raise TypeError('cannot stack datablocks of different types')
    return datablocks[0]._stack(datablocks)
