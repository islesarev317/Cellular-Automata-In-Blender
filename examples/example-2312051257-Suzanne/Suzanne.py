import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
dir = "/".join(dir.split("/")[:-2])
if not dir in sys.path:
    sys.path.append(dir)

import imp
import instance
import virtual

imp.reload(instance)  # reload needs for usage in blender
imp.reload(virtual)

from instance import Instance
from virtual import VirtualObject

# ------------------------------------------------------------------------------------ #
# Suzanne.
# (In this example, I manually removed some noise around Suzanne,
# which was due to tricky Suzanne's geometry.)
# ------------------------------------------------------------------------------------ #

# params
frame_step = 1
grain = 0.3
limit_cells = 5000
collection = bpy.data.collections["Cells"]  # collection for cells (need to be created before script starting)
default_image = bpy.data.objects["Image"]  # object from which cells will be copied (need to be created beforehand)

# objects
suzanne = VirtualObject(bpy.data.objects["Suzanne"], grain).hollow()  # using hollow for optimization

# realize
instance = Instance(suzanne, grain, collection, default_image, limit=limit_cells)
instance.scale_factor = 0.9
instance.update()
