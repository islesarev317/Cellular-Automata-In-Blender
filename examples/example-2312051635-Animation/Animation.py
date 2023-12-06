import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
dir = "/".join(dir.split("/")[:-2])
if not dir in sys.path:
    sys.path.append(dir)

from instance import Instance
from virtual import VirtualObject
from utils import catch_scene, clear_handlers

# ------------------------------------------------------------------------------------ #
# Primitives.
# (catch_scene handler doesn't save with blender file, so we need to launch the script)
# ------------------------------------------------------------------------------------ #

# params
grain = 0.4
limit_cells = 2000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)

# expression
vf = cube

# realize
instance = Instance(vf, grain, collection, default_image, limit=limit_cells)
instance.scale_factor = 0.9
instance.update()

# handler
clear_handlers()
catch_scene(instance)
