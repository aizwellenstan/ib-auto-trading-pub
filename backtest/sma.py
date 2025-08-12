rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
from numba import range, njit

symbol = 'QQQ'
npArr = GetNpData(symbol)

# @njit
def Backtest(npArr):
    length = len(npArr)
    balance = 1
    for i in range(length-1058, length):
        if (

        ):
            gain = npArr[i][3] / npArr[i][0]
            balance *= gain