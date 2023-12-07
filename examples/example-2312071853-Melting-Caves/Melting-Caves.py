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
# Melting Caves.
# [Evan Wallace - cs195v](https://cs.brown.edu/courses/cs195v/projects/life/edwallac/index.html)
# ------------------------------------------------------------------------------------ #

# scene
set_start_frame()

# params
frame_step = 5
grain = 0.25
limit_cells = 12000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)

# rule
code = CellRule.get_code(ndim=3, birth_cond=list(range(14,20)), survive_cond=list(range(13,27)))

# expression
vf_init = cube.random_fill([0, 1]).mirror()
vf_rules = cube.fill(code)
vf_life = VirtualLife(vf_rules, vf_init).hollow()

# realize
instance = Instance(vf_life, grain, collection, default_image, limit=limit_cells,
                    bake=True, frame_step=frame_step)
instance.scale_factor = 1
instance.update()

# handler
clear_handlers()
catch_scene(instance)
