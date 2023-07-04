import bpy
import numpy as np


class StaticRealizeTensor:
    cell_name = "Cell"
    scale = 0.9

    def __init__(self, tensor, grain, collection):
        self.tensor = tensor
        self.grain = grain
        self.collection = collection
        self.all_objects = []
        self.default_image = None
        self.images = {}
        self.fill_images()
        self.realize()

    def realize(self):
        for point in np.ndindex(self.tensor.dim):
            value = self.tensor[point]
            if value != 0:
                location = tuple(np.array(self.tensor.point_to_global(point)) * self.grain)
                image = self.images.get(value, self.default_image)
                obj = image.copy()
                obj.location = location
                obj.scale.xyz = self.grain * self.scale
                obj.name = self.cell_name
                self.collection.objects.link(obj)
                self.all_objects.append(obj)

    @staticmethod
    def get_image(name, func):
        try:
            image = bpy.data.objects[name]
        except KeyError:
            func()
            image = bpy.context.active_object
            image.name = name
        return image

    def fill_images(self):
        f1 = lambda: bpy.ops.mesh.primitive_cube_add(size=1, location=(10, 0, 0))
        self.default_image = self.get_image("DefaultImage", f1)

        f2 = lambda: bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=(10, 0, 0))
        self.images[2] = self.get_image("icoImage", f2)

        f3 = lambda: bpy.ops.mesh.primitive_torus_add(location=(0, 0, 0), major_segments=3, minor_segments=6)
        self.images[3] = self.get_image("TorusImage", f3)

    def clear(self):
        for obj in self.all_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.all_objects.clear()
        for image in self.images.values():
            bpy.data.objects.remove(image, do_unlink=True)
        self.images.clear()