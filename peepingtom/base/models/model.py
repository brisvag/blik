from abc import ABC, abstractmethod

from ...utils.components import Child


class Model(Child, ABC):
    """
    A Model is an object from which a set of Particles can be derived
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def derive_particles(self):
        pass
