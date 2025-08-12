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

RR_range = np.arange(12, 30.1, 0.1)
poc_range = range(2, 101)


# @njit
def calc_vol_price(price_range, closes, volumes):
    vol_price = np.zeros(len(price_range))
    for i, price in enumerate(price_range):
        mask = (closes == price)
        total_vol = np.sum(volumes[mask])
        vol_price[i] = total_vol * price
    return vol_price

# @njit
def calc_pl_for_bars(poc_bars, RR, npArr, lows, highs, closes, volumes, initial_balance=1):
    price_range = np.unique(npArr[:, 3])
    vol_price = calc_vol_price(price_range, closes[-poc_bars:], volumes[-poc_bars:])
    poc_level = price_range[np.argmax(vol_price)]
    position = 0
    pl = initial_balance
    for i in range(poc_bars, len(npArr)-1):
        if npArr[i,3] < poc_level and position == 0:
            position = 1
            entry_price = npArr[i,0]
            trade_size = pl / entry_price
            sl = npArr[i,0] - (poc_level - npArr[i,0])/RR
            target_price = poc_level
        elif (npArr[i,2] < sl or npArr[i,1] >= target_price) and position == 1:
            exit_price = target_price if npArr[i,1] >= target_price else sl
            pl += (exit_price - entry_price) * trade_size
            position = 0
    return (poc_bars, RR, pl)

def find_best_pl(npArr):
    pl_dict = {}
    lows = npArr[:, 2]
    highs = npArr[:, 1]
    closes = npArr[:, 3]
    volumes = npArr[:, 4]

    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(calc_pl_for_bars, poc_bars, RR, npArr, lows, highs, closes, volumes) for poc_bars in poc_range for RR in RR_range]
        for future in as_completed(futures):
            result = future.result()
            pl_dict[(result[0], result[1])] = result[2]

    best_poc, best_RR = max(pl_dict, key=pl_dict.get)
    best_pl = pl_dict[(best_poc, best_RR)]

    return best_poc, best_RR, best_pl


import time


def calc_best_pl_for_all_symbols(symbol_list, dataDict):
    result_list = []
    for symbol in symbol_list:
        npArr = dataDict[symbol][-530:]
        start_time = time.time()
        best_poc, best_RR, best_pl = find_best_pl(npArr)
        end_time = time.time()
        print("Elapsed time:", end_time - start_time, "seconds")
        print(symbol, best_poc, best_RR, best_pl)
        result_list.append((symbol, best_poc, best_RR, best_pl))
    result_list.sort(key=lambda x: x[3], reverse=True)
    return result_list

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'days', 'rr'])
        for symbol, best_poc, best_RR, _ in result_list:
            writer.writerow([symbol, best_poc, best_RR])


symbol_list = list(dataDictJP.keys())
symbol_list2 = list(dataDict.keys())

symbol_list.extend(symbol_list2)
dataDictJP.update(dataDict)

result_list = calc_best_pl_for_all_symbols(symbol_list, dataDictJP)
print(result_list)
csvPath = f"{rootPath}/data/poc.csv"
dump_result_list_to_csv(result_list, csvPath)