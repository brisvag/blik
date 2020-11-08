from abc import ABC, abstractmethod

import numpy as np
import pandas as pd
from scipy.interpolate import splprep, splev
from eulerangles import euler2matrix

from ..utils.components import Child


class DataBlock(Child, ABC):
    """
    Base class for all classes which can be put into Crates for subsequent visualisation

    Examples include geometric primitives such as Points, Line, Sphere

    DataBlock objects must implement a data setter method as _data_setter which sets the value of DataBlock._data

    Calling __getitem__ on a DataBlock will call __getitem__ on its data property
    """

    def __init__(self, properties=None, **kwargs):
        super().__init__(**kwargs)
        self.properties = properties

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        raise NotImplementedError

    def __getitem__(self, item):
        return self.data[item]


class PointBlock(DataBlock):
    """
    PointBlock objects for representing points with convenience methods

    PointBlock data should be array-like objects of shape (n, m) representing n points in m dimensions

    order of dimensions along m is:
    2d : (x, y)
    3d : (x. y, z)
    nd : (..., x, y, z)
    """

    def __init__(self, points, **kwargs):
        super().__init__(**kwargs)
        self.data = points

    def _data_setter(self, points):
        # cast as array
        points = np.asarray(points)

        # coerce 1d point to 2d
        if points.ndim == 1:
            points.reshape((1, len(points)))

        # check ndim of points
        assert points.ndim == 2

        self._data = points

    @property
    def ndim_spatial(self):
        return self.data.shape[1]

    def _named_dimension_to_spatial_index(self, dim: str):
        """
        Gets the index of the named dimension 'x', 'y' or 'z'
        Parameters
        ----------
        dim : str, must be one of 'x', 'y' or 'z'

        Returns data along named dimension
        -------

        """
        # sanitise input
        dim = str(dim.strip().lower())

        # dim to index for 3d or less
        dim_to_index = {'x': 0,
                        'y': 1,
                        'z': 2}

        dim_idx = dim_to_index[dim]

        # check and correct index for higher dimensionality
        if self.ndim_spatial >= 3:
            dim_idx = -dim_idx - 1

        return dim_idx

    def _get_dim_at_spatial_index(self, idx: int):
        return self[:, idx]

    def _get_named_dimension(self, dim: str, as_array=None, as_tuple=None):
        """
        Get data for a named dimension or multiple named dimensions of the object

        as_array and as_tuple are only considered when retrieving multiple dimensions in one method call
        Parameters
        ----------

        dim : str 'x', 'y', 'z' or a combination thereof
        as_array : bool, force return type to be ndarray (incompatible with as_tuple)
        as_tuple : bool, force return type to be tuple (incompatible with as_array)

        Returns : (default) (n,m) ndarray of data along named dimension(s) from m
                  or tuple of arrays of data along each axis
        -------

        """
        if as_tuple and as_array:
            raise ValueError(f"'as_tuple' and 'as_array' cannot both be True")

        if len(dim) > 1:
            # split dims up and get each separately
            data = [self._get_named_dimension(_dim) for _dim in dim]

            # decide on output type and return array or tuple as requested, default to array
            if (as_array and not as_tuple) or (not (as_array and as_tuple)):
                return np.column_stack(data)
            elif as_tuple and not as_array:
                return tuple(data)

        else:
            # get index of named dimension along spatial axis
            dim_idx = self._named_dimension_to_spatial_index(dim)
            # index into self to get data
            return self._get_dim_at_spatial_index(dim_idx)

    @property
    def x(self):
        return self._get_named_dimension('x')

    @property
    def y(self):
        return self._get_named_dimension('y')

    @property
    def y(self):
        return self._get_named_dimension('z')

    @property
    def xyz(self):
        return self._get_named_dimension('xyz')

    @property
    def zyx(self):
        return self._get_named_dimension('zyx')

    @property
    def center_of_mass(self):
        return np.mean(self.data, axis=0)

    def distance_to(self, point):
        """
        Calculate the euclidean distance between the center of mass of this object and a point

        Parameters
        ----------
        point : array-like object

        Returns : euclidean distance
        -------

        """
        point = np.asarray(point)
        assert point.shape == self.center_of_mass.shape
        return np.linalg.norm(point - self.center_of_mass)


class LineBlock(PointBlock):
    """
    LineBlock objects represent lines with convenience methods

    LineBlock line data should be array-like objects of shape (n, m) representing n ordered points in m spatial
    dimensions

    order of dimensions along m is:
    2d : (x, y)
    3d : (x. y, z)
    nd : (..., x, y, z)

    Polarity (direction) of lines, lines start from 0 to n along the 0th dimension
    """

    def __init__(self, line, **kwargs):
        """

        Parameters
        ----------
        line : array-like objects of shape (n, m) representing n ordered points in m spatial dimensions
        kwargs : kwargs are passed to DataBlock object

        """
        super().__init__(points=line, **kwargs)

        # initialise attributes related to spline fitting
        self.spline_smoothing_parameter = 0
        self._tck = None

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


