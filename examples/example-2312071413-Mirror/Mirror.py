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
from tensor import LocatedTensor

# ------------------------------------------------------------------------------------ #
# Game of Life (2d). Symmetry initial set.
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
init_tensor = LocatedTensor.binary_random(dim=(16, 16, 1), density=0.25)
code_life_rule = CellRule.get_code(3, [3], [2, 3])

# expression
vc_init = VirtualConstant(init_tensor).mirror()
vc_rules = VirtualConstant(code_life_rule)
vf = VirtualLife(vc_rules, vc_init)

# realize
instance = Instance(vf, grain, collection, default_image, limit=limit_cells,
                    bake=True, frame_step=frame_step)
instance.scale_factor = 0.9
instance.update()

# handler
clear_handlers()
catch_scene(instance)
