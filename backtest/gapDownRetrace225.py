rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.csvDump import LoadDict
from modules.aiztradingview import GetLargeCapJP
from modules.data import GetNpData
import pickle

import numpy as np

rironkabuakaPath = f'{rootPath}/data/Rironkabuka.csv'
rironkabakaDict = LoadDict(rironkabuakaPath, 'Rironkabuka')

dataPath = "./pickle/dataArrJP.p"
dataArr = {}
closeDictJP = GetLargeCapJP()
currency = 'JPY'

update = False
if update:
    for symbol, close in closeDictJP.items():
        if symbol not in rironkabakaDict: continue
        rironkabuka = rironkabakaDict[symbol]
        if close > rironkabuka: continue
        npArr = GetNpData(symbol, 'JPY')
        dataArr[symbol] = npArr
        print(symbol, len(npArr))
    pickle.dump(dataArr, open(dataPath, "wb"))
    print("pickle dump finished")
else:
    output = open(dataPath, "rb")
    # gc.disable()
    dataArr = pickle.load(output)
    output.close()
    # gc.enable()
    print("load data finished")

closeDict = {}
for symbol, close in closeDictJP.items():
    if symbol not in rironkabakaDict: continue
    rironkabuka = rironkabakaDict[symbol]
    if close > rironkabuka: continue
    closeDict[symbol] = close

# @njit
def Backtest(npArr):
    npArr = npArr[-1058:]
    val = 0.01
    maxBalance = 1
    maxVal = 0
    while val < 1:
        balance = 1
        minRetrace = 1
        retraceList = np.empty(0)
        for i in range(1, len(npArr)):
            if npArr[i][0] < npArr[i-1][3]:
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

def main():
    gainPerDayDict = {}
    for symbol, close in closeDict.items():
        # symbol = '9336'
        # symbol = '5830'
        # symbol = '5129'
        # symbol = '3436'
        symbol = '6503'
        # if symbol in ignoreList: continue
        if symbol not in dataArr: continue
        # if symbol in lowVolList: continue
        # npArr = GetNpData(symbol, 'JPY')
        npArr = dataArr[symbol]
        if len(npArr) < 1: continue
        balance = Backtest(npArr)
        # if not FrequencyCheck1m(symbol):
        # if not FrequencyCheck1mShift(symbol):
        #     lowVolList.append(symbol)
        #     continue
        gainPerDayDict[symbol] = balance
        print(symbol, balance)
        break
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

if __name__ == '__main__':
    main()