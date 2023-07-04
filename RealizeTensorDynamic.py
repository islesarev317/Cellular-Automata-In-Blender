class Instance:

    def __init__(self, grain, createObj, updateObj):

        self.active_objects = {}
        self.all_objects = {}
        self.grain = grain

        # functions
        self.createObj = createObj
        self.updateObj = updateObj

        self.max_objects = 1000

    def update(self, tensor):

        active = set(self.active_objects.keys())
        all = set(self.all_objects.keys())
        t = set(tuple(tensor.pointToGlobal(p)) for p in np.ndindex(tensor.dim) if tensor[p] != 0)

        decrease = active - t
        increase = t - active
        create = increase - all
        reserve = all - active - t

        # decrease
        for p in decrease:
            obj = self.active_objects.pop(p)
            val = 0
            self.updateObj(obj, val, self.grain)

        # create
        for p in create:
            val = tensor[tensor.pointToLocal(p)]
            location = tuple(np.array(p) * self.grain)

            # optimization
            if len(self.all_objects) < self.max_objects or len(reserve) == 0:
                self.all_objects[p] = self.createObj(location, val, self.grain)
            else:
                r = reserve.pop()
                obj = self.all_objects.pop(r)
                obj.keyframe_insert("location", frame=bpy.context.scene.frame_current - 5)
                obj.location = location
                obj.keyframe_insert("location", frame=bpy.context.scene.frame_current - 4)
                self.all_objects[p] = obj

        # increase
        for p in increase:
            obj = self.all_objects[p]
            val = tensor[tensor.pointToLocal(p)]
            self.active_objects[p] = obj
            self.updateObj(obj, val, self.grain)