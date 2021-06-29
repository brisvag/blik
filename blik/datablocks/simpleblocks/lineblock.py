import numpy as np
from scipy.interpolate import splprep, splev

from .pointblock import PointBlock
from ...depictors import LineDepictor


class LineBlock(PointBlock):
    """
    LineBlock objects represent lines with convenience methods

    LineBlock data should be array-like objects of shape (n, d) representing n points in d dimensions
    """
    _depiction_modes = {'default': LineDepictor}

    def __init__(self, *, spline_smoothing_parameter=0, **kwargs):
        super().__init__(**kwargs)

        # initialise attributes related to spline fitting
        self.spline_smoothing_parameter = spline_smoothing_parameter
        self._tck = None

    @property
    def spline_smoothing_parameter(self):
        return self._spline_smoothing_parameter

    @spline_smoothing_parameter.setter
    def spline_smoothing_parameter(self, value):
        self._spline_smoothing_parameter = float(value)

    def fit_spline(self, dimensions='xyz', smoothing_parameter=None):
        """
        dimensions :  str of named dimensions ('xyz') to which a spline should be fit
        smoothing_parameter : smoothing parameter for spline fitting

        Returns tck, list of spline parameters from scipy.interpolate.splprep
        """
        if smoothing_parameter:
            self.spline_smoothing_parameter = smoothing_parameter

        dims_to_fit = self._get_named_dimensions(dimensions).T
        self._tck, _ = splprep(dims_to_fit, s=self.spline_smoothing_parameter)

        return self._tck

    def evaluate_spline(self, n_points):
        u = np.linspace(0, 1, n_points, endpoint=True)
        return np.asarray(splev(u, tck=self._tck)).T

    @property
    def smooth_backbone(self):
        return self._generate_smooth_backbone()

    def _generate_smooth_backbone(self, n_points=1000):
        self.fit_spline()
        return self.evaluate_spline(n_points)
