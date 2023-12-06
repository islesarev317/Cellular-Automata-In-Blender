import bpy
import mathutils
import traceback
import hashlib


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


def vector(v):
    return mathutils.Vector(v)


def copy_obj(image, name, collection):
    obj = image.copy()
    obj.name = name
    collection.objects.link(obj)
    return obj


def move_obj(obj, location):
    obj.location = location


def scale_obj(obj, scale):
    obj.scale.xyz = scale


def catch_scene(instance, frame_step):

    def inner_catch_scene(self, context):
        try:
            nonlocal instance
            nonlocal frame_step
            frame = bpy.context.scene.frame_current
            if frame % frame_step == 0:
                instance.update()
        except Exception as e:
            print("ERROR in inner_catch_scene:")
            print(traceback.format_exc())

    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(inner_catch_scene)


def clear_handlers():
    bpy.app.handlers.frame_change_pre.clear()


def current_frame():
    return bpy.context.scene.frame_current


def start_frame():
    return bpy.context.scene.frame_start


def end_frame():
    return bpy.context.scene.frame_end


def hash_obj(obj):
    location = str(obj.location)
    rotation = str(obj.rotation_euler)
    scale = str(obj.scale.xyz)
    hash_object = hashlib.sha256()
    hash_object.update(location.encode())
    hash_object.update(rotation.encode())
    hash_object.update(scale.encode())
    d = hash_object.hexdigest()
    return d


def show_label(msg, loc=(0, 0, 0)):

    collection = bpy.data.collections["Collection"]  # hardcode!

    # find
    matches = (obj for obj in collection.objects if obj.name.startswith("INFO:"))
    label = next(matches, None)

    # create
    if label is None:
        label = bpy.data.objects.new("empty", None)
        label.empty_display_type = 'PLAIN_AXES'
        label.show_name = True
        label.show_in_front = True
        collection.objects.link(label)

    # update
    label.name = "INFO: " + msg
    label.location = loc
