import numpy as np
from numba import njit

# @njit
def tradeList(op,sl,tp,condition):
    return np.float64([op,sl,tp,condition])

from numba import jit
from numba.types import types

# @jit(nopython=True)
def main():
    # empty_array = np.empty((4, 0), types.float64)
    # longTrades = empty_array
    # op = 0
    # sl = 1
    # tp = 3
    # condition = 4
    # longTrades.append(np.float64([op,sl,tp,condition]))
    # for trade in longTrades:
    #     print(trade)

    volumeList = [1,2,3,4,5,6,7,8,9,10]

    i = 9
    print(volumeList[9-3:9-1])

main()


# import numpy as np
# from numba import njit
# from numba.typed import Dict
# from numba.types import types

# # @njit
# def tradeList(a,b):
#     return a[b]

# x = Dict.empty(key_type=types.int64,value_type=types.float64)
# x[np.int64(0)]=np.float64(100)
# x[np.int64(2)]=np.int64(200)

# from numba import jit

# @jit(nopython=True)
# def main():
#     longTrades = np.empty(0)
#     op = 0
#     sl = 1
#     tp = 3
#     condition = 4
#     longTrades = np.append(longTrades,[x])
#     for trade in longTrades:
#         print(trade)

# main()