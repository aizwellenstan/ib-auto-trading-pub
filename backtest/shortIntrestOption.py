rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetDataWithVolume, GetDataWithDate
from modules.shortIntrest import GetShortIntrest
import pickle

from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.aiztradingview import GetClose
from modules.rironkabuka import GetRironkabuka
import csv

import math
import numpy as np
from modules.aiztradingview import GetAttr, GetClose

closeDictUS = GetClose()
symbolList = list(closeDictUS.keys())

attrDict = GetAttr("float_shares_outstanding")
closeDict = GetClose()

def GetData(symbol):
    try:
        symbol
        npArr = GetDataWithVolume(symbol)
        return [symbol, npArr]
    except: return []

def GetShortIntrestData(symbol):
    try:
        npArr = GetShortIntrest(symbol)
        return [symbol, npArr]
    except: return []

dataDictJP = {}
dataDictUS = {}
shortIntrestDictUS = {}
picklePathPriceUS = f"{rootPath}/backtest/pickle/pro/compressed/dataDictVolumeUS.p"
picklePathShortIntrestUS = f"{rootPath}/backtest/pickle/pro/compressed/dataDictShortIntrest.p"
def UpdateData():
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(GetShortIntrestData, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            npArr = result[1]
            if len(npArr) < 1: continue
            shortIntrestDictUS[symbol] = npArr
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(GetData, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            npArr = result[1]
            if len(npArr) < 1: continue
            dataDictUS[symbol] = npArr

update = False
if update:
    UpdateData()
    pickle.dump(shortIntrestDictUS, open(picklePathShortIntrestUS, "wb"))
    print("pickle dump finished")
    print(dataDictUS)
    pickle.dump(dataDictUS, open(picklePathPriceUS, "wb"))
    print("pickle dump finished")
else:
    output = open(picklePathShortIntrestUS, "rb")
    shortIntrestDictUS = pickle.load(output)
    output.close()

    # output = open(picklePathPriceUS, "rb")
    # dataDictUS = pickle.load(output)
    # output.close()

def CheckShortSqueeze(symbol):
    shortIntrest = shortIntrestDictUS[symbol]
    shortSqueeze = []
    floatShares = attrDict[symbol]
    for i in range(0, len(shortIntrest)):
        date = shortIntrest[i][0]
        if shortIntrest[i][1]/floatShares <= 0.007282150442361121:
            continue
        # if date == "2022-11-15":
        #     print(shortIntrest[i])
        #     print(shortIntrest[i][1]/floatShares)
        shortSqueeze.append(date)
    # print(shortSqueeze)
    return [symbol, shortSqueeze]

def GetHighestSupport(symbol, shortSqueeze):
    # print("GetHighestSupport", symbol)
    npArr = GetDataWithDate(symbol)
    supportLv = np.empty(0)
    close = closeDict[symbol]
    print(shortSqueeze)
    for i in range(0, len(npArr)):
        if npArr[i][4] in shortSqueeze:
            low = npArr[i][2]
            # if low < close:
            supportLv = np.append(supportLv, low)
    if len(supportLv) > 0:
        supportLv = np.max(supportLv)
    else:
        supportLv = 0
    return supportLv

def GetSupportLv(symbol):
    res = CheckShortSqueeze(symbol)
    shortSqueeze = res[1]
    # print(shortSqueeze)

    support = GetHighestSupport(symbol, shortSqueeze)
    close = closeDict[symbol]
    if support > close: support = 0
    # print(support)
    return [symbol, support]

supportLvDict = {}
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(GetSupportLv, symbol) for symbol in list(shortIntrestDictUS.keys())]
    for future in as_completed(futures):
        result = future.result()
        symbol = result[0]
        res = result[1]
        supportLvDict[symbol] = res

supportLvDict = dict(sorted(supportLvDict.items(), key=lambda item: item[1], reverse=True))
print(supportLvDict)


