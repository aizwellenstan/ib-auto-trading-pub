rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolumeWeekday

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose, GetAttr, GetAttrJP
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict
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
    npArr = GetNpDataVolumeWeekday("^N225")
    dataDict["^N225"] = npArr
    for symbol, close in closeJPDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpDataVolumeWeekday(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")

    npArr = GetNpDataVolumeWeekday("QQQ")
    dataDict["QQQ"] = npArr
    npArr = GetNpDataVolumeWeekday("SPY")
    dataDict["SPY"] = npArr
    npArr = GetNpDataVolumeWeekday("DIA")
    dataDict["DIA"] = npArr
    npArr = GetNpDataVolumeWeekday("IWM")
    dataDict["IWM"] = npArr
    npArr = GetNpDataVolumeWeekday("BRK.A")
    dataDict["BRK.A"] = npArr
    npArr = GetNpDataVolumeWeekday("BRK.B")
    dataDict["BRK.B"] = npArr
    for symbol, close in closeDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpDataVolumeWeekday(symbol)
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

# @njit
def Backtest(npArr, type=0):
    period = 252
    npArr = npArr[-period:]
    if len(npArr) < period: return np.array([0.0,0.0,0.0])
    maxBalance = 1.0
    maxVal = 0
    maxWr = 0
    val = 0.01
    valStep = 0.01
    target = 2
    if type == 1:
        val = 1.0
        valStep = 1
        target *= 100
    while val < target:
        win = 0
        loss = 0
        tp_arr = npArr[:, 0] + val
        gains = np.where(npArr[:, 1] > tp_arr, tp_arr / npArr[:, 0], (npArr[:, 0] - val) / npArr[:, 0])
        win = np.sum(gains > 1)
        loss = np.sum(gains < 1)
        wr = win / (win + loss)
        if wr > 0.5:
            risk = wr*2 - 1
            balance = 1
            for i in range(1, len(npArr)):
                tp = tp_arr[i]
                vol = balance / npArr[i, 0] * risk
                balance -= vol * npArr[i, 0]
                if npArr[i, 1] > tp:
                    balance += vol * tp
                else:
                    balance += vol * (npArr[i, 0] - val)
            if balance > maxBalance:
                maxBalance = balance
                maxVal = val
                maxWr = wr
        val += valStep
    res = np.array([maxBalance,maxVal,maxWr])
    return res

gainDict = {}
valDict = {}
wrDict = {}
for symbol, close in closeJPDict.items():
    if symbol not in dataDictJP: continue
    npArr = dataDictJP[symbol]
    res = Backtest(npArr, 1)
    gainDict[symbol] = res[0]
    valDict[symbol] = res[1]
    wrDict[symbol] = res[2]
for symbol, close in closeDict.items():
    if symbol not in dataDict: continue
    npArr = dataDict[symbol]
    res = Backtest(npArr, 0)
    gainDict[symbol] = res[0]
    valDict[symbol] = res[1]
    wrDict[symbol] = res[2]
gainDict = dict(sorted(gainDict.items(), key=lambda item: item[1], reverse=True))
newGainDict = {}
count = 0
for symbol, gain in gainDict.items():
    newGainDict[symbol] = gain
    count += 1
    if count > 100: break
print(newGainDict)
newValDict = {}
for symbol, gain in newGainDict.items():
    newValDict[symbol] = valDict[symbol]
print(newValDict)
newWrDict = {}
for symbol, gain in newGainDict.items():
    newWrDict[symbol] = wrDict[symbol]
print(newWrDict)