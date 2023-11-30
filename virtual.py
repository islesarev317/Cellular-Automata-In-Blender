import numpy as np
import mathutils
import utils as blu
import hashlib
from tensor import LocatedTensor


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
        self.__hash = None
        self.__tensor = None

    # ----------------- Computation of Tensor ----------------- #

    @property
    def hash(self):
        """ determine hash based on child objects """
        hashes = "|".join([child.hash for child in self.children])
        hash_object = hashlib.sha256(hashes.encode())
        return hash_object.hexdigest()

    @property
    def tensor(self):
        """ wrap: cause compute tensor if hash changed else use saved tensor """
        new_hash = self.hash
        if self.__hash != new_hash:
            self.__tensor = self.__compute()
            self.__hash = new_hash
        return self.__tensor

    def __compute(self):
        """ compute total tensor as result of applying operator to child tensor """
        try:
            tensors = [child.tensor for child in self.children]
            result_tensor = self.operator(*tensors)
            return result_tensor
        except AttributeError as e:
            blu.print(self.children)
            blu.print(self.operator)
            blu.print(e)
            raise e

    # ----------------- Creators on each tensor operator ----------------- #

    def __add__(self, other):
        return VirtualFunction(LocatedTensor.__add__, self, other)

    def __sub__(self, other):
        return VirtualFunction(LocatedTensor.__sub__, self, other)

    def hollow(self):
        return VirtualFunction(LocatedTensor.hollow, self)

    def fill(self, value):
        return VirtualFunction(LocatedTensor.fill, self, VirtualConstant(value))

    def minimum(self, value):
        return VirtualFunction(LocatedTensor.minimum, self, VirtualConstant(value))

    def life(self):
        return VirtualLife(self)


# ==================================== #
# ======= 2. VirtualConstant ========= #
# ==================================== #


class VirtualConstant(VirtualFunction):
    """
    The class has only one constant value instead of tensor
    """

    def __init__(self, value):
        super().__init__(None, None)  # it's a leaf, we don't have any children here
        self.value = value

    @property
    def hash(self):
        return str(self.value)

    @property
    def tensor(self):
        return self.value


# ==================================== #
# ======== 3. VirtualObject ========== #
# ==================================== #


class VirtualObject(VirtualFunction):
    """
    The class bind the 3d blender object to the python object
    and also implements function which create tensor form 3d object
    """

    distance = 100  # distance for checking point location attitude the object
    value = 1  # default value for tensor filling

    def __init__(self, obj, grain):
        super().__init__(None, None)  # it's a leaf, we don't have any children here
        self.obj = obj
        self.grain = grain

    @property
    def hash(self):
        """ count hash of the 3d object as summary of location, rotation and size of the object"""
        return blu.hash_obj(self.obj)

    @property
    def tensor(self):
        """ just a wrap """
        return self.__compute()

    def __compute(self):
        """ also a wrap """
        return self.__obj_to_tensor()

    def __is_inside(self, p):
        """ check if point is inside the 3d object """
        p = self.obj.matrix_world.inverted() @ p
        result, point, normal, face = self.obj.closest_point_on_mesh(p, distance=self.distance)
        p2 = point - p
        v = p2.dot(normal)
        return not (v < 0.0)

    def __get_real_bound_box(self):
        """ get a bound box after applying all 3d transformations """
        bb_vertices = [mathutils.Vector(v) for v in self.obj.bound_box]
        mat = self.obj.matrix_world
        world_bb_vertices = np.array([mat @ v for v in bb_vertices])
        return world_bb_vertices

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
            loc = mathutils.Vector(tuple(x * self.grain for x in tensor.point_to_global(point)))
            if self.__is_inside(loc):
                tensor[point] = self.value

        return tensor


# ==================================== #
# ========= 4. VirtualLife =========== #
# ==================================== #


class VirtualLife(VirtualFunction):
    """
    Implementation of John Conway's Game of Life
    """

    def __init__(self, function_rules):
        """ param function rules is virtual function which return tensor with rules in each cell of the tensor """
        super().__init__(None, None)  # it's a leaf, we don't have any children here
        self.function_rules = function_rules
        self.__tensor = LocatedTensor.zeros((0, 0, 0), dim=(1, 1, 1))
        self.seq = 0

    @property
    def hash(self):
        self.seq += 1
        return str(self.seq)  # todo

    @property
    def tensor(self):
        self.__tensor = self.__compute()
        return self.__tensor

    def __compute(self):
        tensor_rules = self.function_rules.tensor
        tensor_values = self.__tensor
        return self.__next_life(tensor_rules, tensor_values)

    def __next_life(self, tensor_rules, tensor_values):

        tensor_next = LocatedTensor.zeros(tuple(tensor_rules.corner), dim=tensor_rules.dim)

        for r_point in tensor_rules.all_points:
            g_point = tensor_rules.point_to_global(r_point)
            v_point = tensor_values.point_to_local(g_point)
            rule = Rule(tensor_rules[r_point])
            cell = tensor_values.get(v_point, 0)
            neighbors = tensor_values.num_alive(v_point)  # change to global!

            tensor_next[r_point] = rule.next_cell(cell, neighbors)

        return tensor_next


# ======================================================================================================================


class Rule:

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def BS_form(cls, born, survive):
        return cls()

    def next_cell(self, cell, neighbors):
        num = int(self.uid)
        binary = f"{num:0b}".rjust(26, "0")
        list_of_rules = [i for i in binary[::-1]]
        try:
            result = list_of_rules[neighbors-1]
        except IndexError as e:
            blu.print("list_of_rules: " + str(list_of_rules))
            blu.print("list_of_rules: " + str(list_of_rules))
            blu.print("neighbors: " + str(neighbors))
            raise e
        return result






