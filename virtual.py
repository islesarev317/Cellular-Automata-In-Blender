import numpy as np
import mathutils
from tensor import LocatedTensor


MODE_A = "a"
MODE_B = "b"


class VirtualFunction:

    def __init__(self, ops, *ff):
        self.ops = ops
        self.ff = ff
        self.__mode = None

    @property
    def mode(self):
        return self.__mode

    @mode.setter
    def mode(self, mode):
        assert mode in [None, MODE_A, MODE_B], "Incorrect value for mode"
        self.__mode = mode

    def compute(self):
        # tt = [f.compute(self.mode) for f in self.ff]
        tt = []
        for f in self.ff:
            saved_mode = f.mode
            f.mode = self.mode
            tt.append(f.compute())
            f.mode = saved_mode
        result = self.ops(*tt)
        return result

    def __add__(self, other):
        return VirtualFunction(LocatedTensor.__add__, self, other)

    def __sub__(self, other):
        return VirtualFunction(LocatedTensor.__sub__, self, other)

    def hollow(self):
        return VirtualFunction(LocatedTensor.hollow, self)


class VirtualObject(VirtualFunction):

    distance = 100

    def __init__(self, obj, grain, value=1, value_a=None, value_b=None):
        super().__init__(None, None)
        self.obj = obj
        self.grain = grain
        self.__value = value
        self.__value_a = value_a
        self.__value_b = value_b
        self.tensor = None

    @property
    def value(self):
        if self.mode is None:
            return self.__value
        if self.mode == MODE_A:
            return self.__value_a
        if self.mode == MODE_B:
            return self.__value_b

    def compute(self):
        self.tensor = self.__obj_to_tensor()
        return self.tensor

    def __is_inside(self, p):
        p = self.obj.matrix_world.inverted() @ p
        result, point, normal, face = self.obj.closest_point_on_mesh(p, distance=self.distance)
        p2 = point - p
        v = p2.dot(normal)
        return not (v < 0.0)

    def __get_real_bound_box(self):
        bb_vertices = [mathutils.Vector(v) for v in self.obj.bound_box]
        mat = self.obj.matrix_world
        world_bb_vertices = np.array([mat @ v for v in bb_vertices])
        return world_bb_vertices

    def __obj_to_tensor(self):
        real_bound_box = self.__get_real_bound_box()
        min_corner = real_bound_box.min(axis=0)
        max_corner = real_bound_box.max(axis=0)
        real_dim = max_corner - min_corner
        real_corner = min_corner
        padding = (real_dim % self.grain) / 2
        first_cell = real_corner + (self.grain / 2) + padding
        dim = tuple(np.int64(real_dim // self.grain))
        corner = tuple(np.int64((first_cell / self.grain).round()))
        tensor = LocatedTensor.zeros(corner, dim=dim)

        for point in np.ndindex(tensor.dim):
            loc = mathutils.Vector(tuple(x * self.grain for x in tensor.point_to_global(point)))
            if self.__is_inside(loc):
                tensor[point] = self.value

        return tensor




