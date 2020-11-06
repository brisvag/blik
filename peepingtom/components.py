class SmartList():
    """
    typed list that can be indexed n-dimensionally, also with properties of the elements
    """
    def __init__(self, basetype, iterable=()):
        super().__init__(iterable)
