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
# Baking.
# (creating keyframes for animation's optimization)
# ------------------------------------------------------------------------------------ #

# params
frame_step = 5
grain = 0.35
limit_cells = 2000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)

# expression
vf = cube.hollow()

# realize
instance = Instance(vf, grain, collection, 
                    default_image, limit=limit_cells, bake=True, frame_step=frame_step)
instance.scale_factor = 0.9
instance.update()

# handler
clear_handlers()
catch_scene(instance)
