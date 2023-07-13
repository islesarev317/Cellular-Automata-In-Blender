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
collection = bpy.data.collections["Collection Cells"]
default_image = bpy.data.objects["Image"]

# clear
clear_collection(collection)

# objects
cube = VirtualObject(bpy.data.objects["Cube"], grain, value_a=1, value_b=1367)
ico = VirtualObject(bpy.data.objects["Ico"], grain, value_a=2, value_b=1258)
box = VirtualObject(bpy.data.objects["Box"], grain, value_a=3, value_b=444)

# virtual
virtual_function_a = (cube + ico).hollow() - box
virtual_function_a.mode = "value_a"

virtual_function_b = cube * ico / box
virtual_function_b.mode = "value_b"

virtual_life = VirtualLife(values=virtual_function_a, rules=virtual_function_b)

# realize
instance = Instance(virtual_function, grain, collection, default_image)
instance.scale_factor = 1

# handler
catch_scene(instance, frame_step)
#cancel_catch_scene(instance)



