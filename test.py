# import numpy as np

# x = np.array([[[1,2],[3,4],[5,6]],[[1,2],[3,4],[5,6]]])
# y = np.array([1,2,3])
# y = np.reshape(y,(-1,1,1))
# print(x)
# print(y)

# c = x*y
# print(c)

import numpy as np

a = np.random.randint(0,9,(2,2))
b = np.random.randint(0,9,(2,1))
print(a)
print("------------------------------------b")
print(b)

c = a * b
print("------------------------------------c")

print(c)
