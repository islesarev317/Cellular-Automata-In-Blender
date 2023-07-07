from tensor import LocatedTensor
from utils import print


class VirtualFunction:

    def __init__(self, ops, *ff):
        self.ops = ops
        self.ff = ff

    def compute(self):
        tt = [f.compute() for f in self.ff]
        result = self.ops(*tt)
        return result

    def __add__(self, other):
        return VirtualFunction(LocatedTensor.__add__, self, other)

    def __sub__(self, other):
        return VirtualFunction(LocatedTensor.__sub__, self, other)

    def hollow(self):
        return VirtualFunction(LocatedTensor.hollow, self)



