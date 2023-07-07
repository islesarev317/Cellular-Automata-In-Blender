import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import tensor
import utils
from old import realize_dynamic, realize_static
import obj_to_tensor

import imp

imp.reload(tensor)
imp.reload(utils)
imp.reload(realize_static)
imp.reload(realize_dynamic)
imp.reload(obj_to_tensor)

from old.realize_static import InstanceStatic
from obj_to_tensor import obj_to_tensor

# =============================================================

collection = bpy.data.collections["Collection"]
target = bpy.data.objects["Target"]
default_image = bpy.data.objects["Cube"]
grain = 0.3

tensor = obj_to_tensor(target, grain)
instance = InstanceStatic(tensor, grain, collection, default_image)
instance.realize()
