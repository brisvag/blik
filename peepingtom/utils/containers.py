from collections.abc import Iterable


class AttributedList(list):
    """
    a list that accepts dot notation to return attributes of its elements, if all
    contained elements have that attribute and itself does not

    You can also set attributes and call methods of the nested elements.
    If setattr is called with a value of type AttributedList, the list will attempt to set the attributes
    element by element
    """
    def __getattribute__(self, name):
        try:
            return super().__getattribute__(name)
        except AttributeError as e:
            try:
                attrs = AttributedList()
                for item in self:
                    # this lets us go as deep as needed, if working with nested lists
                    if isinstance(item, (list, AttributedList)):
                        for sub_item in AttributedList(item):
                            try:
                                attrs.extend(sub_item.__getattribute__(name))
                            # when finding methods, this is raised
                            # TODO: why?
                            except TypeError:
                                attrs.append(sub_item.__getattribute__(name))
                    else:
                        attrs.append(item.__getattribute__(name))
                return attrs
            except AttributeError:
                raise e

    def __setattr__(self, name, value):
        # check first in the normal way
        if hasattr(list(self), name):
            list.__setattr__(self, name, value)

        # can only safely do this recursively if we know where to find the atttributes lower down
        elif hasattr(self, name):
            zip_values = None

            # if another Attributed list is fed, do it value by value if possible
            if isinstance(value, AttributedList):
                # len(self) is not enough because it might be nested
                if len(self.__getattribute__(name)) == len(value):
                    zip_values = list(reversed(value))  # reversed for popping

            for item in self:
                if zip_values is not None:
                    # if an attributed list was given, use it value by value
                    value = zip_values.pop()
                # this lets us go as deep as needed, if working with nested lists
                if isinstance(item, Iterable):
                    for sub_item in AttributedList(item):
                        sub_item.__setattr__(name, value)
                else:
                    item.__setattr__(name, value)
        else:
            raise AttributeError


    def __call__(self, *args, **kwargs):
        return AttributedList(item.__call__(*args, **kwargs) for item in self)
