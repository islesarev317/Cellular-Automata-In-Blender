import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import tensor
import utils
import virtual
import instance
import imp

imp.reload(tensor)
imp.reload(utils)
imp.reload(virtual)
imp.reload(instance)

from instance import Instance
from virtual import VirtualObject
from utils import catch_scene, clear_collection

# =============================

# params
frame_step = 4
grain = 0.5
collection = bpy.data.collections["Collection Cells"]
image = bpy.data.objects["Image"]

# clear
clear_collection(collection)

# objects

a = VirtualObject(bpy.data.objects["Cube"], grain)
b = VirtualObject(bpy.data.objects["Ico"], grain)
c = VirtualObject(bpy.data.objects["Box"], grain)

# virtual
vf = a.hollow() - c

# realize
instance = Instance(vf, grain, collection, image, bake=True, reserve=True)
instance.scale_factor = 1

# handler
catch_scene(instance, frame_step)
# cancel_catch_scene(instance)