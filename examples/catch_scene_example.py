import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from realize_dynamic import InstanceDynamic
from virtual_object import VirtualObject
from utils import catch_scene, clear_collection

# =============================

# params
frame_step = 1
grain = 0.4
collection = bpy.data.collections["Collection Cells"]
default_image = bpy.data.objects["Image"]

# clear
clear_collection(collection)

# objects
a = VirtualObject(bpy.data.objects["Cube"], grain)
b = VirtualObject(bpy.data.objects["Ico"], grain)
c = VirtualObject(bpy.data.objects["Box"], grain)

# virtual
virtual_function = (a + b).hollow() - c

# realize
instance = InstanceDynamic(grain, collection, default_image)
instance.scale_factor = 1

# handler
catch_scene(virtual_function, instance, frame_step)


