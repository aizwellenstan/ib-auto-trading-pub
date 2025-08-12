rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolumeWeekday

import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose
from modules.csvDump import LoadCsv
import pickle
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.rironkabuka import GetRironkabuka
from modules.movingAverage import SmaArr

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

closeDict = GetClose()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDict.p"
rironkabukaDict = {}

update = False
if update:
    npArr = GetNpDataVolumeWeekday("^N225")
    dataDict["^N225"] = npArr
    for symbol, close in closeJPDict.items():
        if symbol in ignoreList: continue
        npArr = GetNpDataVolumeWeekday(symbol, "JPY")
        if len(npArr) < 1: continue
        rironkabuka = GetRironkabuka(symbol)
        rironkabukaDict[symbol] = rironkabuka
        dataDictJP[symbol] = npArr
    pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
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

    output = open(rironkabukaPath, "rb")
    rironkabukaDict = pickle.load(output)
    output.close()

# @njit
def calc_vol_price(price_range, closes, volumes):
    vol_price = np.zeros(len(price_range))
    for i, price in enumerate(price_range):
        mask = (closes == price)
        total_vol = np.sum(volumes[mask])
        vol_price[i] = total_vol * price
    return vol_price

# @njit
def calc_pl_for_bars(npArr, RR, lows, highs, closes):
    position = 0
    balance = 1
    for i in range(1, len(npArr)-1):
        closeArr = SmaArr(closes[:,3])
        if (
            position == 0 and
            npArr[i][0] > npArr[i-1][3] 
        ):
            sl = npArr[i-1][3]
            op = npArr[i,0]
            trade_size = balance / op
            position = 1
            target_price = op + (op-sl) * RR
        elif (npArr[i,2] < sl or npArr[i,1] >= target_price) and position == 1:
            exit_price = target_price if npArr[i,1] >= target_price else sl
            balance += (exit_price - op) * trade_size
            position = 0
    return (RR, balance)

def find_best_pl(npArr):
    RR_range = np.arange(1, 30.1, 0.1)
    pl_dict = {}
    lows = npArr[:, 2]
    highs = npArr[:, 1]
    closes = npArr[:, 3]
    # volumes = npArr[:, 4]

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(calc_pl_for_bars, npArr, RR, lows, highs, closes) for RR in RR_range]
        for future in as_completed(futures):
            result = future.result()
            pl_dict[result[0]] = result[1]

    best_RR = max(pl_dict, key=pl_dict.get)
    best_pl = pl_dict[best_RR]

    return best_RR, best_pl

import time
def calc_best_pl_for_all_symbols(symbol_list, dataDict):
    result_list = []
    for symbol in symbol_list:
        if symbol in closeJPDict:
            if symbol not in rironkabukaDict: continue
            close = closeJPDict[symbol]
            rironkabuka = rironkabukaDict[symbol]
            if close > rironkabuka: continue
        npArr = dataDict[symbol][-530:]
        start_time = time.time()
        best_RR, best_pl = find_best_pl(npArr)
        end_time = time.time()
        print("Elapsed time:", end_time - start_time, "seconds")
        print(symbol, best_RR, best_pl)
        if best_pl <= 1: continue
        result_list.append((symbol, best_RR, best_pl))
    result_list.sort(key=lambda x: x[2], reverse=True)
    return result_list
    
def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'rr', 'pl'])
        for symbol, best_rr, best_pl in result_list:
            writer.writerow([symbol, best_rr, best_pl])

symbol_list = list(dataDictJP.keys())
symbol_list2 = list(dataDict.keys())

symbol_list.extend(symbol_list2)
dataDictJP.update(dataDict)

result_list = calc_best_pl_for_all_symbols(symbol_list, dataDictJP)
print(result_list)

result_list_JP = []
result_list_US = []
for symbol, best_rr, best_pl in result_list:
    if symbol in closeJPDict:
        result_list_JP.append((symbol, best_rr, best_pl))
    else:
        result_list_US.append((symbol, best_rr, best_pl))
csvPath = f"{rootPath}/data/gapAttrJP.csv"
dump_result_list_to_csv(result_list_JP, csvPath)
csvPath = f"{rootPath}/data/gapAttrUS.csv"
dump_result_list_to_csv(result_list_US, csvPath)
