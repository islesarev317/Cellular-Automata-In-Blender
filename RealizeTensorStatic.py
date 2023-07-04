import bpy


class InstanceBase:

    cell_name = "Cell"
    scale_factor = 0.9

    def __init__(self, tensor, grain, collection, default_image):
        self.__tensor = tensor
        self.__grain = grain
        self.__collection = collection
        self.__default_image = default_image
        self.__images = {}
        self.__all_objects = []

    def realize(self):
        for point in self.__tensor.all_points:
            value = self.__tensor[point]
            if value != 0:
                image = self.__images.get(value, self.__default_image)
                if image:
                    obj = image.copy()
                    obj.location = tuple(x * self.__grain for x in self.__tensor.point_to_global(point))
                    obj.scale.xyz = self.__grain * self.scale_factor
                    obj.name = self.cell_name
                    self.__collection.objects.link(obj)
                    self.__all_objects.append(obj)

    def add_image(self, value, obj):
        self.__images[value] = obj

    def clear(self):
        for obj in self.__all_objects:
            bpy.data.objects.remove(obj, do_unlink=True)
        self.__all_objects.clear()
