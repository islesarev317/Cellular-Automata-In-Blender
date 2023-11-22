import numpy as np
from copy import copy


class LocatedTensor:
    """
    the class implements a pair of an N dimensional tensor and a vector which contained N element
    """

    # ----------------- Class creators ----------------- #

    def __init__(self, corner, value):
        """
        :param corner: (tuple) vector of the lower left corner of the tensor location in N dimensional space
        :param value: (ndarray) value of the tensor
        """
        assert isinstance(corner, tuple), "Init exception: arg corner must be a tuple"
        assert isinstance(value, np.ndarray), "Init exception: arg value must be an ndarray"
        assert len(corner) == value.ndim, "Init exception: len of corner must fit ndim of value"
        self.__corner = np.array(corner)
        self.__value = value.copy()

    @classmethod
    def zeros(cls, corner, *, dim):
        """ alternative creator, which fills tensor with zeros values """
        value = np.zeros(dim)
        return cls(corner, value)

    # ----------------- Values ----------------- #

    def __getitem__(self, key):
        """ straight access to tensor (getter) """
        return self.__value[key]

    def __setitem__(self, key, value):
        """ straight access to tensor (setter) """
        self.__value[key] = value

    def get(self, point, default):
        """ handling for exception if we get values of the tensor which not exist """
        if sum(n < 0 for n in point) > 0:  # if local point = for example (0, -1)
            return default
        try:
            return self[point]
        except IndexError:
            return default

    # ----------------- Points ----------------- #

    @property
    def all_points(self):
        """
        returns list consists of all indexes of tensor
        to iterate all elements of tensor in loop
        (local points)
        """
        return list(np.ndindex(self.dim))

    @property
    def not_null_points(self):
        """ does the same that all_points, but it excludes zero values of tensor """
        return list(zip(*np.nonzero(self.__value != 0)))

    def point_to_global(self, point):
        """
        shifting point (index of the tensor) to the corner vector
        to get a global location of the point
        """
        return tuple(point + self.corner)

    def point_to_local(self, point):
        """ reverse operation: get a local location of the point from global one """
        return tuple(point - self.corner)

    # ----------------- Attributes ----------------- #

    @property
    def dim(self):
        """ shortcut for the shape """
        return self.__value.shape

    @property
    def corner(self):
        """ shortcut for corner param """
        return self.__corner

    @property
    def opp_corner(self):
        """ vector of the opposite corner of the tensor """
        return self.corner + self.dim - 1

    # ----------------- Math Operations ----------------- #

    @classmethod
    def __base_ops(cls, T1, T2, ops):
        """
        base internal function that can use for create the binary operations, such as union and subtract.
        """

        # create blank result tensor
        corner = tuple(np.vstack((T1.corner, T2.corner)).min(axis=0))
        dim = tuple(np.vstack((T1.opp_corner, T2.opp_corner)).max(axis=0) - corner + 1)
        result = cls.zeros(corner, dim=dim)

        # calculating values for result tensor:
        for point in result.all_points:
            global_point = result.point_to_global(point)
            t1_local_point = T1.point_to_local(global_point)
            t2_local_point = T2.point_to_local(global_point)
            t1_value = T1.get(t1_local_point, 0)
            t2_value = T2.get(t2_local_point, 0)
            result[point] = ops(t1_value, t2_value)

        return result

    def __add__(self, t):
        """ operation of addition two tensors """
        return self.__base_ops(self, t, lambda a, b: a + b)

    def __sub__(self, t):
        """ operation of subtraction two tensors"""
        return self.__base_ops(self, t, lambda a, b: a - b)

    def fill(self, value):
        """ set all not null points with given value """
        result = copy(self)
        for point in result.not_null_points:
            result[point] = value
        return result

    def minimum(self, threshold):
        """ fill with zero all values which don't satisfy the minimum  """
        result = copy(self)
        for point in result.not_null_points:
            value = result[point]
            if value < threshold:
                result[point] = 0
        return result

    def hollow(self):
        """
        [[1 1 1]    [[1 1 1]
         [1 1 1] =>  [1 0 1]
         [1 1 1]]    [1 1 1]]
        """
        result = copy(self)
        dim = self.dim
        ndim = len(dim)
        for point in np.ndindex(dim):
            if self[point] != 0:
                cnt = 0
                for i in range(ndim):
                    offset = np.zeros(ndim)
                    offset[i] = 1
                    for sign in [1, -1]:
                        n = tuple(np.int64(np.array(point) + (offset * sign)))
                        if 0 <= n[i] < dim[i]:
                            cnt += 0 if self[n] == 0 else 1
                if cnt == len(point) * 2:
                    result[point] = 0
        return result

    def num_alive(self, point):
        """ count the number of the alive neighbors """
        def get_neighbors(point, start=True):
            result = []
            for i in [0, 1, -1]:
                if len(point) > 1:
                    for tail in get_neighbors(point[1:], False):
                        neighbor = (point[0] + i, *tail)
                        result.append(neighbor)
                else:
                    neighbor = (point[0] + i,)
                    result.append(neighbor)
            if start:
                del result[0]
            return result

        num = 0
        for n_point in get_neighbors(point):
            if self.get(n_point, 0) != 0:
                num += 1
        return num

    # ----------------- Others ----------------- #

    def __copy__(self):
        """ implementation of copy process """
        return LocatedTensor(tuple(self.__corner.copy()), self.__value.copy())

    def __str__(self):
        """
        string representation of an object
        (works only for 2 and 3 dims so far)
        """
        def prepare_convert(array):
            return np.flip(array.transpose(), axis=tuple(range(array.ndim - 1)))

        def str_2d_matrix(matrix):
            rows = str(matrix).split("\n")
            rows.insert(0, "Y ")
            rows.insert(1, "^ ")
            rows[2:] = ["| " + row for row in rows[2:]]
            rows.append("+" + "-" * (len(rows[-1])) + " > X")
            result = "\n".join(rows)
            return result

        def str_3d_tensor(tensor):
            matrices = str(tensor).split("\n\n")
            matrices = [str_2d_matrix(matrix) for matrix in matrices]
            matrices = "\n\n".join(matrices)
            matrices = matrices.split("\n")
            matrices.insert(0, "Z")
            matrices.insert(1, "^")
            matrices[2:] = ["| " + matrix for matrix in matrices[2:]]
            result = "\n".join(matrices)
            return result

        result = prepare_convert(self.__value)

        if self.__value.ndim == 3:
            result = str_3d_tensor(result)
        elif self.__value.ndim == 2:
            result = str_2d_matrix(result)

        return "{" + str(self.corner) + ",\n" + result + "}"