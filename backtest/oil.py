rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr, GetGainable
from modules.data import GetNpData
import pickle
from numba import range, njit

gainable = GetGainable()
uso = GetNpData('USO')
uso = uso[-1058:]

def GetDataDict(symbolList, update=False):
    dataDict = {}
    picklePath = "./pickle/pro/compressed/oil.p"
    if update:
        for symbol in symbolList:
            npArr = GetNpData(symbol)
            if len(npArr) < 1: continue
            dataDict[symbol] = npArr
            print(symbol)
        pickle.dump(dataDict, open(picklePath, "wb"))
    else:
        output = open(picklePath, "rb")
        dataDict = pickle.load(output)
    return dataDict

# @njit
def Backtest(npArr):
    npArr = npArr[-1058:]
    val = 0.01
    maxBalance = 1
    maxVal = 0
    while val < 1:
        balance = 1
        for i in range(1, len(npArr)):
            if (npArr[i][0] < npArr[i-1][3] and
                uso[i][0] > uso[i-1][3]
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

symbolList = list(gainable.keys())
dataDict = GetDataDict(symbolList)

gainPerDayDict = {}
for symbol, clsoe in gainable.items():
    symbol = 'COP'
    npArr = dataDict[symbol]
    gainPerDay = Backtest(npArr)
    gainPerDayDict[symbol] = gainPerDay
    break

gainPerDayDict = dict(sorted(gainPerDayDict.items(), key=lambda item: item[1], reverse=True))
print(gainPerDayDict)