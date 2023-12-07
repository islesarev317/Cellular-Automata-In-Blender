import bpy
import sys
import os
import numpy as np

dir = os.path.dirname(bpy.data.filepath)
dir = "/".join(dir.split("/")[:-2])
if not dir in sys.path:
    sys.path.append(dir)

from instance import Instance
from virtual import VirtualObject, VirtualConstant, VirtualLife
from utils import catch_scene, clear_handlers, set_start_frame
from rule import CellRule

# ------------------------------------------------------------------------------------ #
# Limit Test. (Look at the Info Label)
# ------------------------------------------------------------------------------------ #

# scene
set_start_frame()

# params
frame_step = 5
grain = 0.5
limit_cells = 300  # Small Limit
collection = bpy.data.collections["Cells"]
default_image = bpy.data.objects["Image"]

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)


# expression
vf = cube.hollow()

# realize
instance = Instance(vf, grain, collection, default_image, limit=limit_cells,
                    bake=False, frame_step=frame_step)
instance.scale_factor = 1
instance.update()

# handler
clear_handlers()
catch_scene(instance)
