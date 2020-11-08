from collections.abc import Iterable, Sized


def flatten(iterable):
    """
    Flattens an iterable of iterables into one level
    e.g. [[1, 2, 3], [4, 5, 6]] -> [1, 2, 3, 4, 5, 6]

    Parameters
    ----------
    iterable : nested iterable which you want to flatten

    Returns flattened version of iterable
    -------

    """
    return [x for y in z for x in y]


def simplify(obj):
    """
    Simplify length one list, and tuple iterables into the object themselves
    simplify length one dict iterables into the value of the only key present

    Parameters
    ----------
    obj : iterable of one or more objects

    Returns object if iterable is tuple or list of length 1, else iterable
            returns value if iterable is dict of length 1, else iterable
    -------

    """
    if len(obj) > 1:
        return

    obj = obj[0] if type(obj) in (tuple, list) and len(obj) == 1 else obj
    obj = obj[obj.keys[0]] if obj is dict and len(obj) == 1 else obj

    return obj
