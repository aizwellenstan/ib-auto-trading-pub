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

qqqArr = dataDict["QQQ"]

# @njit
def Backtest(qqqArr, npArr):
    period = 756
    qqqArr = qqqArr[-period:]
    npArr = npArr[-period:]
    if len(npArr) < period: return 0
    gainList = np.empty(0)
    count = 0
    for i in range(1, period):
        if qqqArr[i][3] > qqqArr[i][0]:
            gain = npArr[i][3] / npArr[i][0]
            if gain > qqqArr[i][3] / qqqArr[i][0]:
                count += 1
            else:
                count -= 1
    return count

gainDict = {}
for symbol, close in closeDict.items():
    if symbol not in dataDict: continue
    npArr = dataDict[symbol]
    gain = Backtest(qqqArr, npArr)
    gainDict[symbol] = gain
gainDict = dict(sorted(gainDict.items(), key=lambda item: item[1], reverse=True))
newGainDict = {}
count = 0
for symbol, gain in gainDict.items():
    newGainDict[symbol] = gain
    count += 1
    if count > 50: break
print(newGainDict)