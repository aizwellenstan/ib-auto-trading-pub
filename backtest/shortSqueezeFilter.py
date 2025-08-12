rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.csvDump import load_csv_to_dict
from modules.aiztradingview import GetClose, GetCloseJP
import numpy as np

from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
import numpy as np
from modules.aiztradingview import GetClose, GetCloseJP, GetAttr, GetAttrJP, GetBestGainUS
from modules.rironkabuka import GetRironkabuka
import csv

import math
import pickle
import csv

closeDictJP = GetCloseJP()
closeDictUS = GetClose()
symbolList = list(closeDictJP.keys()) + list(closeDictUS.keys())

def GetData(symbol):
    try:
        ticker = symbol
        if ticker in closeDictJP: 
            ticker += ".T"
        data = yf.Ticker(ticker).history(start="2021-03-19")
        npArr = data[["Open","High","Low","Close","Volume"]].to_numpy()
        return [symbol, npArr]
    except: return []

dataDictJP = {}
dataDictUS = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictVolumeJP.p"
picklePathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataDictVolumeUS.p"
def UpdateData():
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(GetData, symbol) for symbol in symbolList]
        for future in as_completed(futures):
            result = future.result()
            if len(result) < 1: continue
            symbol = result[0]
            npArr = result[1]
            if len(npArr) < 1: continue
            if symbol in closeDictJP:
                dataDictJP[symbol] = npArr
            else:
                dataDictUS[symbol] = npArr

update = False
if update:
    UpdateData()
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")
    
    pickle.dump(dataDictUS, open(picklePathUS, "wb"))
    print("pickle dump finished")
else:
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(picklePathUS, "rb")
    dataDictUS = pickle.load(output)
    output.close()

allDict = dataDictJP
allDict.update(dataDictUS)

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'MaxGain', 'LowestPreviousClose', 'PreviousGain', 'PreviousCloseLow', 'PreviousVolume','LowestIdx', 'LowestEntry', 'LowestLow', 'HighestHigh', 'VolumePercentage'])
        for symbol, maxGain, lowestPreviousClose, previousGain, previousCloseLow, previousVolume, lowestIdx, lowestEntry, lowestLow, highestHigh, volumePercentage in result_list:
            writer.writerow([symbol, maxGain, lowestPreviousClose, previousGain, previousCloseLow, previousVolume,lowestIdx, lowestEntry, lowestLow, highestHigh, volumePercentage])


closeJPDict = GetCloseJP()
closeUSDict = GetClose()


csvPath = f"{rootPath}/data/ShortSqueeze.csv"
shortSqueezeDict = load_csv_to_dict(csvPath)
print(shortSqueezeDict)

def CheckGain(symbol, dataDict, length, allDict):
    ignoreList = ["TOP"]

    if symbol in ignoreList:
        return [symbol, 0]
    npArr = dataDict[symbol]
    lowestLow = 9999
    maxGain = 0
    lowIdx = 0
    lowestLowIdx = 0
    highIdx = 1
    for i in range(0, len(npArr)):
        if i > 0:
            if npArr[i][2] / npArr[i-1][2] < 0.001:
                continue
            if npArr[i][1] / npArr[i-1][1] > 87: 
                continue
            if i > 3:
                if npArr[i-2][0] == npArr[i-3][0]:
                    continue
        low = npArr[i][2]
        if low < 0.01: continue
        if low < lowestLow:
            lowestLow = low
            lowIdx = i
        if i == lowIdx and npArr[i][3] < npArr[i][0]:
            continue
        high = npArr[i][1]
        gain = high / lowestLow
        if gain > maxGain:
            maxGain = gain
            lowestLowIdx = lowIdx
            highIdx = i

    diff = length-len(npArr)
    lowestLowIdx += diff
    highIdx += diff

    endIdx = -(length - highIdx)- 1
    startIdx = -(length - lowestLowIdx) - 1
    # print(startIdx, endIdx)
    passed = 1
    breakLoop = False

    if symbol in dataDictJP:
        for ticker, npArr in dataDictJP.items():
            if len(npArr) < length+endIdx+1: continue
            lowestLow = 9999
            lowIdx = 0
            if breakLoop: break
            if ticker in ignoreList: continue
            for i in range(length+startIdx+1, length+endIdx+1):
                try:
                    if i != 0:
                        if npArr[i][2] / npArr[i-1][2] < 0.001:
                            continue
                        if npArr[i][1] / npArr[i-1][1] > 87: 
                            continue
                        if i > 3:
                            if npArr[i-2][0] == npArr[i-3][0]:
                                continue
                except:
                    print(length+startIdx+1, length+endIdx-1, len(npArr))
                low = npArr[i][2]
                if low < 0.01: continue
                if low < lowestLow:
                    lowestLow = low
                    lowIdx = i
                if i == lowIdx and npArr[i][3] < npArr[i][0]:
                    continue
                high = npArr[i][1]
                gain = high / lowestLow
                if gain > maxGain:
                    passed = 0
                    breakLoop = True
                    break
        for ticker, npArr in dataDictUS.items():
            if len(npArr) < length+endIdx+2: continue
            lowestLow = 9999
            lowIdx = 0
            if breakLoop: break
            if ticker in ignoreList: continue
            for i in range(length+startIdx, length+endIdx+1):
                try:
                    if i != 0:
                        if npArr[i][2] / npArr[i-1][2] < 0.001:
                            continue
                        if npArr[i][1] / npArr[i-1][1] > 87: 
                            continue
                        if i > 3:
                            if npArr[i-2][0] == npArr[i-3][0]:
                                continue
                except:
                    print(length+startIdx+1, length+endIdx-1, len(npArr))
                low = npArr[i][2]
                if low < 0.01: continue
                if low < lowestLow:
                    lowestLow = low
                    lowIdx = i
                if i == lowIdx and npArr[i][3] < npArr[i][0]:
                    continue
                high = npArr[i][1]
                gain = high / lowestLow
                if gain > maxGain:
                    passed = 0
                    breakLoop = True
                    break

    if symbol in dataDictUS:
        for ticker, npArr in dataDictUS.items():
            if len(npArr) < length+endIdx+1: continue
            lowestLow = 9999
            lowIdx = 0
            if breakLoop: break
            if ticker in ignoreList: continue
            for i in range(length+startIdx+1, length+endIdx+1):
                try:
                    if i != 0:
                        if npArr[i][2] / npArr[i-1][2] < 0.001:
                            continue
                        if npArr[i][1] / npArr[i-1][1] > 87: 
                            continue
                        if i > 3:
                            if npArr[i-2][0] == npArr[i-3][0]:
                                continue
                except:
                    print(length+startIdx+1, length+endIdx-1, len(npArr))
                low = npArr[i][2]
                if low < 0.01: continue
                if low < lowestLow:
                    lowestLow = low
                    lowIdx = i
                if i == lowIdx and npArr[i][3] < npArr[i][0]:
                    continue
                high = npArr[i][1]
                gain = high / lowestLow
                if gain > maxGain:
                    passed = 0
                    breakLoop = True
                    break
        for ticker, npArr in dataDictJP.items():
            if len(npArr) < length+endIdx+2: continue
            lowestLow = 9999
            lowIdx = 0
            if breakLoop: break
            if ticker in ignoreList: continue
            for i in range(length+startIdx, length+endIdx+1):
                try:
                    if i != 0:
                        if npArr[i][2] / npArr[i-1][2] < 0.001:
                            continue
                        if npArr[i][1] / npArr[i-1][1] > 87: 
                            continue
                        if i > 3:
                            if npArr[i-2][0] == npArr[i-3][0]:
                                continue
                except:
                    print(length+startIdx+1, length+endIdx-1, len(npArr))
                low = npArr[i][2]
                if low < 0.01: continue
                if low < lowestLow:
                    lowestLow = low
                    lowIdx = i
                if i == lowIdx and npArr[i][3] < npArr[i][0]:
                    continue
                high = npArr[i][1]
                gain = high / lowestLow
                if gain > maxGain:
                    passed = 0
                    breakLoop = True
                    break
    return [symbol, passed]

