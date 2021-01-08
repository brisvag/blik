def listify(obj):
    """
    transform input into an appropriate list, unless already list-like
    """
    # avoid circular import
    from ..core import DataCrate, DataSet
    if isinstance(obj, (list, tuple)) and not isinstance(obj, (DataCrate, DataSet)):
        return obj
    if obj is None:
        return []
    return [obj]
