import LocatedTensor as ten

a = ten.LocatedTensor.zeros(corner=(1, 1, 1), dim=(5, 4, 3))
a[1:4,0:3] = 1
a.hollow()
print(a)

b = ten.LocatedTensor.zeros(corner=(3, 4, 2), dim=(3, 3, 3))
b[:] = 3
print(b)

c = ten.LocatedTensor.union(a, b)
print(c)
