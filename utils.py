import bpy
import traceback

def print(data):
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'CONSOLE':
                override = {'window': window, 'screen': screen, 'area': area}
                output = str(data).split("\n")
                for row in output:
                    text = "blender script: " + str(row)
                    bpy.ops.console.scrollback_append(override, text=str(text), type="OUTPUT")


def remove_obj(obj):
    bpy.data.objects.remove(obj, do_unlink=True)


def clear_collection(collection):
    for obj in collection.objects:
        bpy.data.objects.remove(obj, do_unlink=True)


def normalize_factor(obj):
    return 1 / max(obj.dimensions[i] / obj.scale.xyz[i] for i in range(3))


def copy_obj(image, name, collection, location, scale):
    obj = image.copy()
    obj.location = location
    obj.scale.xyz = scale
    obj.name = name
    collection.objects.link(obj)
    return obj


def catch_scene(virtual_function, instance, frame_step):

    def inner_catch_scene(self, context):
        try:
            nonlocal virtual_function
            nonlocal instance
            nonlocal frame_step
            frame = bpy.context.scene.frame_current
            if frame % frame_step == 0:
                tensor = virtual_function.compute()
                instance.update(tensor)
        except Exception as e:
            print("ERROR in inner_catch_scene:")
            print(traceback.format_exc())

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(inner_catch_scene)




