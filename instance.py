import utils as blu


class Instance:

    cell_name = "Cell"
    scale_factor = 0.9
    default_limit = 3000

    def __init__(self, virtual_function, grain, collection, image, reserve=True, bake=False, bake_interval=1, limit=default_limit):
        self.__tensor = None
        self.virtual_function = virtual_function
        self.grain = grain
        self.collection = collection
        self.image = image
        self.all_objects = {}
        self.reserve = reserve
        self.bake = bake
        self.bake_interval = bake_interval
        self.limit = limit
        self.__baked_frames = []
        self.__reuse_objects()

    def __reuse_objects(self):
        i = 0
        for obj in self.collection.objects:
            obj.scale.xyz = 0
            self.all_objects[i] = obj
            i += 1

    @staticmethod
    def bake(input_func):
        def output_func(self, obj, value):
            if self.bake:
                current_frame = blu.current_frame()
                obj.keyframe_insert("scale", frame=current_frame-self.bake_interval)
                obj.keyframe_insert("location", frame=current_frame-self.bake_interval)
                input_func(self, obj, value)
                obj.keyframe_insert("scale", frame=current_frame)
                obj.keyframe_insert("location", frame=current_frame)
            else:
                input_func(self, obj, value)
        return output_func

    @bake
    def __update_obj(self, obj, value):
        obj.scale.xyz = 0 if value == 0 else self.grain * self.scale_factor * blu.normalize_factor(self.image)

    def update(self):

        if self.bake:
            current_frame = blu.current_frame()
            if current_frame in self.__baked_frames:
                return
            self.__baked_frames.append(current_frame)

        curr_tensor = self.virtual_function.tensor()
        prev_tensor = self.__tensor
        self.__tensor = curr_tensor

        prev_points = set(prev_tensor.not_null_points_global) if prev_tensor else set()
        curr_points = set(curr_tensor.not_null_points_global)
        reserve_points = set(self.all_objects.keys()) - curr_points

        # create
        for point in (curr_points - prev_points):
            if point not in self.all_objects:
                location = tuple(x * self.grain for x in point)
                # optimization
                if len(reserve_points) > 0 and self.reserve:
                    rp = reserve_points.pop()
                    obj = self.all_objects.pop(rp)
                    blu.move_obj(obj, location, scale=0)
                elif len(self.all_objects) < self.limit:
                    obj = blu.copy_obj(self.image, self.cell_name, self.collection, location, scale=0)
                else:
                    obj = None
                self.all_objects[point] = obj

        # update
        for point in curr_points:
            obj = self.all_objects[point]
            value = curr_tensor[curr_tensor.point_to_local(point)]
            self.__update_obj(obj, value)

        # delete
        for point in ((prev_points - curr_points) & set(self.all_objects.keys())):
            obj = self.all_objects[point]
            value = 0
            self.__update_obj(obj, value)

