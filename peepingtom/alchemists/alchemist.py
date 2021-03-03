from ..utils import listify


class Alchemist:
    """
    Base class for all alchemist objects, used to transform a datablocks into other datablocks
    """
    def __init__(self, input_blocks):
        self.inputs = listify(input_blocks)
        self.outputs = []
        self.transform()
        for output in reversed(self.outputs):
            self.inputs[0].add_to_same_volume(output)

    def transform(self):
        """
        generate the output blocks based on the current settings and the input blocks
        """
        raise NotImplementedError

    def update(self):
        """
        update data of the outputs and fire the update method of the generated datablocks
        """
        raise NotImplementedError
