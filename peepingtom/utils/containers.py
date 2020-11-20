class AttributedList(list):
    """
    a list that accepts dot notation to return attributes of its elements, if all
    contained elements have that attribute and itself does not
    """
    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            try:
                return AttributedList(item.__getattribute__(name) for item in self)
            except AttributeError:
                raise e

    def __setattr__(self, name, value):
        try:
            [item.__setattr__(name, value) for item in self]
        except TypeError:
            super().__setattr__(name, value)

    def __call__(self, *args, **kwargs):
        return AttributedList(item.__call__(*args, **kwargs) for item in self)