passedList = []

length = len(dataDictUS[next(iter(dataDictUS.keys()))])
symbolList = []
for symbol in shortSqueezeDict.keys():
    if symbol not in closeDictUS: continue
    symbolList.append(symbol)

with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(CheckGain, symbol, dataDictUS, length, allDict) for symbol in symbolList]
    for future in as_completed(futures):
        result = future.result()
        ticker = result[0]
        passed = result[1]
        if passed < 1: continue
        passedList.append(ticker)

symbolList = []
for symbol in shortSqueezeDict.keys():
    if symbol not in closeDictJP: continue
    symbolList.append(symbol)

length = len(dataDictJP[next(iter(dataDictJP.keys()))])
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(CheckGain, symbol, dataDictJP, length, allDict) for symbol in symbolList]
    for future in as_completed(futures):
        result = future.result()
        ticker = result[0]
        passed = result[1]
        if passed < 1: continue
        passedList.append(ticker)

result_list = []
for symbol in shortSqueezeDict:
    if symbol not in passedList: continue
    res = shortSqueezeDict[symbol]

    result_list.append((symbol, float(res[0]), res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9]))
    result_list.sort(key=lambda x: x[1], reverse=True)

csvPath = f"{rootPath}/data/ShortSqueezeClean.csv"
dump_result_list_to_csv(result_list, csvPath)

import sys
sys.exit()

minEntryJP = 99999
maxEntryJP = 0
minEntryUS = 99999
maxEntryUS = 0

entryJP = []
entryUS = []
sharesPercentageJP = np.empty(0)
sharesPercentageUS = np.empty(0)

for symbol, res in shortSqueezeDict.items():
    maxGain = float(res[0])
    entry = float(res[1])
    sharesPercentage = float(res[4])
    if sharesPercentage == 0: continue
    if symbol in closeJPDict:
        entryJP.append(entry)
        sharesPercentageJP = np.append(sharesPercentageJP, sharesPercentage)
        # if entry < minEntryJP:
        #     minEntryJP = entry
        # elif entry > maxEntryJP:
        #     maxEntryJP = entry
    elif symbol in closeUSDict:
        entryUS.append(entry)
        sharesPercentageUS = np.append(sharesPercentageUS, sharesPercentage)
        # if entry < minEntryUS:
        #     minEntryUS = entry
        # elif entry > maxEntryUS:
        #     maxEntryUS = entry

print(minEntryJP, maxEntryJP)
print(minEntryUS, maxEntryUS)
print(entryJP[:10])
print(entryUS[:10])
sharesPercentageJP = np.sort(sharesPercentageJP)
sharesPercentageUS = np.sort(sharesPercentageUS)
# sharesPercentageJP = np.sort(sharesPercentageJP)[::-1]
# sharesPercentageUS = np.sort(sharesPercentageUS)[::-1]
print(sharesPercentageJP[:10])
print(sharesPercentageUS[:10])