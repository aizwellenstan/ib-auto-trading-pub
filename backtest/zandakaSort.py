rootPath = '..'
import sys
sys.path.append(rootPath)
import modules.dividend as dividendModule

from modules.aiztradingview import GetCloseJP, GetAttrJP
from modules.rironkabuka import GetRironkabuka
from modules.margin import GetMargin, GetUSStock
from modules.csvDump import DumpCsv, DumpDict, LoadDict
from modules.dict import take
import pandas as pd
from modules.irbank import GetZandaka
import pickle
from numba import range
import numpy as np
from modules.data import GetNpDataDate

closeJPDict = GetCloseJP()
floatDictJP = GetAttrJP("float_shares_outstanding")
totalShareDictJP = GetAttrJP("total_shares_outstanding_fundamental")
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictForZandaka.p"

zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
dividendJP = f"{rootPath}/backtest/pickle/pro/compressed/dividendJP.p"

rironkabukaDict = {}
zandakaDict = {}
dividendDict = {}
update = False
if update:
    for symbol, close in closeJPDict.items():
        npArr = GetNpDataDate(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
        rironkabuka = GetRironkabuka(symbol)
        zandaka = GetZandaka(symbol)
        rironkabukaDict[symbol] = rironkabuka
        zandakaDict[symbol] = zandaka
        dividend = dividendModule.GetDividendData(symbol, 'JPY')
        dividendDict[symbol] = dividend

    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    # pickle.dump(zandakaDict, open(zandakaPath, "wb"))
    pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
    pickle.dump(dividendDict, open(dividendJP, "wb"))
    print(rironkabukaDict)
    print(zandakaDict)
    print("pickle dump finished")
else:
    # output = open(picklePathJP, "rb")
    # dataDictJP = pickle.load(output)
    # output.close()

    output = open(zandakaPath, "rb")
    zandakaDict = pickle.load(output)
    output.close()

    output = open(rironkabukaPath, "rb")
    rironkabukaDict = pickle.load(output)
    output.close()

    # output = open(dividendJP, "rb")
    # dividendDict = pickle.load(output)
    # output.close()

    # output = open(picklePath, "rb")
    # dataDict = pickle.load(output)
    # output.close()

# Buy when high1 break range
def CheckShortSqueeze(zandaka):
    return zandaka[0][7] - zandaka[0][1] 

zandakaHiritsuDict = {}
for symbol, close in closeJPDict.items():
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if symbol not in rironkabukaDict: continue
    rironkabuka = rironkabukaDict[symbol]
    if close >= rironkabuka - 5: continue
    zandakaHiritsu = CheckShortSqueeze(zandaka)
    floatShares = 0
    if symbol in floatDictJP:
        floatShares = floatDictJP[symbol]
    elif symbol in totalShareDictJP:
        floatShares = totalShareDictJP[symbol]
    zandakaHiritsuTofloatShares = zandakaHiritsu/floatShares
    if zandakaHiritsuTofloatShares <= 0: continue 
    zandakaHiritsuDict[symbol] = zandakaHiritsuTofloatShares

zandakaHiritsuDict = dict(sorted(zandakaHiritsuDict.items(), key=lambda item: item[1], reverse=True))
# print(zandakaHiritsuDict)

count = 0
newZandakaHiritsuDict = {}
for k, v in zandakaHiritsuDict.items():
    newZandakaHiritsuDict[k] = v
    count += 1
    # if count > 40:
    #     break
# print(newZandakaHiritsuDict)
import csv
def dump_result_list_to_csv(result_list, filename):
    with open(filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['Symbol', 'Price'])
        for symbol, price in result_list:
            writer.writerow([symbol, price])

tradeList = []
for symbol, v in newZandakaHiritsuDict.items():
    print(symbol, closeJPDict[symbol])
    tradeList.append([symbol,closeJPDict[symbol]])

csvPath = f"{rootPath}/data/ZandakaSort.csv"
dump_result_list_to_csv(tradeList, csvPath)