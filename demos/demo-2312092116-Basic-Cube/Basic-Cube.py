import bpy
import sys
import os
import numpy as np
import random

dir = os.path.dirname(bpy.data.filepath)
dir = "/".join(dir.split("/")[:-2])
if not dir in sys.path:
    sys.path.append(dir)

# ------------------------------------------------------------------------------------ #
# Libs from github.com/islesarev317/Cellular-Automata-In-Blender
# ------------------------------------------------------------------------------------ #

from rule import CellRule
from virtual import VirtualObject, VirtualConstant, VirtualLife
from instance import Instance
from utils import catch_scene, clear_handlers, set_start_frame, show_label

# ------------------------------------------------------------------------------------ #
# 3D Cellular Automata in Blender. Basic cube.
# ------------------------------------------------------------------------------------ #

# preparing
set_start_frame()  # set current frame to 1

# params
frame_step = 15                             # animation step
grain = 0.3                                 # size of each cell
scale_factor = 0.9                          # to make gaps between cells
limit = 5000                                # limit of cells for preventing overload
bake = True                                 # make animation keys for optimization
collection = bpy.data.collections["Cells"]  # collection to keep cells
image = bpy.data.objects["Image"]           # object to copy cell from
info = bpy.data.collections["Info"]         # collection for info labels

# rule
code_max = CellRule.get_max_code()          # rule 18014398509481983 always keeps each cell alive
code_rand = random.randrange(code_max//100) # random rule
code_maze = 17403075121982975               # rule which makes mazes
code_cond = CellRule.get_code(birth_cond=[4, 5, 6], survive_cond=[5, 6])  # from conditions
code_range = CellRule.get_code(birth_cond=list(range(4, 9)), survive_cond=[16, 26])  # from ranges

# info
show_label("1:", "code_rand=" + str(code_rand), collection=info, hidden=True) # name of empty as message

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain)

# expression
vf_init = cube.random_fill([0, 1], weights=[0.8, 0.2])  # create cube with random values
vf_init = vf_init.mirror()
vf_rule = cube.fill(code_rand)                          # create cube with CA-rule values
vf_life = VirtualLife(vf_rule, vf_init)                 # create CA-function
 
# realize
instance = Instance(vf_life, grain, collection, image, bake, frame_step, limit)
instance.scale_factor = scale_factor
instance.label_collection = info
instance.update()

# handler
clear_handlers()
catch_scene(instance)
