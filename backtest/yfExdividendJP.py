rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.data import GetDateWithDividends

import numpy as np

from modules.aiztradingview import GetCloseJP
import pickle
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.rironkabuka import GetRironkabuka

closeJPDict = GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJPDividends.p"
rironkabukaDict = {}
rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"

update = False
if update:
    npArr = GetDateWithDividends("^N225")
    dataDictJP["^N225"] = npArr
    for symbol, close in closeJPDict.items():
        npArr = GetDateWithDividends(symbol, "JPY")
        if len(npArr) < 1: continue
        rironkabuka = GetRironkabuka(symbol)
        rironkabukaDict[symbol] = rironkabuka
        dataDictJP[symbol] = npArr
    pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")

else:
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(rironkabukaPath, "rb")
    rironkabukaDict = pickle.load(output)
    output.close()

# https://www.kabuyutai.com/yutai/may.html

def GetExDividendMonth(npArr):
    monthList = np.empty(0)
    for i in range(0, len(npArr)):
        if npArr[i][4] > 0:
            year, month, date = npArr[i][5].split("-")
            month = int(month)
            if month in monthList: continue
            monthList = np.append(monthList, month)
    return monthList

import pandas as pd
currency = "JPY"
exDividendPath = f"{rootPath}/data/ExDividendMay.csv"
resDict = {}
for symbol, close in closeJPDict.items():
    if symbol not in rironkabukaDict: continue
    if symbol not in dataDictJP: continue
    rironkabaka = rironkabukaDict[symbol]
    if close >= rironkabaka: continue
    npArr = GetDateWithDividends(symbol, currency)
    monthList = GetExDividendMonth(npArr)
    print(symbol, monthList)
    if 5 in monthList:
        resDict[symbol] = monthList
        df = pd.DataFrame()
        df['Symbol'] = resDict.keys()
        df.to_csv(exDividendPath)
            