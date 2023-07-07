import utils as blu


class InstanceStatic:

    cell_name = "Cell"
    scale_factor = 0.99

    def __init__(self, tensor, grain, collection, default_image):
        self.__tensor = tensor
        self.__grain = grain
        self.__collection = collection
        self.__default_image = default_image
        self.__images = {}
        self.__all_objects = []

    def realize(self):
        for point in self.__tensor.not_null_points:
            value = self.__tensor[point]
            image = self.__images.get(value, self.__default_image)
            if image:
                location = tuple(x * self.__grain for x in self.__tensor.point_to_global(point))
                scale = self.__grain * self.scale_factor * blu.normalize_factor(image)
                obj = blu.copy_obj(image, self.cell_name, self.__collection, location, scale)
                self.__all_objects.append(obj)

    def add_image(self, value, obj):
        self.__images[value] = obj

    def clear(self):
        for obj in self.__all_objects:
            blu.remove_obj(obj)
        self.__all_objects.clear()
