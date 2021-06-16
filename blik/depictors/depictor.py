class Depictor:
    """
    base depictor class. Subclasses should call super().__init__ last, to properly
    create a depiction
    """
    def __init__(self, datablock):
        self.datablock = datablock

    @property
    def name(self):
        return self.datablock.name

    def depict(self, **kwargs):
        """
        generate or update depictions based on current parameters
        """
        raise NotImplementedError

    def update(self):
        """
        update the displayed data based on the current state of the datablock
        """

    def changed(self, event):
        """
        fired when data is changed from the depiction side.
        Subclasses can overload this method with the logic to update
        the data in the datablock accordingly
        don't forget to accept the `event` argument!
        """

    def purge(self):
        """
        delete all depictions, resetting to initialized state
        """

    def __repr__(self):
        return f'{type(self).__name__}{self.datablock.__name_repr__()}'
