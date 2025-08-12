rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose
from modules.csvDump import DumpCsv, LoadCsv, DumpDict
import pickle

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

closeDict = GetClose()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDict.p"

update = False
if update:
    for symbol, close in closeJPDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpData(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")

    for symbol, close in closeDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpData(symbol)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr
    
    pickle.dump(dataDict, open(picklePath, "wb"))
    print("pickle dump finished")
else:
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(picklePath, "rb")
    dataDict = pickle.load(output)
    output.close()

# # @njit
def Backtest(npArr,closeArr,sma25):
    bias = 0.0482831585
    bias25 = (closeArr-sma25)/closeArr
    npArr = npArr[-756:]
    bias25 = bias25[-756:]
    noVolCount = 0
    balance = 1
    for i in range(26, len(npArr)):
        if (
            npArr[i][0] == npArr[i][3]
        ):
            noVolCount += 1
            if noVolCount > 2: return 0
        if bias25[i-1] < -bias:
            # balance *= npArr[i][0] / npArr[i-1][3]
            balance *= npArr[i][3] / npArr[i][0]
    return balance
            


noTradeList = []
gainDict = {}

# for symbol, close in closeJPDict.items():
#     if symbol in ignoreList: continue
#     if symbol in noTradeList: continue
#     if symbol not in dataDictJP: continue
#     npArr = dataDictJP[symbol]
#     if len(npArr) < 1:
#         ignoreList.append(symbol)
#         continue
#     closeArr = npArr[:,3]
#     sma25 = SmaArr(closeArr, 25)
#     balance = Backtest(npArr,closeArr,sma25)
#     if balance <= 1: 
#         noTradeList.append(symbol)
#         continue
#     gainDict[symbol] = balance
#     print(symbol, balance)

for symbol, close in closeDict.items():
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    if symbol not in dataDict: continue
    if symbol != "TSLA": continue
    npArr = dataDict[symbol]
    if len(npArr) < 1:
        ignoreList.append(symbol)
        continue
    closeArr = npArr[:,3]
    sma25 = SmaArr(closeArr, 25)
    balance = Backtest(npArr,closeArr,sma25)
    if balance <= 1: 
        noTradeList.append(symbol)
        # continue
    gainDict[symbol] = balance
    print(symbol, balance)
    
gainDict = dict(sorted(gainDict.items(), key=lambda item: item[1], reverse=True))
print(gainDict)

newGainDict = {}
count = 0
infCount = 0
for symbol, gain in gainDict.items():
    newGainDict[symbol] = gain
    if gain != float('inf'):
        infCount += 1
        count += 1
    if count > 50: break
print(newGainDict)
print(infCount)

# DumpCsv(ignorePath, ignoreList)
# DumpCsv(noTradePath, noTradeList)
# gainPath = f"{rootPath}/data/gainDictDayTrade.csv"
# DumpDict(gainDict,"gain",gainPath)

# gainPath = f"{rootPath}/data/gainDayTrade.csv"
# DumpCsv(gainPath,list(gainDict.keys()))


# symbol = "9101"
# npArr = GetNpData(symbol, currency="JPY")
# # symbol = "TSLA"
# # npArr = GetNpData(symbol)
# closeArr = npArr[:,3]
# sma25 = SmaArr(closeArr, 25)
# Backtest(npArr,closeArr,sma25)