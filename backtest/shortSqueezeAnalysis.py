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

def GetData(symbol):
    try:
        ticker = symbol
        # if ticker in closeDictJP: 
        #     ticker += ".T"
        data = yf.Ticker(ticker).history(start="2021-03-19")
        npArr = data[["Open","High","Low","Close","Volume"]].to_numpy()
        return [symbol, npArr]
    except: return []

csvPath = f"{rootPath}/data/ShortSqueezeClean.csv"
shortSqueezeDict = load_csv_to_dict(csvPath)
print(shortSqueezeDict)

attrDict = GetAttr("total_shares_outstanding_fundamental")
# attrDict = GetAttr("net_income")
# attrDict = GetAttr("sector")
# attrDict = GetAttr("industry")
# attrDict = GetAttr("debt_to_equity")
# attrDict = GetAttr("net_debt")
# attrDict = GetAttr("total_assets")
# attrDict = GetAttr("return_on_assets")
# attrDict = GetAttr("return_on_invested_capital")
# attrDict = GetAttr("basic_eps_net_income")
# attrDict = GetAttr("market_cap_basic")

# attrDict = GetAttr("return_on_equity")




attrList = np.empty(0)
previousCloseList = np.empty(0)
volumePercentageList = np.empty(0)

gainDict = GetBestGainUS()

marketCapDict = {}
passedList = []
for symbol in list(shortSqueezeDict.keys()):
    if symbol not in attrDict: continue
    attr = attrDict[symbol]
    attrList = np.append(attrList, attr)
    res = shortSqueezeDict[symbol]
    previousClose = float(res[6])
    if previousClose != 1:
        previousCloseList = np.append(previousCloseList, previousClose)
    passedList.append(symbol)
    volumePercentage = float(res[9])
    volumePercentageList = np.append(volumePercentageList, volumePercentage)
    marketCap = previousClose * attrDict[symbol]
    print(symbol, previousClose, marketCap)
    marketCapDict[symbol] = marketCap

marketCapDict = dict(sorted(marketCapDict.items(), key=lambda item: item[1], reverse=True))
print(marketCapDict)
# print(attrList)
print(np.min(attrList), np.max(attrList))
print(np.min(previousCloseList), np.max(previousCloseList))
# print(np.min(volumePercentageList), np.max(volumePercentageList))

sys.exit()
for symbol in passedList:
    if symbol not in gainDict:
        print(symbol)

print(len(gainDict))

passedList = []
for symbol, close in gainDict.items():
    print(symbol, close)
    if symbol not in attrDict: continue
    shares = attrDict[symbol]
    npArr = GetData(symbol)[1]
    print(npArr[-1][4] , shares )
    if npArr[-1][4] / shares < 0.0009307523060585659: continue
    gain = npArr[-1][3] / npArr[-1][0]
    if (
        npArr[-1][4] >= 99600 and
        gain >= 0.8291457126888404 and 
        gain <= 1.0454545011205132 and
        npArr[-1][3] / npArr[-1][2] >= 1.0088383452209477
    ):
        passedList.append(symbol)
print(passedList)

print(marketCapDict)