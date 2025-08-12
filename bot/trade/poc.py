rootPath = "../.."
import sys
sys.path.append(rootPath)

from modules.data import GetNpDataVolumeWeekday

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose, GetAttr, GetAttrJP
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict
import pickle
import math

ignorePath = f"{rootPath}/data/IgnoreDividends.csv"
noTradePath = f"{rootPath}/data/NoTradeBias.csv"

ignoreList = LoadCsv(ignorePath)

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

closeDict = GetClose()
dataDict = {}
picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDict.p"

rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"

rironkabukaDict = {}
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

    output = open(rironkabukaPath, "rb")
    rironkabukaDict = pickle.load(output)
    output.close()

import csv

def load_csv_to_dict(filename):
    result_dict = {}
    with open(filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            symbol = row['Symbol']
            del row['Symbol']
            result_dict[symbol] = list(row.values())
    return result_dict

csvPath = f"{rootPath}/data/poc.csv"
result_dict = load_csv_to_dict(csvPath)

result_list = []
for symbol, attr in result_dict.items():
    poc_bars = int(attr[0])
    rr = round(float(attr[1]), 1)
    if symbol not in rironkabukaDict: continue
    if symbol in closeJPDict:
        npArr = dataDictJP[symbol]
        close = closeJPDict[symbol]
        devide = 1
    elif symbol in closeDict:
        npArr = dataDict[symbol]
        close = closeDict[symbol]
        devide = 100
    else: continue
    
    lows = npArr[:, 2]
    highs = npArr[:, 1]
    volumes = npArr[:, 4]

    # Find the price range for the last poc_bars bars
    price_range = np.arange(np.min(lows[-poc_bars:]), np.max(highs[-poc_bars:])+1)

    # Initialize an array to store the volume for each price level
    vol = np.zeros(len(price_range))

    # Loop through each price level and calculate the volume
    for i, price in enumerate(price_range):
        # Find the bars with low price <= current price <= high price for the last poc_bars bars
        mask = (lows[-poc_bars:] <= price) & (highs[-poc_bars:] >= price)
        # Calculate the total volume for the bars that meet the condition
        total_vol = np.sum(volumes[-poc_bars:][mask])
        # Store the total volume for the current price level
        vol[i] = total_vol

    # Find the price level with the highest volume of the last poc_bars bars
    poc_level = price_range[np.argmax(vol)]
    if devide == 1:
        poc_level = math.floor(poc_level)
    else:
        poc_level = math.floor(poc_level * devide) / devide

    # print(symbol, "Current POC level:", poc_level)

    # if symbol == "9101": print(poc_level)
    rironkabuka = rironkabukaDict[symbol]
    if close < poc_level and close < rironkabuka:
        print('poc', symbol, poc_level, poc_bars, rr)
        result_list.append((symbol, close/poc_level, poc_level, poc_bars, rr))
# result_list.sort(key=lambda x: x[1])
print(result_list)

import csv

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'poc_level','proc_bars', 'rr'])
        for symbol, _, poc_level, poc_bars, rr in result_list:
            writer.writerow([symbol, poc_level, poc_bars, rr])
csvPath = f"{rootPath}/data/poc_trade.csv"
dump_result_list_to_csv(result_list, csvPath)

# import modules.ib as ibc
# from modules.trade.vol import GetVolTp
# from modules.normalizeFloat import NormalizeFloat

# ibc = ibc.Ib()
# ib = ibc.GetIB(27)

# total_cash, avalible_cash = ibc.GetTotalCash()
# positions = ibc.GetAllPositions()
# basicPoint = 0.01