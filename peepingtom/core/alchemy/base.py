from abc import ABC, abstractmethod


class Alchemist(ABC):
    """
    Base class for all alchemist objects, used to transform a datablocks into other datablocks
    """
    def __init__(self, input_blocks):
        self.inputs = input_blocks
        self.outputs = {}

    def __repr__(self):
        return f'<{type(self).__name__}>'

    @abstractmethod
    def transform(self):
        """
        generate the output blocks based on the current settings and the input blocks
        """
