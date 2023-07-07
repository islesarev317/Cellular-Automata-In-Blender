import utils as blu


class InstanceBaked:

    cell_name = "Cell"
    scale_factor = 0.99

    def __init__(self, grain, collection, default_image):
        self.__tensor = None
        self.grain = grain
        self.collection = collection
        self.default_image = default_image
        self.all_objects = {}
        self.baked_frames = []

    def __update_obj(self, obj, value, frame):
        obj.scale.xyz = 0 if value == 0 else self.grain * self.scale_factor * blu.normalize_factor(self.default_image)

    def __bake_keyframe(self):
        current_frame = blu.current_frame()
        for obj in self.all_objects.values():
            obj.keyframe_insert("scale", frame=current_frame)
            obj.keyframe_insert("location", frame=current_frame)

    def update(self, curr_tensor):

        current_frame = blu.current_frame()
        if current_frame not in self.baked_frames:
            self.baked_frames.append(current_frame)

            prev_tensor = self.__tensor
            self.__tensor = curr_tensor

            prev_points = set(prev_tensor.point_to_global(point) for point in prev_tensor.not_null_points) if prev_tensor else set()
            curr_points = set(curr_tensor.point_to_global(point) for point in curr_tensor.not_null_points)
            reserve_points = set(self.all_objects.keys()) - prev_points - curr_points

            # create
            for point in (curr_points - prev_points):
                if point not in self.all_objects:
                    location = tuple(x * self.grain for x in point)
                    # optimization
                    if len(reserve_points) > 0:
                        rp = reserve_points.pop()
                        obj = self.all_objects.pop(rp)
                        blu.move_obj(obj, location, scale=0)
                    else:
                        obj = blu.copy_obj(self.default_image, self.cell_name, self.collection, location, scale=0)
                    self.all_objects[point] = obj

            # update
            for point in curr_points:
                obj = self.all_objects[point]
                value = curr_tensor[curr_tensor.point_to_local(point)]
                self.__update_obj(obj, value, current_frame)

            # delete
            for point in (prev_points - curr_points):
                obj = self.all_objects[point]
                value = 0
                self.__update_obj(obj, value, current_frame)

            self.__bake_keyframe()

