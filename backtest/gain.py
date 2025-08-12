rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.data import GetNpData
from modules.aiztradingview import GetAttr, GetPerformance, GetClose
from numba import njit
from numba import types
from numba.typed import Dict
from modules.movingAverage import SmaArr
from modules.data import GetDividend
import pandas as pd
import os

def DumpResCsv(resPath, resList):
    df = pd.DataFrame(resList, columns = ['Symbol'])
    df.to_csv(resPath)

# @njit
def GetDailyGain(gainList):
    if len(gainList) < 1: return 1
    vol = 1 / len(gainList)
    dailyGain = 0
    for gain in gainList:
        dailyGain += vol * gain
    return dailyGain

# @njit
def Backtest(dataDict, period):
    totalGain = 1
    for i in range(1, backtestLength):
        # gainList = np.empty(0)
        maxMomentum = 2
        gain = 1
        for symbol, npArr in dataDict.items():
            momentum = npArr[i-1][3]/npArr[i-1][0]
            if (
                momentum < maxMomentum and
                npArr[i][0] < npArr[i-1][2]
            ):
                maxMomentum = momentum
                gain = npArr[i][4]
                # gainList = np.append(gainList, gain)
        totalGain *= gain
        # dailyGain = GetDailyGain(gainList)
        # totalGain *= dailyGain
    return totalGain

emptyDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])
# # @njit
# def main(dataDict):
#     maxTotalGain = 0
#     minPeriod = 0
#     period = 1
#     while period < 500:
#         totalGain = Backtest(dataDict, period)
#         if totalGain > maxTotalGain:
#             maxTotalGain = totalGain
#             minPeriod = period
        
#         print(maxTotalGain,minPeriod)
#         period += 1
# main(dataDict)

# # @njit
def main():
    resPath = f'{rootPath}/data/historicalTopGainner.csv'
    update = False
    topGainnerList = []
    if update:
        for i in range(1, backtestLength):
            maxGain = 1
            topGainner = ""
            for symbol, npArr in dataDict.items():
                if npArr[i][4] > maxGain:
                    maxGain = npArr[i][4]
                    topGainner = symbol
            if topGainner not in topGainnerList:
                topGainnerList.append(topGainner)
        DumpResCsv(resPath, topGainnerList)
    else:
        if os.path.exists(resPath):
            df = pd.read_csv(resPath)
            topGainnerList = list(df.Symbol.values)

    attrDict = GetAttr("market_cap_basic")

    attrList = []
    for symbol in topGainnerList:
        if symbol not in attrDict: continue
        attr = attrDict[symbol]
        if attr not in attrList:
            attrList.append(attr)
    attrList.sort()
    print(attrList)
    # for i in attrList:
    #     print(i)
main()