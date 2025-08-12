rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolumeWeekday

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose, GetAttr, GetAttrJP
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict
import pickle
import modules.income as yfincome

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/netIncome/dataDictJP.p"

closeDict = GetClose()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/netIncome/dataDict.p"

update = False
if update:
    # npArr = GetNpDataVolumeWeekday("^N225")
    # dataDict["^N225"] = npArr
    for symbol, close in closeJPDict.items():
        if symbol in ignoreList: continue
        npArr = yfincome.GetIncome(symbol, "JPY")
        # npArr = GetNpDataVolumeWeekday(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")

    # npArr = GetNpDataVolumeWeekday("QQQ")
    # dataDict["QQQ"] = npArr
    # npArr = GetNpDataVolumeWeekday("SPY")
    # dataDict["SPY"] = npArr
    # npArr = GetNpDataVolumeWeekday("DIA")
    # dataDict["DIA"] = npArr
    # npArr = GetNpDataVolumeWeekday("IWM")
    # dataDict["IWM"] = npArr
    # npArr = GetNpDataVolumeWeekday("BRK.A")
    # dataDict["BRK.A"] = npArr
    # npArr = GetNpDataVolumeWeekday("BRK.B")
    # dataDict["BRK.B"] = npArr
    for symbol, close in closeDict.items():
        if symbol in ignoreList: continue
        # npArr = GetNpDataVolumeWeekday(symbol)
        npArr = yfincome.GetIncome(symbol)
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
def Backtest(npArr, sharesFloat, close):
    if len(npArr) < 4: return 0
    # if npArr[1][1] < 1: return 0
    # if npArr[3][1] < 1: return 0
    # if npArr[0][1] / npArr[1][1] <= 0.533373119466199:
    #     return 0
    # if npArr[2][1] / npArr[3][1] <= 0.054775054096825246:
    #     return 0
    netIncome = npArr[0][1]
    return netIncome / sharesFloat

floatDictJP = GetAttrJP("float_shares_outstanding")
floatDictUS = GetAttr("float_shares_outstanding")


cpDict = {}
for symbol, close in closeJPDict.items():
    if symbol not in dataDictJP: continue
    if symbol not in floatDictJP: continue
    sharesFloat = floatDictJP[symbol]
    npArr = dataDictJP[symbol]
    cp = Backtest(npArr, sharesFloat, close)
    cpDict[symbol] = cp
for symbol, close in closeDict.items():
    # if symbol != "NMR": continue
    if symbol not in dataDict: continue
    if symbol not in floatDictUS: continue
    sharesFloat = floatDictUS[symbol]
    npArr = dataDict[symbol]
    # print(npArr[0][1]/npArr[1][1])
    # print(npArr[0][1]/npArr[2][1])
    # print(npArr[0][1]/npArr[3][1])
    # print(npArr[0][1]/npArr[1][1])
    # print(npArr[1][1]/npArr[2][1])
    # print(npArr[2][1]/npArr[3][1])
    # print(npArr)
    # print(sharesFloat)
    # print(close)
    cp = Backtest(npArr, sharesFloat, close)
    cpDict[symbol] = cp
cpDict = dict(sorted(cpDict.items(), key=lambda item: item[1], reverse=True))
newCpDict = {}
count = 0
for symbol, gain in cpDict.items():
    newCpDict[symbol] = gain
    count += 1
    if count > 50: break
print(newCpDict)