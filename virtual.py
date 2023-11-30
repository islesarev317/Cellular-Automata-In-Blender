import numpy as np
import mathutils
import utils as blu
import hashlib
from copy import copy
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

    def hash(self):
        """ determine hash based on child objects """
        hashes = "|".join([child.hash() for child in self.children])
        hash_object = hashlib.sha256(hashes.encode())
        return hash_object.hexdigest()

    def tensor(self):
        """ wrap: cause compute tensor if hash changed else use saved tensor """
        new_hash = self.hash()
        if self.__hash != new_hash:
            self.__tensor = self.__compute()
            self.__hash = new_hash
        return self.__tensor

    def __compute(self):
        """ compute total tensor as result of applying operator to child tensor """
        try:
            tensors = [child.tensor() for child in self.children]
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

    def hash(self):
        """ count hash of the 3d object as summary of location, rotation and size of the object"""
        return blu.hash_obj(self.obj)

    def tensor(self):
        """ wrap: cause compute tensor if hash changed else use saved tensor """
        new_hash = self.hash()
        if self.__hash != new_hash:
            self.__tensor = self.__compute()
            self.__hash = new_hash
        return self.__tensor

    def __compute(self):
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
            loc = mathutils.Vector(tuple(x * self.grain for x in tensor.point_to_global(point)))
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
        bb_vertices = [mathutils.Vector(v) for v in self.obj.bound_box]
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

    def __init__(self, virtual_function):
        """ param function rules is virtual function which return tensor with rules in each cell of the tensor """
        super().__init__(None, None)  # we use self.virtual_function for the only children
        self.virtual_function = virtual_function
        self.__tensor_rules = None
        self.__tensor_values = None
        self.seq = 0

    def hash(self):
        """ send different hash each time because we need to recalculate tensor each time """
        self.seq += 1
        return str(self.seq)

    def tensor(self):
        """ just a wrap """
        return self.__compute()

    def __compute(self):
        """ compute rules, next life and keep results """
        self.__tensor_rules = self.virtual_function.tensor()
        self.__tensor_values = self.__next_life( self.__tensor_rules, self.__tensor_values)
        return self.__tensor_values

    def __next_life(self, tensor_rules, tensor_values):
        """  apply cellular automata rules to tensor and return next tensor state """

        def apply_rule(rule, value, neighbor_count):
            """ apply cellular automata rule to one cell and return next cell state """
            cell_rule_binary = f"{int(rule):0b}".rjust(26, "0")
            list_of_rules = [i for i in cell_rule_binary[::-1]]
            try:
                result = list_of_rules[neighbor_count - 1]
            except IndexError as e:
                blu.print("list_of_rules: " + str(list_of_rules))
                blu.print("neighbors: " + str(neighbor_count))
                raise e
            return result

        tensor_next = LocatedTensor.zeros(tuple(tensor_rules.corner), dim=tensor_rules.dim)

        for global_point in tensor_rules.all_points_global:
            cell_rule = tensor_rules.get_global(global_point)
            if self.seq == 0:  # we don't have values at first step
                cell_value = 0
                neighbors = 0
            else:
                cell_value = tensor_values.get_global(global_point, 0)
                neighbors = tensor_values.num_alive(global_point)
            next_cell_value = apply_rule(cell_rule, cell_value, neighbors)
            tensor_next.set_global(global_point, next_cell_value)

        return tensor_next