class OrientationBlock(DataBlock):
    """
    OrientationBlock objects represent orientations in a 2d or 3d space

    Contains factory methods for instantiation from eulerian angles
    """

    def __init__(self, rotation_matrices: np.ndarray, **kwargs):
        """

        Parameters
        ----------
        rotation_matrices : (n, 2, 2) or (n, 3, 3) array of rotation matrices R
                            R should satisfy Rv = v' where v is a column vector
        kwargs
        """
        super().__init__(**kwargs)
        self.data = rotation_matrices

    def _data_setter(self, rotation_matrices: np.ndarray):
        # check for single matrix case and assert dimensionality
        assert rotation_matrices.shape[-1] == rotation_matrices.shape[-2]

        if rotation_matrices.ndim == 2:
            m = rotation_matrices.shape[-1]
            rotation_matrices = rotation_matrices.reshape((1, m, m))
        self._data = rotation_matrices

    @property
    def ndim_spatial(self):
        return self.data.shape[-1]

    @classmethod
    def from_euler_angles(cls, euler_angles: np.ndarray, axes: str, intrinsic: bool, positive_ccw: bool,
                          invert_matrix: bool):
        """
        Factory method for creating a VectorBlock directly from a set of eulerian angles

        Parameters
        ----------
        euler_angles : ndarray, (n, 3) array of n sets of eulerian angles in degrees
        axes : str, 3 characters from 'x', 'y' and 'z' representing axes around which rotations occur in the euler angles
        intrinsic : bool, are the euler angles describing a set of intrinsic (rotating reference frame) or extrinsic
                    (fixed reference frame) rotations
        positive_ccw : bool, are positive euler angles referring to counterclockwise rotations of vectors when looking
                       from a positive point along the axis towards the origin
        invert_matrix : bool, should the matrix be inverted?
                        this is useful if your euler angles describe the rotation of a target to a source but you would
                        like your rotation matrices to describe the rotation of a source to align it with a target

        Returns
        -------

        """
        # Calculate rotation matrices
        rotation_matrices = euler2matrix(euler_angles, axes=axes, intrinsic=intrinsic, positive_ccw=positive_ccw)

        # invert matrix if required
        if invert_matrix:
            rotation_matrices = rotation_matrices.transpose((-1, -2))

        return cls(rotation_matrices)

    def _calculate_matrix_product(self, vector: np.ndarray):
        """
        Calculates the matrix product (v') of the orientation matrices (R) in this VectorBlock object with a given vector (v)
        Rv = v'

        Parameters
        ----------
        vector : ndarray v, column vector or set of column vectors to be premultiplied by rotation matrices

        Returns ndarray v', matrix product Rv
        -------

        """
        return self.data @ vector

    def _unit_vector(self, axis: str):
        """
        Get a unit vector along a specified axis which matches the dimensionality of the VectorBlock object

        Parameters
        ----------
        axis : str, named axis 'x', 'y' or 'z'

        Returns unit vector along provided axis with appropriate dimensionality
        -------

        """
        # check dimensionality
        if self.ndim_spatial > 3:
            raise NotImplementedError(
                'Unit vector generation for objects with greater than 3 spatial dimensions is not implemented')

        # initialise unit vector array
        unit_vector = np.zeros(self.ndim_spatial)

        # get index which corresponds to axis for vector
        axis_to_index = {'x': 0,
                         'y': 1,
                         'z': 2}
        dim_idx = axis_to_index[axis]

        # construct unit vector
        if dim_idx <= self.ndim_spatial:
            unit_vector[dim_idx] = 1
        else:
            raise ValueError(f"You asked for axis {axis} from a {self.ndim_spatial}d object")

        return unit_vector


class ImageBlock(DataBlock):
    """
    n-dimensional image block
    data can be interpreted as n-dimensional images or stacks of n-dimensional images,
    this is controlled by the ndim_spatial attribute
    """

    def __init__(self, data, ndim_spatial: int, pixel_size=None, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.ndim_spatial = ndim_spatial
        self.pixel_size = pixel_size

    def _data_setter(self, image: np.ndarray):
        """
        TODO: should we contain only the path to the images or the images themselves here?
        Parameters
        ----------
        image

        Returns
        -------

        """
        self._data = image

    @property
    def pixel_size(self):
        return self._pixel_size

    @pixel_size.setter
    def pixel_size(self, value):
        self._pixel_size = float(value)
