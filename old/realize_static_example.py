import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import tensor
import utils
from old import realize_static

import imp

imp.reload(tensor)
imp.reload(utils)
imp.reload(realize_static)

from tensor import LocatedTensor
from utils import print
from old.realize_static import InstanceStatic

# =============================================================

a = LocatedTensor.zeros(corner=(1, 1, 1), dim=(5, 4, 3))
a[1:4, 0:3] = 1
a.hollow()

b = LocatedTensor.zeros(corner=(3, 3, 2), dim=(3, 3, 3))
b[:] = 3

c = LocatedTensor.union(a, b)
print(c)

collection = bpy.data.collections["Collection"]
default_image = bpy.data.objects["Icosphere"]
grain = 0.5

instance = InstanceStatic(c, grain, collection, default_image)
instance.add_image(1, bpy.data.objects["Cube"])
instance.add_image(3, bpy.data.objects["Torus"])
instance.add_image(4, bpy.data.objects["Diamond"])
instance.realize()
