# Don't forget to clean unlinked meshes: File > Clean Up > Unused Data Blocks

import bpy
import math
import random
from time import time
from datetime import datetime

# ------------------------------------------
# bPrint
# ------------------------------------------

def bPrint(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                data = "blender script: " + data
                bpy.ops.console.scrollback_append(override, text=str(data), type="OUTPUT")

# ------------------------------------------
bPrint("------------ START ------------")
bPrint("(0) DECLARE VARS".ljust(31, "-"))
first_time = time()
stage_time = time()
# ------------------------------------------

n = 15 # not over 20
step_count = 20
step_delta = 10

# ------------------------------------------
bPrint("| --- time = %s" % datetime.now().strftime("%H:%M:%S"))
bPrint(f"| --- n = {n}, steps = {step_count}")
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("(1) DECLARE MATRIX ".ljust(31, "-"))
stage_time = time()
# ------------------------------------------

current_frame = 0
grid = [[[None for i in range(n)] for j in range(n)] for k in range(n)]
offsets = [(i, j, k) for i in range(-1,2) for j in range(-1,2) for k in range(-1,2) if not (i==j==k==0)]

# ------------------------------------------
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("(2) PREPARING ".ljust(31, "-"))
stage_time = time()
# ------------------------------------------

bpy.context.scene.frame_end = step_count * step_delta
bpy.ops.object.select_all()
bpy.ops.object.delete()
bpy.ops.outliner.orphans_purge()

# ------------------------------------------
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("(3) CUBE FOR COPY ".ljust(31, "-"))
stage_time = time()
# ------------------------------------------

bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 0, 0))
cube_for_copy = bpy.context.active_object

# ------------------------------------------
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("(4) INIT GRID ".ljust(31, "-"))
stage_time = time()
# ------------------------------------------

for i in range(n):
        for j in range(n):
            for k in range(n):
                random_state = random.choice([0, 0, 1])
                grid[i][j][k] = cube_for_copy.copy()
                grid[i][j][k].data = cube_for_copy.data.copy()
                grid[i][j][k].location = (i, j, k)
                grid[i][j][k].scale.xyz = random_state
                grid[i][j][k]["state"] = random_state
                grid[i][j][k]["previous"] = random_state
                grid[i][j][k].keyframe_insert("scale", frame=current_frame)
                bpy.context.collection.objects.link(grid[i][j][k])

# ------------------------------------------
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("(5) CALCULATE ANIMATION ".ljust(31, "-"))
stage_time = time()
# ------------------------------------------

for step in range(step_count):
    current_frame += step_delta
    for i in range(n):
            for j in range(n):
                for k in range(n):
                    current_cube = grid[i][j][k]
                    current_cube["previous"] = current_cube["state"]
                    neighbours = 0
                    for delta in offsets:
                        x = i + delta[0]
                        y = j + delta[1]
                        z = k + delta[2]
                        if (0 <= x < n) and (0 <= y < n) and (0 <= z < n):
                            neighbours += grid[x][y][z]["previous"]
                    if current_cube["previous"] == 0 and neighbours == 4:
                        current_cube["state"] = 1
                        current_cube.scale.xyz = 1
                        current_cube.keyframe_insert("scale", frame=current_frame)
                    elif current_cube["previous"] == 1 and neighbours not in [4,5]:
                        current_cube["state"] = 0
                        current_cube.scale.xyz = 0
                        current_cube.keyframe_insert("scale", frame=current_frame)
                    else:
                        # you can comment line below and get interesting effect
                        current_cube.keyframe_insert("scale", frame=current_frame)

# ------------------------------------------
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("(6) UNLINK CUBE ".ljust(31, "-"))
stage_time = time()
# ------------------------------------------

for collection in cube_for_copy.users_collection:
    collection.objects.unlink(cube_for_copy)

# ------------------------------------------
bPrint("| --- seconds = " + str(round(time() - stage_time, 3)))
bPrint("| --- time = %s" % datetime.now().strftime("%H:%M:%S"))
bPrint("| --- total seconds = " + str(round(time() - first_time, 3)))
bPrint("------------ END --------------")
# ------------------------------------------
