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
                return AttributedList([item.__getattribute__(name) for item in self])
            except AttributeError:
                raise e
