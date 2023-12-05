import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
dir = "/".join(dir.split("/")[:-2])
if not dir in sys.path:
    sys.path.append(dir)

from instance import Instance
from virtual import VirtualObject

# ------------------------------------------------------------------------------------ #
# Primitives.
# ------------------------------------------------------------------------------------ #

# params
frame_step = 1
grain = 0.3
limit_cells = 5000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)
cylinder = VirtualObject(bpy.data.objects["Cylinder"], grain)
sphere = VirtualObject(bpy.data.objects["Sphere"], grain)
bar = VirtualObject(bpy.data.objects["Bar"], grain)
cone = VirtualObject(bpy.data.objects["Cone"], grain)

# expression
vf = cube.diff(cylinder).union(sphere).diff(bar).union(cone)
vf = vf.hollow()

# realize
instance = Instance(vf, grain, collection, default_image, limit=limit_cells)
instance.scale_factor = 0.95
instance.update()
