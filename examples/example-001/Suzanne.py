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

imp.reload(instance)
imp.reload(virtual)

from instance import Instance
from virtual import VirtualObject

# =============================

# params
frame_step = 1
grain = 0.3
limit_cells = 5000
collection = bpy.data.collections["Cells"]
default_image = bpy.data.objects["Image"]

# objects
suzanne = VirtualObject(bpy.data.objects["Suzanne"], grain).hollow()

# realize
instance = Instance(suzanne, grain, collection, default_image, limit=limit_cells)
instance.scale_factor = 0.9
instance.update()
