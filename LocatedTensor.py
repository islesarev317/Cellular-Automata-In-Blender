import numpy as np


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

    @classmethod
    def __base_ops(cls, T1, T2, ops):
        corner = tuple(np.vstack((T1.corner, T2.corner)).min(axis=0))
        dim = tuple(np.vstack((T1.opp_corner, T2.opp_corner)).max(axis=0) - corner + 1)
        res = cls.zeros(corner, dim=dim)

        for t in [T1, T2]:
            for point in np.ndindex(t.dim):
                a = res[res.point_to_local(t.point_to_global(point))]
                b = t[point]
                c = ops(a, b)
                res[res.point_to_local(t.point_to_global(point))] = c

        return res

    @classmethod
    def union(cls, T1, T2):
        return cls.__base_ops(T1, T2, lambda a, b: a + b)

    @classmethod
    def diff(cls, T1, T2):
        return cls.__base_ops(T1, T2, lambda a, b: a - b)

    def hollow(self):
        """
        [[1 1 1]    [[1 1 1]
         [1 1 1] =>  [1 0 1]
         [1 1 1]]    [1 1 1]]
        """
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
                    self[point] = 0
