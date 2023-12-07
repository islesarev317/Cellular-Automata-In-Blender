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
# 3d Cellular Automata.
# ------------------------------------------------------------------------------------ #

# scene
set_start_frame()

# params
frame_step = 10
grain = 0.5
limit_cells = 2000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)
sphere = VirtualObject(bpy.data.objects["Sphere"], grain)

# rule
code = CellRule.get_code(ndim=3, birth_cond=[5, 6], survive_cond=[2, 3, 4])

# expression
vf_init = sphere.random_fill([0, 1]).mirror()
vf_rules = cube.fill(code)
vf_life = VirtualLife(vf_rules, vf_init)

# realize
instance = Instance(vf_life, grain, collection, default_image, limit=limit_cells,
                    bake=True, frame_step=frame_step)
instance.scale_factor = 1
instance.update()

# handler
clear_handlers()
catch_scene(instance)
