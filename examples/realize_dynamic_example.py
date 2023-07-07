import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

import tensor
import utils
from old import realize_dynamic

import imp

imp.reload(tensor)
imp.reload(utils)
imp.reload(realize_dynamic)

from tensor import LocatedTensor
from utils import print
from old.realize_dynamic import InstanceDynamic

# =============================================================

a = LocatedTensor.zeros(corner=(1, 1, 1), dim=(5, 4, 3))
a[1:4, 0:3] = 1
a.hollow()
#print(a)

b = LocatedTensor.zeros(corner=(3, 3, 2), dim=(3, 3, 3))
b[:] = 3
#print(b)

c = LocatedTensor.union(a, b)
print(c)

collection = bpy.data.collections["Collection"]
default_image = bpy.data.objects["Cube"]
grain = 0.5

instance = InstanceDynamic(grain, collection, default_image)
instance.update(a)
instance.update(b)

