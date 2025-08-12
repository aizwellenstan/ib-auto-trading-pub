rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.movingAverage import SmaArr
from modules.data import GetNpData
import numpy as np
from numba import range, njit
from modules.aiztradingview import GetClose
import pickle
from modules.csvDump import DumpCsv, LoadCsv
import yfinance as yf
import pandas as pd

def GetData(symbol, period='1100d'):
    stockInfo = yf.Ticker(symbol)
    hist = stockInfo.history(period=period)
    df = hist.dropna()
    df['Date'] = df.index
    weekday=pd.to_datetime(df['Date'], format='%Y-%m-%d')
    df=df.assign(Weekday=weekday.dt.dayofweek)
    df = df[['Open','High','Low','Close','Weekday']]
    return df.to_numpy()

# dataPath = "./pickle/dataArr.p"
# dataArr = {}
# closeDict = GetClose()

# update = False
# if update:
#     for symbol, close in closeDict.items():
#         npArr = GetNpData(symbol)
#         if len(npArr) < 1: continue
#         dataArr[symbol] = npArr
#         print(symbol)

#     pickle.dump(dataArr, open(dataPath, "wb"))
#     print("pickle dump finished")
# else:
#     # import gc
#     output = open(dataPath, "rb")
#     # gc.disable()
#     dataArr = pickle.load(output)
#     output.close()
#     # gc.enable()



# @njit
def Backtest(npArr):
    npArr = npArr[-1058:]
    
    maxBalance = 1
    maxVal = 0
    maxAdjVal = 0
    adjVal = 0.01
    while adjVal < 1:
        val = 0.01
        while val < 1:
            balance = 1
            minRetrace = 1
            retraceList = np.empty(0)
            for i in range(1, len(npArr)):
                if npArr[i][0] < npArr[i-1][3]:
                    if (
                        (npArr[i-1][1] - npArr[i-1][3]) /
                        (npArr[i-1][1] - npArr[i-1][2]) > adjVal and
                        npArr[i-1][3] != 4 and
                        npArr[i-1][3] < npArr[i-1][0]
                    ): continue
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
                maxAdjVal = adjVal
                print(maxBalance,maxVal,maxAdjVal)
            val += 0.01
        adjVal += 0.01
    if maxBalance <= 1: return 0
    print('MaxBalance',maxBalance)
    return maxBalance/len(npArr)

gainPerDayDict = {}
symbol = 'QQQ'

npArr = GetData(symbol)
balance = Backtest(npArr)
gainPerDayDict[symbol] = balance
print(symbol, balance)
print(len(gainPerDayDict))
gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
# print(gainPerDayDict)

newGainPerDayDict = {}
count = 0
for symbol, gainPerDay in gainPerDayDict.items():
    if gainPerDay == 0: continue
    newGainPerDayDict[symbol] = gainPerDay
    count += 1
    if count > 100: break
print(newGainPerDayDict)

import sys
sys.exit(0)

lowVolPath = f"{rootPath}/data/lowVol2.csv"
DumpCsv(lowVolPath, lowVolList)
DumpCsv(ignorePath, ignoreList)

