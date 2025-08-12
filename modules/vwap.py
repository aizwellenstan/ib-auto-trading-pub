# from numba import jit
import numpy as np

# @jit
def Vwap(v,h,l):
    tmp1 = np.zeros_like(v)
    tmp2 = np.zeros_like(v)
    for i in range(0,len(v)):
        tmp1[i] = tmp1[i-1] + v[i] * ( h[i] + l[i] ) / 2.
        tmp2[i] = tmp2[i-1] + v[i]
    return tmp1 / tmp2

# @jit
def Vwma(v,c):
    tmp1 = np.zeros_like(v)
    tmp2 = np.zeros_like(v)
    for i in range(0,len(v)):
        tmp1[i] = tmp1[i-1] + v[i] * c[i]
        tmp2[i] = tmp2[i-1] + v[i]
    return tmp1 / tmp2