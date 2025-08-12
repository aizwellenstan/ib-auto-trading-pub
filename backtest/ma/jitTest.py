from numba import njit
import numpy as np

# @njit(nopython=False)
def func(n):
    c = np.empty(0)
    print(c)
    for i in range(1,n):
        c = np.append(c,i)
    print(len(c))
    for i in c:
        print(i)
    return c

ans = func(5)
print(ans)