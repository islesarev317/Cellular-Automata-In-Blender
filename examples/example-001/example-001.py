import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from instance import Instance
from virtual import VirtualObject
from utils import catch_scene, clear_collection

# =============================

# params
frame_step = 1
grain = 0.8
collection = bpy.data.collections["Cells"]
default_image = bpy.data.objects["Image"]

# clear
clear_collection(collection)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain).set(1)
ico = VirtualObject(bpy.data.objects["Ico"], grain).set(2)
box = VirtualObject(bpy.data.objects["Box"], grain).set(3)

# virtual
vf_a = (cube + ico).hollow() - box
vf_b = vf_a.set(1368).life()
vf_c = vf_a * vf_b

# realize
instance = Instance(vf_c, grain, collection, default_image)
instance.scale_factor = 1
instance.update()

# handler
#catch_scene(instance, frame_step)
#cancel_catch_scene(instance)



