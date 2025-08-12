rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpData

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose
from modules.csvDump import DumpCsv, LoadCsv, DumpDict
import pickle

import csv
import concurrent.futures

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

closeDict = GetClose()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDict.p"

symbolListUS = list(closeDict.keys())
symbolListUS.append('QQQ')
symbolListUS.append('SPY')

update = False
if update:
    # for symbol, close in closeJPDict.items():
    #     if symbol in ignoreList: continue
    #     npArr = GetNpData(symbol, "JPY")
    #     if len(npArr) < 1: continue
    #     dataDictJP[symbol] = npArr
    # pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    # print("pickle dump finished")

    for symbol in symbolListUS:
        if symbol in ignoreList: continue
        npArr = GetNpData(symbol)
        if len(npArr) < 1: continue
        dataDict[symbol] = npArr
    
    pickle.dump(dataDict, open(picklePath, "wb"))
    print("pickle dump finished")
else:
    # output = open(picklePathJP, "rb")
    # dataDictJP = pickle.load(output)
    # output.close()

    output = open(picklePath, "rb")
    dataDict = pickle.load(output)
    output.close()

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'signal', 'period'])
        for symbol, signal, period, _ in result_list:
            writer.writerow([symbol, signal, period])

import numpy as np


# @njit
def calculate_balance(signalArr, npArr, signalPeriod):
    balance = 1
    position = 0
    entry_price = 0
    trade_size = 0
    for i in range(1, len(npArr) - signalPeriod):
        # detect highest point and lowest point
        signalCloseArr = signalArr[i:i + signalPeriod][:, 3]
        highest_index = np.argmax(signalCloseArr)
        lowest_index = np.argmin(signalCloseArr)
        if highest_index > lowest_index and highest_index > i and position == 0:
            # the trend is an uptrend and has upside potential
            position = 1
            entry_price = npArr[i, 0]
            trade_size = balance / entry_price
        else:
            exit_price = npArr[i, 0]
            balance += (exit_price - entry_price) * trade_size
            position = 0
    return balance

# @njit
def optimize_backtest(signal, symbol, signalArr, npArr):
    minLength = min(len(signalArr), len(npArr), 533)
    signalArr = signalArr[-minLength:]
    npArr = npArr[-minLength:]
    maxBalance = 0.0
    maxSignalPeriod = 0.0
    signalPeriod = 1
    while signalPeriod < len(npArr) - 1:
        balance = calculate_balance(signalArr, npArr, signalPeriod)
        if balance > maxBalance:
            maxBalance = balance
            maxSignalPeriod = signalPeriod
        signalPeriod += 1
    return symbol, signal, int(maxSignalPeriod), maxBalance


symbolList = [symbol for symbol in symbolListUS if symbol in dataDict]
csvPath = f"{rootPath}/data/leadUSQQQ.csv"

# symbolList = [symbol for symbol, close in closeJPDict.items() if symbol in dataDict]
# csvPath = f"{rootPath}/data/leadJP.csv"

comb = [(symbol, symbol2) for symbol in symbolList for symbol2 in symbolList if symbol != symbol2]


result_list = []
with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    futures = []
    for c in comb:
        signal = c[0]
        symbol = c[1]
        if symbol != "QQQ": continue
        signalArr = dataDict[signal]
        npArr = dataDict[symbol]
        futures.append(executor.submit(optimize_backtest, signal, symbol, signalArr, npArr))
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if len(result) < 4: continue
        if result[3] > 1:
            print(result[0], result[1], result[2], result[3])
            result_list.append((result[0], result[1], result[2], result[3]))
    result_list.sort(key=lambda x: x[3], reverse=True)
    dump_result_list_to_csv(result_list, csvPath)