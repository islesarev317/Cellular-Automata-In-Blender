import numpy as np
try:
    import utils as blu
except ImportError:
    pass  # utils module works only inside blender, so we skip it for the test purposes
import hashlib
from tensor import LocatedTensor
from copy import copy
from rule import CellRule


# ==================================== #
# ======= 1. VirtualFunction ========= #
# ==================================== #


class VirtualFunction:
    """
    The class implements a function consists from the list of elements and the operator.
    Each instance of class cam include another instance of the same class as child element.
    """

    # ----------------- Creator ----------------- #

    def __init__(self, operator, *children):
        self.operator = operator
        self.children = children
        self._hash = None
        self._tensor = None

    # ----------------- Computation of Tensor ----------------- #

    def hash(self):
        """ determine hash based on child objects """
        hashes = "|".join([child.hash() for child in self.children])
        hash_object = hashlib.sha256(hashes.encode())
        return hash_object.hexdigest()

    def tensor(self):
        """ wrap: cause compute tensor if hash changed else use saved tensor """
        new_hash = self.hash()
        if self._hash != new_hash:
            self._tensor = self.compute()
            self._hash = new_hash
        return self._tensor

    def compute(self):
        """ compute total tensor as result of applying operator to child tensor """
        try:
            tensors = [child.tensor() for child in self.children]
            result_tensor = self.operator(*tensors)
            return result_tensor
        except AttributeError as e:
            print(self.children)
            print(self.operator)
            print(e)
            try:
                blu.print(self.children)
                blu.print(self.operator)
                blu.print(e)
            except NameError:
                pass  # for manual test, because we have blu module only inside blender
            raise e

    # ----------------- Creators on each tensor operator ----------------- #

    def __add__(self, other):
        return VirtualFunction(LocatedTensor.__add__, self, other)

    def __sub__(self, other):
        return VirtualFunction(LocatedTensor.__sub__, self, other)
    
    def cross(self, other):
        return VirtualFunction(LocatedTensor.cross, self, other)

    def union(self, other):
        return VirtualFunction(LocatedTensor.union, self, other)

    def diff(self, other):
        return VirtualFunction(LocatedTensor.diff, self, other)

    def __rshift__(self, other):
        return VirtualFunction(LocatedTensor.__rshift__, self, other)

    def __lshift__(self, other):
        return VirtualFunction(LocatedTensor.__lshift__, self, other)

    def minimum(self, value):
        return VirtualFunction(LocatedTensor.minimum, self, VirtualConstant(value))

    def maximum(self, value):
        return VirtualFunction(LocatedTensor.maximum, self, VirtualConstant(value))

    def fill(self, value):
        return VirtualFunction(LocatedTensor.fill, self, VirtualConstant(value))

    def random_fill(self, values, weights=None):
        return VirtualFunction(LocatedTensor.random_fill, self, VirtualConstant(values), VirtualConstant(weights))

    def hollow(self):
        return VirtualFunction(LocatedTensor.hollow, self)

    def life(self):
        return VirtualLife(self)

    def mirror(self):
        return VirtualFunction(LocatedTensor.mirror, self)


# ==================================== #
# ======= 2. VirtualConstant ========= #
# ==================================== #


class VirtualConstant(VirtualFunction):
    """
    The class has only one constant value instead of tensor
    """

    def __init__(self, value):
        super().__init__(None, None)  # it's a leaf, we don't have any children here
        self.__value = value  # it can be single int value or ndarray tensor, so we don't use __tensor

    def hash(self):
        hash_object = hashlib.sha256(str(self.__value).encode())
        return hash_object.hexdigest()

    def tensor(self):
        return self.__value


# ==================================== #
# ======== 3. VirtualObject ========== #
# ==================================== #


class VirtualObject(VirtualFunction):
    """
    The class bind the 3d blender object to the python object
    and also implements function which create tensor form 3d object
    """

    distance = 100  # distance for checking point location attitude the object
    value = 1  # default value to fill tensor

    def __init__(self, obj, grain):
        super().__init__(None, None)  # it's a leaf, we don't have any children here
        self.obj = obj
        self.grain = grain

    def hash(self):
        """ count hash of the 3d object as summary of location, rotation and size of the object"""
        return blu.hash_obj(self.obj)

    def tensor(self):
        """ wrap: cause compute tensor if hash changed else use saved tensor """
        new_hash = self.hash()
        if self._hash != new_hash:
            self._tensor = self.compute()
            self._hash = new_hash
        return self._tensor

    def compute(self):
        """ just a wrap """
        return self.__obj_to_tensor()

    def __obj_to_tensor(self):
        """ transform object to tensor """
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
            loc = blu.vector(tuple(x * self.grain for x in tensor.point_to_global(point)))
            if self.__is_inside(loc):
                tensor[point] = self.value

        return tensor

    def __is_inside(self, p):
        """ check if point is inside the 3d object """
        p = self.obj.matrix_world.inverted() @ p
        result, point, normal, face = self.obj.closest_point_on_mesh(p, distance=self.distance)
        p2 = point - p
        v = p2.dot(normal)
        return not (v < 0.0)

    def __get_real_bound_box(self):
        """ get a bound box after applying all 3d transformations """
        bb_vertices = [blu.vector(v) for v in self.obj.bound_box]
        mat = self.obj.matrix_world
        world_bb_vertices = np.array([mat @ v for v in bb_vertices])
        return world_bb_vertices


# ==================================== #
# ========= 4. VirtualLife =========== #
# ==================================== #


class VirtualLife(VirtualFunction):
    """
    Implementation of John Conway's Game of Life
    """

    def __init__(self, rules_function, initial_function=None, lifetime=False):
        """
        param virtual_function is virtual function which return tensor with rules in each cell of the tensor
        param initial_function is virtual function which return tensor for initialization __tensor_values
        """
        super().__init__(None, None)  # we use self.virtual_function for the only children
        self.rules_function = rules_function
        self.initial_function = initial_function
        self.lifetime = lifetime
        self.__tensor_rules = None
        self.__tensor_values = None
        self.seq = 0

    def hash(self):
        """ send different hash each time because we need to recalculate tensor each time """
        return str(self.seq)

    def tensor(self):
        """ just a wrap """
        return self.compute()

    def compute(self):
        """ compute rules, initial values, next life and keep results """
        self.__tensor_rules = self.rules_function.tensor()
        self.seq += 1
        if self.seq == 1:
            if self.initial_function:
                self.__tensor_values = self.initial_function.tensor()  # set initial values
                return self.__tensor_values
            else:
                self.__tensor_values = copy(self.__tensor_rules)  # we can have no values at first step
                self.__tensor_values[:] = 0  # or .fill(0) ?
        apply_func = CellRule.apply_rule_lifetime if self.lifetime else CellRule.apply_rule_binary
        self.__tensor_values = self.__tensor_values.next_life(self.__tensor_rules, apply_func)
        return self.__tensor_values
