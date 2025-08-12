rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetNpDataVolumeWeekday

from modules.movingAverage import SmaArr
import numpy as np
from modules.aiztradingview import GetCloseJP, GetClose, GetAttr, GetAttrJP
from modules.csvDump import DumpCsv, LoadCsv, DumpDict, LoadDict
import pickle
import math
from modules.dividendCalendar import GetExDividendNp
from modules.normalizeFloat import NormalizeFloat
import csv
from modules.trade.vol import GetVol

def load_csv_to_dict(filename):
    result_dict = {}
    with open(filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            symbol = row['Symbol']
            del row['Symbol']
            result_dict[symbol] = list(row.values())
    return result_dict

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'poc_level', 'rr'])
        for symbol, poc_level, rr in result_list:
            writer.writerow([symbol, poc_level, rr])

def GetPocLevel(npArr, poc_bars, devide=100):
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
    return poc_level

csvPath = f"{rootPath}/data/poc.csv"
result_dict = load_csv_to_dict(csvPath)

dividendList = []
tradeList = []
passed = []
for i in range(1, 90):
    dividendList = GetExDividendNp(i)
    print(dividendList,i)
    for symbol, div in dividendList:
        if symbol not in result_dict: continue
        npArr = GetNpDataVolumeWeekday(symbol)
        if len(npArr) < 1: continue
        attr = result_dict[symbol]
        poc_bars = int(attr[0])
        rr = round(float(attr[1]), 1)
        poc_level = GetPocLevel(npArr,poc_bars)
        # print(symbol, poc_level)
        if poc_level > npArr[-1][3]:
            passed.append([symbol,poc_level,npArr[-1][3]])
            op = npArr[-1][3]
            tp = poc_level
            sl = op - (tp - op) / rr
            sl = NormalizeFloat(sl, 0.01)
            vol = GetVol(
                total_cash,avalible_cash,op,sl,'USD'
            )
            # if vol < 1: vol = 1
            if (tp - op) * vol < 2: continue
            tradeList.append([symbol, poc_level, rr])
    if len(tradeList) > 0: break
print(tradeList)
print(passed)
csvPath = f"{rootPath}/data/ExDividendPoc.csv"
dump_result_list_to_csv(tradeList, csvPath)
