# import numpy as np

# x = np.array([[[1,2],[3,4],[5,6]],[[1,2],[3,4],[5,6]]])
# y = np.array([1,2,3])
# y = np.reshape(y,(-1,1,1))
# print(x)
# print(y)

# c = x*y
# print(c)

import numpy as np

a = np.random.randint(0,9,(2,3,2))
b = np.random.randint(0,9,(3))
print("------------------------------------a")
print(a)
print("------------------------------------b")
print(b)

given_axis = 1

dim_array = np.ones((1,a.ndim),int).ravel()
dim_array[given_axis] = -1

b_reshaped = b.reshape(dim_array)
mult_out = a*b_reshaped

print("------------------------------------res")

print(mult_out)