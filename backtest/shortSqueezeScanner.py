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

attrDict = GetAttr("total_shares_outstanding_fundamental")
attrDictJP = GetAttrJP("total_shares_outstanding_fundamental")
attrDict.update(attrDictJP)

bond = yf.Ticker("^TNX")
hist = bond.history(period="max")
risk_free_rate = round(hist.iloc[-1]['Close']/100,4)

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

# @njit
def GetHighestGain(npArr, shares):
    sharesPercentageSecond = 0
    sharesPercentageThird = 0
    sharesPercentage = npArr[-1][4]/shares
    if len(npArr) > 1:
        sharesPercentageSecond = npArr[-2][4]/shares
    if len(npArr) > 2:
        sharesPercentageThird = npArr[-3][4]/shares
    return [sharesPercentage, sharesPercentageSecond, sharesPercentageThird ]

def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'VolumePercentage', 'VolumePercentageSecond', 'VolumePercentageThird'])
        for symbol, volumePercentage, volumePercentageSecond, volumePercentageThird in result_list:
            writer.writerow([symbol, volumePercentage, volumePercentageSecond, volumePercentageThird])

def GetSharpe(npArr, shares):
    try:
        res = GetHighestGain(npArr, shares)
        return res
    except:
        return 0

def HandleGetSharpe(symbol):
    try:
        ticker = symbol
        if ticker in closeDictJP: 
            ticker += ".T"
            npArr = dataDictJP[symbol]
        else:
            npArr = dataDictUS[symbol]
        res = GetSharpe(npArr, shares)
        return [symbol, res]
    except:
        return [symbol, 0]

csvPath = f"{rootPath}/data/ShortSqueezeScan.csv"
result_list = []
sharesPercentageLimit = 0.0009307523060585659
sharesPercentageLimitJP = 0.3172068676300444
with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(HandleGetSharpe, symbol) for symbol in symbolList]
    for future in as_completed(futures):
        result = future.result()
        symbol = result[0]
        res = result[1]
        if res == 0: continue
        sharesPercentage = res[0]
        sharesPercentageSecond = res[1]
        sharesPercentageThird = res[2]

        if sharesPercentage < sharesPercentageLimit: continue
        
        if symbol in closeDictJP:
            if sharesPercentage < sharesPercentageLimitJP: continue
        # if sharesPercentageSecond < sharesPercentageLimit: continue
        # if sharesPercentageThird < sharesPercentageLimit: continue
        # if symbol in closeDictJP:
        #     rironkabuka = GetRironkabuka(symbol)
        #     close = closeDictJP[symbol]
        #     if close > rironkabuka: continue
        result_list.append((symbol,  sharesPercentage, sharesPercentageSecond, sharesPercentageThird))
        result_list.sort(key=lambda x: x[1], reverse=True)
        dump_result_list_to_csv(result_list, csvPath)
# symbol = "ELVN"
# sharpe = HandleGetSharpe(symbol)
# print(sharpe)
