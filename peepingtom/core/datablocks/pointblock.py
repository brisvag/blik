import numpy as np

from .base import SimpleBlock


class PointBlock(SimpleBlock):
    """
    PointBlock objects for representing points with convenience methods

    PointBlock data should be array-like objects of shape (n, m) representing n points in m dimensions

    order of dimensions along m is:
    2d : (x, y)
    3d : (x. y, z)
    nd : (..., x, y, z)
    """
    def _data_setter(self, data):
        # cast as array
        data = np.asarray(data)

        # coerce 1d point to 2d
        if data.ndim == 1:
            data = data.reshape((1, len(data)))

        # check ndim of data
        if not data.ndim == 2:
            raise ValueError("data object should have ndim == 2")

        return data

    @property
    def ndim(self):
        """
        as ndim for numpy arrays, but treating the points as a sparse matrix.
        returns the number of dimensions (spatial or not) describing the points
        """
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
        if self.ndim > 3:
            dim_idx = -dim_idx - 1

        return dim_idx

    def _get_dim_at_spatial_index(self, idx: int):
        return self[:, idx]

    def _get_named_dimension(self, dim: str, as_type='array'):
        """
        Get data for a named dimension or multiple named dimensions of the object

        as_array and as_tuple are only considered when retrieving multiple dimensions in one method call
        Parameters
        ----------

        dim : str 'x', 'y', 'z' or a combination thereof
        as_type : str for return type, only if len(dim) > 1
                  'array' for ndarray or 'tuple' for tuple return type

        Returns (default) (n,m) ndarray of data along named dimension(s) from m
                  or tuple of arrays of data along each axis
        -------

        """
        if as_type not in ('array', 'tuple'):
            raise ValueError("Argument 'as_type' must be a string from 'array' or 'tuple'")

        if len(dim) > 1:
            # split dims up and get each separately
            data = [self._get_named_dimension(_dim) for _dim in dim]

            # decide on output type and return array or tuple as requested, default to array
            if as_type == 'array':
                return np.column_stack(data)
            elif as_type == 'tuple':
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
    def z(self):
        return self._get_named_dimension('z')

    @property
    def xyz(self):
        return self._get_named_dimension('xyz')

    @property
    def zyx(self):
        return self._get_named_dimension('zyx')

    def as_zyx(self):
        """
        return the data with the order of the spatial axes switched to 'zyx' style rather than 'xyz'

        Returns
        -------
        correct view into data no matter the dimensionality
        """
        if self.ndim == 1:
            return self.data
        elif self.ndim == 2:
            # invert last two axes
            return self.data[:, ::-1]
        else:
            # invert only last three axes, leave leading dimensions intact
            data = np.empty_like(self.data)
            data[:, :-3] = self.data[:, :-3]
            data[:, -3:] = self.data[:, -1:-4:-1]
            return data

    @property
    def n(self):
        return len(self)

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
        if not point.shape == self.center_of_mass.shape:
            raise ValueError(
                f"shape of point '{point.shape}' does not match shape of center of mass "
                f"'{self.center_of_mass.shape}'")
        return np.linalg.norm(point - self.center_of_mass)

    def dump(self):
        kwargs = super().dump()
        kwargs.update({'points': self.data})
        return kwargs

    @staticmethod
    def _merge_data(datablocks):
        return np.concatenate([db.data for db in datablocks])

    @staticmethod
    def _stack_data(datablocks):
        # this method assumes that stacked points are always intended to have
        # indexes at any dimension that's higher than 3
        dims = [db.ndim for db in datablocks]
        # only obvious how to stack elements with just 1 dimension of difference
        if abs(min(dims) - max(dims)) > 1:
            return NotImplemented
        # allocate the right size
        stack_shape = (sum([db.n for db in datablocks]), min(dims) + 1)
        stacked = np.zeros(stack_shape)
        previous = 0
        for idx, db in enumerate(datablocks):
            current = previous + db.n
            if db.ndim == max(dims) and db.ndim != min(dims):
                if len(np.unique(db.data)) != 1:
                    raise ValueError(f'cannot stack: dimension #{db.ndim} of {db} is not an index')
                # if the given data is not in order, just give up. TODO: implement something smarter!
                elif db.data[0, 0] != idx:
                    raise ValueError(f'cannot stack: the index ({db.data[0,0]}) of {db} does not match')
                else:
                    stacked[previous:current] = db.data
            elif db.ndim == min(dims):
                stacked[previous:current] = np.concatenate([np.ones((db.n, 1)) * idx, db.data], axis=1)
            previous = current
        return stacked

    def __shape_repr__(self):
        return f'{self.data.shape}'
