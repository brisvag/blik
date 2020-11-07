from abc import ABC

import numpy as np
from scipy.interpolate import splprep, splev

from .components import Child, ArrayContainer


class GeometricPrimitive(Child):
    """
    Base class for geometric primitive objects
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

    def _min_attr(self, attribute_name):
        attr = getattr(self, attribute_name)
        return np.min(attr)

    def _max_attr(self, attribute_name):
        attr = getattr(self, attribute_name)
        return np.max(attr)


class Point(GeometricPrimitive):
    """
    Base class for Point objects in 2D and 3D with convenience methods
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def _min_x(self):
        return self._min_attr('x')

    @property
    def _min_y(self):
        return self._min_attr('y')

    @property
    def _min_z(self):
        return self._min_attr('z')

    @property
    def _max_x(self):
        return self._max_attr('x')

    @property
    def _max_y(self):
        return self._max_attr('y')

    @property
    def _max_z(self):
        return self._max_attr('z')

    @property
    def xy(self):
        return np.column_stack((self.x, self.y))

    @property
    def yx(self):
        return np.column_stack((self.y, self.x))

    @property
    def xyz(self):
        return np.column_stack((self.x, self.y, self.z))

    @property
    def zyx(self):
        return np.column_stack((self.z, self.y, self.x))

    @property
    def center_of_mass(self):
        # Check dimensionality
        if self.ndim == 1:
            return self

        elif self.ndim == 2:
            return np.mean(self, axis=0)

        else:
            raise NotImplementedError(f'center of mass calculation not implemented for objects with ndim > 2')

    def distance_to_point(self, point):
        """
        Calculates the distance form the center of mass of a Point object to a point

        Parameters
        ----------
        point

        Returns
        -------

        """
        point = np.asarray(point)
        if point.ndim == 1:
            return np.linalg.norm(self.center_of_mass - point)


class Point2D(Point, ArrayContainer):
    """
    An array container class for a 2D point
    1-dimensional array of order (x, y) along axis 0
    """

    def __new__(cls, point, **kwargs):
        return ArrayContainer(point, target_shape=2).view(cls)

    def __init__(self, point, **kwargs):
        super().__init__(**kwargs)

    @property
    def x(self):
        return self.asarray[0]

    @property
    def y(self):
        return self.asarray[1]


class Point3D(Point, ArrayContainer):
    """
    An array container class for 3D point
    1-dimensional array of order (x, y, z) along axis 0
    """

    def __new__(cls, point, **kwargs):
        return ArrayContainer(point, target_shape=3).view(cls)

    def __init__(self, point, **kwargs):
        super().__init__(**kwargs)

    @property
    def x(self):
        return self.asarray[0]

    @property
    def y(self):
        return self.asarray[1]

    @property
    def z(self):
        return self.asarray[2]


class Points2D(Point, ArrayContainer):
    """
    An array container class for 2D points
    2-dimensional array of shape (n, 2) with order (x, y) along axis 1
    """

    def __new__(cls, points, **kwargs):
        return ArrayContainer(points, target_shape=(-1, 2)).view(cls)

    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)

    @property
    def x(self):
        return self.asarray[:, 0]

    @property
    def y(self):
        return self.asarray[:, 1]


class Points3D(Point, ArrayContainer):
    """
    An array container class for 3D points
    2-dimensional array of shape (n, 3) with order (x, y, z) along axis 1
    """

    def __new__(cls, points, **kwargs):
        return ArrayContainer(points, target_shape=(-1, 3)).view(cls)

    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)

    @property
    def x(self):
        return self.asarray[:, 0]

    @property
    def y(self):
        return self.asarray[:, 1]

    @property
    def z(self):
        return self.asarray[:, 2]


class Line(GeometricPrimitive, ABC):
    """
    Abstract base class for Line objects with convenience methods common to line classes

    Line classes should be ArrayContainers of shape (n, m), n ordered points in m dimensions

    order of dimensions along m is (x, y, z)

    Polarity (direction) of lines, lines start from 0 to n along the 0th dimension
    """

    def __new__(cls):
        pass

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.spline_smoothing_parameter = 0
        self._tck = None

    @property
    def asarray(self):
        return np.asarray(self)

    @property
    def x(self):
        return self.asarray[:, 0]

    @property
    def y(self):
        return self.asarray[:, 1]

    @property
    def z(self):
        return self.asarray[:, 2]

    @property
    def ndim(self):
        return self.shape[1]

    @property
    def _ordered_dims(self):
        """
        the order of dimensions
        Returns str 'xyz'
        -------

        """
        return 'xyz'

    @property
    def dims_list(self):
        """
        returns a list of observations in each dimension present in the line object
        (this is expected by splprep for preparing splines)
        Returns
        -------

        """
        return [getattr(self, dim) for idx, dim in enumerate(self.ordered_dims) if idx < self.ndim]

    @property
    def npoints(self):
        return self.shape[0]

    @property
    def spline_smoothing_parameter(self):
        return self._spline_smoothing_parameter

    @spline_smoothing_parameter.setter
    def spline_smoothing_parameter(self, value):
        self._spline_smoothing_parameter = float(value)

    def fit_spline(self):
        self._tck = splprep(self.dims_list, self.spline_smoothing_parameter)
        return self._tck

    def evaluate_spline(self, n_points):
        u = np.linspace(0, 1, n_points, endpoint=True)
        return splev(u, tck=self._tck)

    @property
    def smooth_backbone(self):
        return self._generate_smooth_backbone()

    def _generate_smooth_backbone(self, n_points=1000):
        u = np.linspace(0, 1, n_points, endpoint=True)
        self.fit_spline()
        return self.evaluate_spline(n_points)





# class Sphere:
#     def __init__(self, center=None, edge_point=None, radius: float = None):
#         self.center = center
#         self.radius = float(radius)
#         self.edge_point = edge_point
#
#     @property
#     def center(self):
#
#
#     @property
#     def edge_point(self):
#         return self._edge_point
#
#     @edge_point.setter
#     def edge_point(self, point):
#         point = np.asarray()
#
