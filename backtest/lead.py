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

# @njit
def Backtest(signalArr, npArr):
    minLength = min(len(signalArr),len(npArr),533)
    signalArr = signalArr[-minLength:]
    npArr = npArr[-minLength:]
    maxBalance = 0.0
    maxSignalPeriod = 0.0
    signalPeriod = 1
    while signalPeriod < len(npArr) - 1:
        balance = 1
        position = 0
        entry_price = 0
        trade_size = 0
        for i in range(1, len(npArr)-signalPeriod):
            # detect highespoint lowestpoint
            signalCloseArr = signalArr[i:i+signalPeriod][:,3]
            highest_index = np.argmax(signalCloseArr)
            lowesest_index = np.argmin(signalCloseArr)
            if (
                highest_index > lowesest_index and
                highest_index > i and position == 0
            ):
                # the trend is up trend and have upside potencial
                # gain = npArr[i][3] / npArr[i][0]
                # balance *= gain
                position = 1
                entry_price = npArr[i,0]
                trade_size = balance / entry_price
            else:
                exit_price = npArr[i,0]
                balance += (exit_price - entry_price) * trade_size
                position = 0
        if balance > maxBalance:
            maxBalance = balance
            maxSignalPeriod = signalPeriod
        signalPeriod += 1
    return np.array([maxBalance,maxSignalPeriod])

import csv
def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'signal', 'period'])
        for symbol, signal, period, _ in result_list:
            writer.writerow([symbol, signal, period])

symbolList = []
for symbol, close in closeDict.items():
    if symbol not in dataDict: continue
    symbolList.append(symbol)

comb = []
for symbol in symbolList:
    for symbol2 in symbolList:
        if symbol == symbol2: continue
        comb.append([symbol,symbol2])

csvPath = f"{rootPath}/data/leadUS.csv"
result_list = []
oldSymbol = ""
for c in comb:
    signal = c[0]
    symbol = c[1]
    signalArr = dataDict[signal]
    npArr = dataDict[symbol]
    res = Backtest(signalArr, npArr)
    if res[0] <= 1: continue
    print(symbol, signal, res[0], int(res[1]))
    result_list.append((symbol, signal, res[1], res[0]))
    if symbol != oldSymbol:
        oldSymbol = symbol
        result_list.sort(key=lambda x: x[3], reverse=True)
        new_result_list = []
        added = []
        for symbol, signal, res[1], res[0] in result_list:
            if symbol not in added:
                new_result_list.append((symbol, signal, res[1], res[0]))
                added.append(symbol)
        result_list = new_result_list
        dump_result_list_to_csv(result_list, csvPath)


# csvPath = f"{rootPath}/data/leadJP.csv"
# symbolList = []
# for symbol, close in closeJPDict.items():
#     if symbol not in dataDictJP: continue
#     symbolList.append(symbol)

# comb = []
# for symbol in symbolList:
#     for symbol2 in symbolList:
#         if symbol == symbol2: continue
#         comb.append([symbol,symbol2])

# result_list = []
# oldSymbol = ""
# for c in comb:
#     signal = c[0]
#     symbol = c[1]
#     signalArr = dataDictJP[signal]
#     npArr = dataDictJP[symbol]
#     res = Backtest(signalArr, npArr)
#     if res[0] <= 1: continue
#     print(symbol, signal, res[0], int(res[1]))
#     result_list.append((symbol, signal, res[1], res[0]))
#     if symbol != oldSymbol:
#         oldSymbol = symbol
#         result_list.sort(key=lambda x: x[3], reverse=True)
#         new_result_list = []
#         added = []
#         for symbol, signal, res[1], res[0] in result_list:
#             if symbol not in added:
#                 new_result_list.append((symbol, signal, res[1], res[0]))
#                 added.append(symbol)
#         result_list = new_result_list
#         dump_result_list_to_csv(result_list, csvPath)