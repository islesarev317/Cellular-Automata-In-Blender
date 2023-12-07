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
# Property.
# (we use property "value" in Image shader to color objects)
# ------------------------------------------------------------------------------------ #

# scene
set_start_frame()

# params
frame_step = 5
grain = 0.3
limit_cells = 1000  # Small Limit
collection = bpy.data.collections["Cells"]
default_image = bpy.data.objects["Image"]

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain).fill(1)  # RED!
sphere = VirtualObject(bpy.data.objects["Sphere"], grain).fill(2)  # BLUE!


# expression
vf = cube + sphere

# realize
instance = Instance(vf, grain, collection, default_image, limit=limit_cells,
                    bake=False, frame_step=frame_step, provide_prop=True)
instance.scale_factor = 0.9
instance.update()

# handler
clear_handlers()
catch_scene(instance)
