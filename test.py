from scipy.optimize import linprog
import numpy as np
# find max of 2x0 + x1
# 3x0 + x1 <= 7
# 1x0 + 2x1 <= 9
# x0 >= 0
# x1 >= 0


c = [-2, -1]
A = [[3, 1], [1, 2]]
b = np.array([7, 9])
x0_bounds = (0, None)
x1_bounds = (0, None)

res = linprog(c, A_ub=A, b_ub=b, bounds=[x0_bounds, x1_bounds])

print(res)



