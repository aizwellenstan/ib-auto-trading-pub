rootPath = ".."
import sys
sys.path.append(rootPath)
from concurrent.futures import ThreadPoolExecutor, as_completed
import yfinance as yf
import pandas as pd
import numpy as np
from modules.aiztradingview import GetClose, GetCloseJP, GetAttr, GetAttrJP
from modules.rironkabuka import GetRironkabuka
import csv

import math
import pickle

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

attrDict = GetAttr("total_shares_outstanding_fundamental")
attrDictJP = GetAttrJP("total_shares_outstanding_fundamental")
attrDict.update(attrDictJP)

bond = yf.Ticker("^TNX")
hist = bond.history(period="max")
risk_free_rate = round(hist.iloc[-1]['Close']/100,4)

# @njit
def GetHighestGain(npArr, shares):
    lowestLow = 99999
    lowIdx = 0
    maxGainLowIdx = 0
    maxGainHighIdx = 0
    maxGain = 0
    highestHigh = 0
    lowestEntry = 0.01
    lowestClose = 0.01
    lowestOpen = 0.01
    lowestPreviousClose = 0.01
    previousGain = 1
    lowestPreviousGain = 1
    previousCloseLow = 1
    lowestPreviousCloseLow = 1
    previousVolume = 0
    lowestPreviousVolume = 1
    maxSharesPercentage = 0
    maxSharesPercentageSecond = 0
    maxSharesPercentageThird = 0
    maxSharesPercentageForth = 0
    change = 0
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
            if i != 0: 
                lowestClose = npArr[i-1][3]
            else:
                lowestClose = npArr[i][0]
            lowestOpen = npArr[i][0]
            lowIdx = i
            if i != 0: 
                previousGain = npArr[i-1][3]/npArr[i-1][0]
            if i != 0: 
                previousVolume = npArr[i-1][4]
            lowestOpen = npArr[i][0]
            if i != 0: 
                previousCloseLow = npArr[i-1][3]/npArr[i-1][2]
        high = npArr[i][1]
        if i == lowIdx and npArr[i][3] < npArr[i][0]:
            continue
        gain = high / lowestLow
        if gain > maxGain:
            maxGainLowIdx = lowIdx
            maxGainHighIdx = i
            maxGain = gain
            highestHigh = high
            lowestEntry = lowestLow
            lowestEntryOpen = lowestOpen
            lowestPreviousGain = previousGain
            lowestPreviousCloseLow = previousCloseLow
            lowestPreviousVolume = previousVolume
            lowestIdx = lowIdx
            lowestPreviousClose = lowestClose
    if lowestEntry == 99999: maxGain = 0

    sharesPercentage = npArr[maxGainLowIdx][4]/shares
    return [maxGain, lowestPreviousClose, lowestPreviousGain, lowestPreviousCloseLow, lowestPreviousVolume, lowestIdx, lowestEntryOpen, lowestEntry, highestHigh, sharesPercentage]

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'MaxGain', 'LowestPreviousClose', 'PreviousGain', 'PreviousCloseLow', 'PreviousVolume', 'LowestIdx', 'LowestEntry', 'LowestLow', 'HighestHigh', 'VolumePercentage'])
        for symbol, maxGain, lowestPreviousClose, previousGain, previousCloseLow, previousVolume,lowestIdx, lowestEntry, lowestLow, highestHigh, volumePercentage in result_list:
            writer.writerow([symbol, maxGain, lowestPreviousClose, previousGain, previousCloseLow, previousVolume,lowestIdx, lowestEntry, lowestLow, highestHigh, volumePercentage])

def GetSharpe(npArr, shares):
    try:
        res = GetHighestGain(npArr, shares)
        return res
    except:
        return 0

def HandleGetSharpe(symbol):
    try:
        ticker = symbol
        if symbol in attrDict:
            shares = attrDict[symbol]
        else:
            return [symbol, 0]
        if ticker in closeDictJP: 
            ticker += ".T"
            npArr = dataDictJP[symbol]
        else:
            npArr = dataDictUS[symbol]
        res = GetSharpe(npArr, shares)
        return [symbol, res]
    except:
        return [symbol, 0]

csvPath = f"{rootPath}/data/ShortSqueeze.csv"
result_list = []
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleGetSharpe, symbol) for symbol in symbolList]
    for future in as_completed(futures):
        result = future.result()
        symbol = result[0]
        res = result[1]
        if res == 0: continue
        # if symbol in closeDictJP:
        #     rironkabuka = GetRironkabuka(symbol)
        #     close = closeDictJP[symbol]
        #     if close > rironkabuka: continue
        if res[0] < 1: continue
        result_list.append((symbol,  res[0], res[1], res[2], res[3], res[4], res[5], res[6], res[7], res[8], res[9]))
        result_list.sort(key=lambda x: x[1], reverse=True)
        dump_result_list_to_csv(result_list, csvPath)
# symbol = "HKD"
# sharpe = HandleGetSharpe(symbol)
# print(sharpe)
