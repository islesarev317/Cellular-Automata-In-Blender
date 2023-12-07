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
grain = 0.3
limit_cells = 5000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)
sphere = VirtualObject(bpy.data.objects["Sphere"], grain)
half = VirtualObject(bpy.data.objects["Half"], grain)

# rule
code = CellRule.get_code(ndim=3, birth_cond=list(range(6, 10)), survive_cond=list(range(9, 22)))

# expression
vf_init = sphere.mirror()
vf_rules = cube.fill(code)
vf_life = VirtualLife(vf_rules, vf_init, lifetime=True).diff(half)

# realize
instance = Instance(vf_life, grain, collection, default_image, limit=limit_cells,
                    bake=True, frame_step=frame_step, provide_prop=True)
instance.scale_factor = 0.9
instance.update()

# handler
clear_handlers()
catch_scene(instance)
