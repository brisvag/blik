def listify(obj):
    """
    transform input into an appropriate list, unless already list-like
    """
    if isinstance(obj, (list, tuple)):
        return obj
    if obj is None:
        return []
    return [obj]
