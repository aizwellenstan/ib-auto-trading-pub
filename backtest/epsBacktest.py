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

# @njit
def split_list_average_high_low(lst):
    # Calculate the average of all values in the list
    average = np.mean(lst)
    
    # Filter high values and calculate the average
    high_values = lst[lst > average]
    average_high = np.mean(high_values)
    
    # Filter low values and calculate the average
    low_values = lst[lst < average]
    average_low = np.mean(low_values)
    
    return np.array([average_high, average_low])

for symobl in symbolList