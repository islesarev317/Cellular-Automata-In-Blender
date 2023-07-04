from classes import LocatedTensor as lt

a = lt.LocatedTensor.zeros(corner=(1, 1, 1), dim=(5, 4, 3))
a[1:4,0:3] = 1
a.hollow()
print(a)

b = lt.LocatedTensor.zeros(corner=(3, 4, 2), dim=(3, 3, 3))
b[:] = 3
print(b)

c = lt.LocatedTensor.union(a, b)
print(c)
