class Depictor:
    """
    base depictor class. Subclasses should call super().__init__ last, to properly
    create a depiction
    """
    def __init__(self, datablock):
        self.datablock = datablock
        self.depict()

    @property
    def name(self):
        return self.datablock.name

    def depict(self):
        """
        generate or update depictions based on current parameters
        """
        raise NotImplementedError

    def show(self, viewer):
        """
        display depictions in a viewer
        """
        raise NotImplementedError

    def hide(self, viewer):
        """
        hide depictions from a viewer
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

    def __repr__(self):
        return f'{type(self).__name__}{self.datablock.__name_repr__()}'
