import numpy as np
import mathutils
from tensor import LocatedTensor

distance = 100


def is_inside(p, obj):
    p = obj.matrix_world.inverted() @ p
    result, point, normal, face = obj.closest_point_on_mesh(p, distance=distance)
    p2 = point - p
    v = p2.dot(normal)
    return not (v < 0.0)


def get_real_bound_box(obj):
    bb_vertices = [mathutils.Vector(v) for v in obj.bound_box]
    mat = obj.matrix_world
    world_bb_vertices = np.array([mat @ v for v in bb_vertices])
    return world_bb_vertices


def obj_to_tensor(obj, grain):
    real_bound_box = get_real_bound_box(obj)
    min_corner = real_bound_box.min(axis=0)
    max_corner = real_bound_box.max(axis=0)
    real_dim = max_corner - min_corner
    real_corner = min_corner
    padding = (real_dim % grain) / 2
    first_cell = real_corner + (grain / 2) + padding
    dim = tuple(np.int64(real_dim // grain))
    corner = tuple(np.int64((first_cell / grain).round()))
    tensor = LocatedTensor.zeros(corner, dim=dim)

    for point in np.ndindex(tensor.dim):
        loc = mathutils.Vector(tuple(x * grain for x in tensor.point_to_global(point)))
        if is_inside(loc, obj):
            tensor[point] = 1

    return tensor
