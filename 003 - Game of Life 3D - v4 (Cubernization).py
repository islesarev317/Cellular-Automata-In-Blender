import bpy
import numpy as np
import mathutils

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                data = "blender script: " + str(data)
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")
                
                
def addCube(location, size):
    try:
        cubeForCopy = bpy.data.objects["cubeForCopy"]
    except KeyError:
        bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 0, 0))
        cubeForCopy = bpy.context.active_object
        cubeForCopy.name = "cubeForCopy"
    
    newCube = cubeForCopy.copy()
    newCube.location = location
    newCube.scale.xyz = size
    newCube.name = "Cell"
    bpy.context.collection.objects.link(newCube)    
    return newCube
    
    
def is_inside(p, obj):
    result, point, normal, face = obj.closest_point_on_mesh(p, distance=100)
    p2 = point-p 
    v = p2.dot(normal)
    return not(v < 0.0)


def nonameFunc(cellSize, boundBox, *objList):

    dim = np.array([int(v // cellSize) for v in boundBox.dimensions])
    area = np.zeros(dim)
    cornerPoint = np.array(boundBox.bound_box[0]) + np.array(boundBox.location) + cellSize/2
    
    for cell in np.ndindex(area.shape):
        cellLoc = np.array(cell) * cellSize + cornerPoint
        vCellLoc = mathutils.Vector((cellLoc[0], cellLoc[1], cellLoc[2]))
        
        for obj in objList:        
            if is_inside(vCellLoc, obj):
                area[cell] = 1                
                
        if area[cell] == 1:
            newCube = addCube(location=cellLoc, size=cellSize)
        
nonameFunc(0.5, bpy.data.objects["Box"], bpy.data.objects["Icosphere"], bpy.data.objects["Cube"])



    
    