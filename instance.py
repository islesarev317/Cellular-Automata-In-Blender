import utils as blu
import random


class Instance:

    cell_name = "Cell"
    scale_factor = 0.9
    default_limit = 3000

    def __init__(self, virtual_function, grain, collection, image, reserve=True, bake=False,
                 frame_step=1, limit=default_limit):
        self.__tensor = None
        self.__start_frame = None
        self.__current_frame = None
        self.__end_frame = None
        self.virtual_function = virtual_function
        self.grain = grain
        self.collection = collection
        self.image = image
        self.all_objects = {}
        self.reserve = reserve
        self.bake = bake
        self.frame_step = frame_step
        self.limit = limit
        self.__baked_frames = []
        self.__reuse_objects()

    def __reuse_objects(self):
        i = 0
        for obj in self.collection.objects:
            if obj.name.startswith(self.cell_name):
                obj.animation_data_clear()
                obj.scale.xyz = 0
                self.all_objects[i] = obj
                i += 1

    def __get_cell_size(self, value):
        return 0 if value == 0 else self.grain * self.scale_factor * blu.normalize_factor(self.image)

    def __bake_obj(self, obj, shift=0):
        obj.keyframe_insert("scale", frame=self.__current_frame + shift)
        obj.keyframe_insert("location", frame=self.__current_frame + shift)

    def update(self):

        self.__start_frame = blu.start_frame()
        self.__current_frame = blu.current_frame()
        self.__end_frame = blu.end_frame()

        if not(self.__start_frame <= self.__current_frame <= self.__end_frame):
            return

        if self.bake:
            if self.__start_frame <= self.__current_frame <= self.__end_frame:
                if self.__current_frame in self.__baked_frames:
                    return
                self.__baked_frames.append(self.__current_frame)

        curr_tensor = self.virtual_function.tensor()
        prev_tensor = self.__tensor
        self.__tensor = curr_tensor

        prev_points = set(prev_tensor.not_null_points_global) if prev_tensor else set()
        curr_points = self.apply_limit(curr_tensor)
        existed_points = set(self.all_objects.keys())
        reserve_points = (existed_points - curr_points) - prev_points

        # create
        for point in (curr_points - existed_points):
            location = tuple(x * self.grain for x in point)
            if len(reserve_points) > 0 and self.reserve:  # optimization
                reserve = reserve_points.pop()  # extract reserve point
                obj = self.all_objects.pop(reserve)  # extract reserve object
            else:
                obj = blu.copy_obj(self.image, self.cell_name, self.collection)  # create new object
            self.all_objects[point] = obj
            blu.move_obj(obj, location)  # --> move
            blu.scale_obj(obj, self.__get_cell_size(0))  # --> scale
            if self.bake:
                self.__bake_obj(obj)
                if self.frame_step == 1:
                    self.__bake_obj(obj, -1)
                if self.frame_step > 1:
                    self.__bake_obj(obj, 1 - self.frame_step)

        # update
        for point in curr_points:
            obj = self.all_objects[point]
            value = curr_tensor.get_global(point)
            if self.bake and self.frame_step > 1:
                self.__bake_obj(obj, 1 - self.frame_step)
            blu.scale_obj(obj, self.__get_cell_size(value))  # --> scale
            if self.bake:
                self.__bake_obj(obj)

        # delete
        for point in (prev_points - curr_points):
            obj = self.all_objects[point]
            if self.bake and self.frame_step > 1:
                self.__bake_obj(obj, 1 - self.frame_step)
            blu.scale_obj(obj, self.__get_cell_size(0))  # --> scale
            if self.bake:
                self.__bake_obj(obj)

    def apply_limit(self, curr_tensor):
        """ crop set and show label """
        curr_points = set(curr_tensor.not_null_points_global)
        curr_cnt = len(curr_points)
        msg = str(curr_cnt) + " / " + str(self.limit)
        if curr_cnt > self.limit:
            curr_points = set(random.sample(curr_points, self.limit))  # crop set of points!
            msg += " (LIMIT EXCEEDED!)"
        label_loc = [(curr_tensor.corner[i] + curr_tensor.dim[i] / 2) * self.grain for i in range(3)]  # center
        label_loc[2] += curr_tensor.dim[2] * self.grain  # move on the top
        blu.show_label(msg, tuple(label_loc))
        print(msg)
        return curr_points
