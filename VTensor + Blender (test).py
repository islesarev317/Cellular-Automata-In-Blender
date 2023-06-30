import bpy
import numpy as np
import mathutils
import sys, os
import traceback


class VTensor:

    def __init__(self, corner, dim):
        self.corner = np.array(corner)  # array [x, y, z]
        self.value = np.zeros(np.flip(dim))  # array [[[ 0, ... , 0 ]]]

    def __getitem__(self, key):
        fkey = tuple(np.flip(key))
        return self.value[fkey]

    def __setitem__(self, key, value):
        fkey = tuple(np.flip(key))
        self.value[fkey] = value

    def __str__(self):
        return "{" + str(self.corner) + ",\n" + str(np.flip(self.value, axis=0)) + "}"

    @property
    def dim(self):
        return tuple(np.flip(self.value.shape))

    @property
    def oppCorner(self):
        return self.corner + self.dim - 1

    def pointToGlobal(self, point):
        return point + self.corner

    def pointToLocal(self, point):
        return point - self.corner

    @staticmethod
    def union(T1, T2):
        corner = np.vstack((T1.corner, T2.corner)).min(axis=0)
        dim = np.vstack((T1.oppCorner, T2.oppCorner)).max(axis=0) - corner + 1
        res = VTensor(corner, dim)

        for point in np.ndindex(T1.dim):
            res[res.pointToLocal(T1.pointToGlobal(point))] += T1[point]

        for point in np.ndindex(T2.dim):
            res[res.pointToLocal(T2.pointToGlobal(point))] += T2[point]

        return res


# ====================================================================================

class Instance:

    def __init__(self, grain, createObj, updateObj):

        self.active_objects = {}
        self.all_objects = {}
        self.grain = grain

        # functions
        self.createObj = createObj
        self.updateObj = updateObj

    def update(self, tensor):

        active = set(self.active_objects.keys())
        all = set(self.all_objects.keys())
        t = set(tuple(tensor.pointToGlobal(p)) for p in np.ndindex(tensor.dim) if tensor[p] != 0)

        decrease = active - t
        increase = t - active
        create = increase - all

        # decrease
        for p in decrease:
            obj = self.active_objects.pop(p)
            val = 0
            self.updateObj(obj, val, self.grain)

        # create
        for p in create:
            val = tensor[tensor.pointToLocal(p)]
            location = tuple(np.array(p) * self.grain)
            self.all_objects[p] = self.createObj(location, val, self.grain)

        # increase
        for p in increase:
            obj = self.all_objects[p]
            val = tensor[tensor.pointToLocal(p)]
            self.active_objects[p] = obj
            self.updateObj(obj, val, self.grain)


# ====================================================================================

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                data = "blender script: " + str(data)
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")


# ====================================================================================

def addCube(location, size, name, collection):
    try:
        cubeForCopy = bpy.data.objects["cubeForCopy"]
    except KeyError:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 0, 0))
        cubeForCopy = bpy.context.active_object
        cubeForCopy.name = "cubeForCopy"

    newCube = cubeForCopy.copy()
    newCube.location = location
    newCube.scale.xyz = size
    newCube.name = name
    collection.objects.link(newCube)
    return newCube


# ====================================================================================

def isInside(p, obj):
    p = obj.matrix_world.inverted() @ p
    result, point, normal, face = obj.closest_point_on_mesh(p, distance=100)
    p2 = point - p
    v = p2.dot(normal)
    return not (v < 0.0)


# ====================================================================================

def getRealBoundBox(obj):
    bb_vertices = [mathutils.Vector(v) for v in obj.bound_box]
    mat = obj.matrix_world
    world_bb_vertices = np.array([mat @ v for v in bb_vertices])
    return world_bb_vertices


# ====================================================================================

def objToTensor(obj, grain, carve=True):
    realBoundBox = getRealBoundBox(obj)
    minCorner = realBoundBox.min(axis=0)
    maxCorner = realBoundBox.max(axis=0)
    realDim = maxCorner - minCorner
    realCorner = minCorner
    padding = (realDim % grain) / 2
    firstCell = realCorner + (grain / 2) + padding
    dim = np.int64(realDim // grain)
    corner = np.int64((firstCell / grain).round())
    tensor = VTensor(corner, dim)

    if carve:
        for point in np.ndindex(tensor.dim):
            loc = mathutils.Vector(tuple(tensor.pointToGlobal(point) * grain))
            if isInside(loc, obj):
                tensor[point] = 1

    return tensor


# ====================================================================================

def clearCollection(collection):
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


# ====================================================================================

def CreateObj(location, val, grain):
    size = grain
    name = "Cell"
    collection = bpy.data.collections["Collection Cubes"]
    return addCube(location, size, name, collection)


# ====================================================================================

def UpdateObj(obj, val, grain):
    obj.scale.xyz = 0 if val == 0 else grain


# ====================================================================================

def getUpdateScene():
    # ico = bpy.data.objects["Icosphere"]
    cube = bpy.data.objects["Cube"]
    grain = 0.7
    instance = Instance(grain, CreateObj, UpdateObj)

    def updateScene(self, context):

        try:

            # nonlocal ico
            nonlocal cube
            nonlocal grain
            nonlocal instance

            tensorCube = objToTensor(cube, grain)
            # tensorIco = objToTensor(ico, grain)
            # tensorSum = VTensor.union(tensorCube, tensorIco)

            # instance.update(tensorSum)
            instance.update(tensorCube)

            bpy.ops.object.select_all(action='DESELECT')

        except Exception as e:
            print("---")
            print(traceback.format_exc())

    return updateScene


# ====================================================================================

clearCollection(bpy.data.collections["Collection Cubes"])

updateScene = getUpdateScene()

bpy.app.handlers.frame_change_pre.clear()
bpy.app.handlers.frame_change_pre.append(updateScene)




