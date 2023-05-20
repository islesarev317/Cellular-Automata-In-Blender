# Don't forget to clean unlinked meshes: File > Clean Up > Unused Data Blocks

import bpy
import math
import random

# vars

n = 5
grid = [[[None for i in range(n)] for j in range(n)] for k in range(n)]
offsets = [(i, j, k) for i in range(-1,2) for j in range(-1,2) for k in range(-1,2) if not (i==j==k==0)]
current_frame = 0
step_count = 10
step_delta = 10
bpy.context.scene.frame_end = step_count * step_delta

# init

for i in range(n):
        for j in range(n):
            for k in range(n):
                random_state = random.choice([0, 1])
                bpy.ops.mesh.primitive_cube_add(size=1, location=(i, j, k))
                grid[i][j][k] = bpy.context.active_object
                grid[i][j][k].scale.xyz = random_state
                grid[i][j][k]["state"] = random_state
                grid[i][j][k]["previous"] = random_state
                grid[i][j][k].keyframe_insert("scale", frame=current_frame)

# next

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
                    print("neighbours: " + str(neighbours))
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
