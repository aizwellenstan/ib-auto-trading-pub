rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.movingAverage import SmaArr
from modules.data import GetNpData
import numpy as np
from numba import range, njit
from modules.aiztradingview import GetClose, GetTradable, GetGainable
import pickle
from modules.csvDump import DumpCsv, LoadCsv

symbolList = ["KO","PEP"]


# @njit
def Backtest(qqqArr, npArr):
    npArr = npArr[-1058:]
    val = 0.01
    maxBalance = 1
    maxVal = 0
    while val < 1:
        balance = 1
        for i in range(1, len(npArr)):
            if (
                qqqArr[i][0] > qqqArr[i-1][3] and
                npArr[i][0] < npArr[i-1][3]
            ):
                op = npArr[i][0]
                if op < 0.01: return 0
                tp = (npArr[i-1][3] - npArr[i][0]) * val + npArr[i][0]
                if tp - op < 0.01: continue
                if tp > npArr[i][1]:
                    tp = npArr[i][3]
                gain = tp / op
                balance *= gain
        if balance > maxBalance:
            maxBalance = balance
            maxVal = val
            print(maxBalance,maxVal)
        val += 0.01
    if maxBalance <= 1: return 0
    print('MaxBalance',maxBalance)
    return maxBalance/len(npArr)

qqqArr = GetNpData("KO")
qqqArr = qqqArr[-1058:]
npArr = GetNpData("PEP")
balance = Backtest(qqqArr, npArr)
print(balance)
