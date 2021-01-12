class Alchemist:
    """
    Base class for all alchemist objects, used to transform a datablocks into other datablocks
    """
    def __init__(self, input_blocks):
        self.inputs = input_blocks
        self.outputs = {}
        self.transform()

    def transform(self):
        """
        generate the output blocks based on the current settings and the input blocks
        """
        raise NotImplementedError
