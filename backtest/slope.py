rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.movingAverage import SmaArr
from modules.data import GetNpData
import numpy as np
from numba import range, njit
from modules.aiztradingview import GetClose
import pickle

symbol = 'TSLA'
npArr = GetNpData(symbol)

# @njit
def Backtest(npArr):
    pPerDayList = np.empty(0)
    for i in range(1, len(npArr)):
        performance = npArr[i-1][3] / npArr[i-1][0]
        pPerDay = performance/i
        pPerDayList = np.append(pPerDayList, pPerDay)

    pPerDayList.sort()
    print(pPerDayList)

    maxBalance = 1
    maxPPerDayLimit = 0
    for pPerDayLimit in pPerDayList:
        balance = 1
        for i in range(1, len(npArr)):
            performance = npArr[i-1][3] / npArr[i-1][0]
            pPerDay = performance/i
            if pPerDay > pPerDayLimit:
                op = npArr[i][0]
                close = npArr[i][3]
                gain = close/op
                balance *= gain
                if balance > maxBalance:
                    maxBalance = balance
                    maxPPerDayLimit = pPerDayLimit
                    print(maxBalance, maxPPerDayLimit)

Backtest(npArr)