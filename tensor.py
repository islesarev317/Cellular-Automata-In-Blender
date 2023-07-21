import numpy as np
import utils as blu
from copy import copy


class LocatedTensor:

    def __init__(self, corner, value):
        assert isinstance(corner, tuple), "Init exception: Arg corner must be a tuple"
        assert isinstance(value, np.ndarray), "Init exception: Arg value must be an ndarray"
        assert len(corner) == value.ndim, "Init exception: Len of corner must fit ndim of value"
        assert len(corner) in [2, 3], "Init exception: Dim must be either 2 or 3"

        self.__corner = np.array(corner)
        self.__value = value.copy()

    @classmethod
    def zeros(cls, corner, *, dim):
        value = np.zeros(dim)
        return cls(corner, value)

    def __getitem__(self, key):
        return self.__value[key]

    def __setitem__(self, key, value):
        self.__value[key] = value

    def __str__(self):
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

    @property
    def all_points(self):
        return np.ndindex(self.dim)

    @property
    def not_null_points(self):
        return list(zip(*np.nonzero(self.__value != 0)))

    @property
    def dim(self):
        return self.__value.shape

    @property
    def corner(self):
        return self.__corner

    @property
    def opp_corner(self):
        return self.corner + self.dim - 1

    def point_to_global(self, point):
        return tuple(point + self.corner)

    def point_to_local(self, point):
        return tuple(point - self.corner)

    def get(self, point, default):
        try:
            return self[point]
        except IndexError:
            return default

    @classmethod
    def __base_ops(cls, T1, T2, ops):
        corner = tuple(np.vstack((T1.corner, T2.corner)).min(axis=0))
        dim = tuple(np.vstack((T1.opp_corner, T2.opp_corner)).max(axis=0) - corner + 1)
        result = cls.zeros(corner, dim=dim)

        for i, t in [(0, T1), (1, T2)]:
            for point in t.all_points:
                rlp = result.point_to_local(t.point_to_global(point))
                a = result[rlp]
                b = t[point]
                c = a + b if i == 0 else ops(a, b)
                result[rlp] = c

        return result

    @classmethod
    def union(cls, T1, T2):
        return cls.__base_ops(T1, T2, lambda a, b: a + b)

    @classmethod
    def diff(cls, T1, T2):
        return cls.__base_ops(T1, T2, lambda a, b: a - b)

    def __add__(self, t):
        return self.__base_ops(self, t, lambda a, b: a + b)

    def __sub__(self, t):
        return self.__base_ops(self, t, lambda a, b: 0 if b != 0 else a)

    def __copy__(self):
        return LocatedTensor(tuple(self.__corner.copy()), self.__value.copy())

    def copy(self):
        return LocatedTensor(tuple(self.__corner.copy()), self.__value.copy())

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

    def set(self, value):
        # blu.print("set:::" + str(self))
        result = copy(self)
        for point in result.not_null_points:
            result[point] = value
        return result

    def num_alive(self, point):
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
