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
from utils import catch_scene, clear_handlers
from rule import CellRule
from tensor import LocatedTensor

# ------------------------------------------------------------------------------------ #
# Game of Life (2d). Random initial set.
# After baking animation we can change Interpolation Mode for keys
# Cells collection => Select objects => Animation tab => Key => Interpolation mode 
# ------------------------------------------------------------------------------------ #

# params
frame_step = 10
grain = 0.5
limit_cells = 2000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
init_tensor = LocatedTensor.binary_random(dim=(15, 15, 1), density=0.25)
init_constant = VirtualConstant(init_tensor)
code_life_rule = CellRule.get_code(3, [3], [2, 3])
rule_constant = VirtualConstant(code_life_rule)

# expression
vf = VirtualLife(rule_constant, init_constant)

# realize
instance = Instance(vf, grain, collection, default_image, limit=limit_cells,
                    bake=True, frame_step=frame_step)
instance.scale_factor = 0.9
instance.update()

# handler
clear_handlers()
catch_scene(instance)
