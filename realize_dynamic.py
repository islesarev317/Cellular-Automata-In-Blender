import utils as blu


class InstanceDynamic:

    cell_name = "Cell"
    scale_factor = 0.99

    def __init__(self, grain, collection, default_image):
        self.__tensor = None
        self.grain = grain
        self.collection = collection
        self.default_image = default_image
        self.all_objects = {}

    def __update_obj(self, obj, value):
        obj.scale.xyz = 0 if value == 0 else self.grain * self.scale_factor * blu.normalize_factor(self.default_image)

    def update(self, curr_tensor):

        prev_tensor = self.__tensor
        self.__tensor = curr_tensor

        prev_points = set(prev_tensor.point_to_global(point) for point in prev_tensor.not_null_points) if prev_tensor else set()
        curr_points = set(curr_tensor.point_to_global(point) for point in curr_tensor.not_null_points)

        # create
        for point in (curr_points - prev_points):
            if point not in self.all_objects:
                location = tuple(x * self.grain for x in point)
                obj = blu.copy_obj(self.default_image, self.cell_name, self.collection, location, scale=0)
                self.all_objects[point] = obj

        # update
        for point in curr_points:
            obj = self.all_objects[point]
            value = curr_tensor[curr_tensor.point_to_local(point)]
            self.__update_obj(obj, value)

        # delete
        for point in (prev_points - curr_points):
            obj = self.all_objects[point]
            value = 0
            self.__update_obj(obj, value)

