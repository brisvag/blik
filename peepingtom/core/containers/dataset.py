from ...utils import AttributedList, listify


class DataSet(AttributedList):
    """
    A container for a collection of DataCrates
    """
    def __init__(self, datacrates):
        super().__init__(listify(datacrates))
