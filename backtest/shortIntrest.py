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

attrDict = GetAttr("total_shares_outstanding_fundamental")
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

    output = open(picklePathPriceUS, "rb")
    dataDictUS = pickle.load(output)
    output.close()


def GetSetups(symbol, shortSqueeze):
    # npArr = dataDictUS[symbol]
    npArr = GetDataWithDate(symbol)
    setups = []
    triggered = []
    for i in range(0, len(npArr)):
        newSetups = []
        for setup in setups:
            op = setup[0]
            sl = setup[1]
            if (
                npArr[i][1] > op and
                npArr[i][2] < sl and
                npArr[i][3] < npArr[i][0]
            ): continue
            if npArr[i][1] > op:
                # triggered.append([setup[0], setup[1], 0])
                triggered.append([setup[0],setup[1],setup[2],0])
            else:
                newSetups.append(setup)
        setups = newSetups

        newTriggered = []
        for setup in triggered:
            # daysPassed = setup[2]
            daysPassed = setup[3]
            # if daysPassed < 1:
            
            # if daysPassed > 3:
            if (
                npArr[i-2][2] > setup[0] and
                npArr[i-1][2] < setup[0]
            ):
                continue
            daysPassed += 1
            if npArr[i-2][2] < setup[1]:
                # print(npArr[i][4], npArr[i-2][2], setup)
                continue
            # newTriggered.append([setup[0],setup[1],daysPassed])
            newTriggered.append([setup[0],setup[1],setup[2],daysPassed])
        triggered = newTriggered
        if npArr[i][4] in shortSqueeze:
            # setups.append([npArr[i][1], npArr[i][2]])
            setups.append([npArr[i][1], npArr[i][2], npArr[i][4]])
    if len(triggered) > 0:
        print(symbol, setups, triggered)

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
    shortSqueeze = GetSetups(symbol, shortSqueeze)
    return [symbol, shortSqueeze]

# CheckShortSqueeze("SNPS")
# sys.exit()
supportLvDict = {}
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(CheckShortSqueeze, symbol) for symbol in list(shortIntrestDictUS.keys())]
    for future in as_completed(futures):
        result = future.result()
        symbol = result[0]
        res = result[1]
        supportLvDict[symbol] = res

# supportLvDict = dict(sorted(supportLvDict.items(), key=lambda item: item[1], reverse=True))
# print(supportLvDict)


