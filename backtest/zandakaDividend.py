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

# rironkabuakaPath = f"{rootPath}/data/Rironkabuka.csv"

closeJPDict = GetCloseJP()
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
    output = open(picklePathJP, "rb")
    dataDictJP = pickle.load(output)
    output.close()

    output = open(zandakaPath, "rb")
    zandakaDict = pickle.load(output)
    output.close()

    output = open(rironkabukaPath, "rb")
    rironkabukaDict = pickle.load(output)
    output.close()

    output = open(dividendJP, "rb")
    dividendDict = pickle.load(output)
    output.close()

# Buy when high1 break range
def CheckShortSqueeze(zandaka, npArr, floatShares):
    low = npArr[-1][2]
    shortSqueeze = []
    resistance = []
    
    print(zandaka[0][1],zandaka[0][7])
    print(zandaka[0][1],zandaka[0][3])
    for i in range(0, len(zandaka)):
        if (
            zandaka[i][8] > 0
        ):
            if (zandaka[i][7] - zandaka[i][1]) / floatShares <= 0.030253359960790177:
                continue
            
            date = zandaka[i][0]
            # if date == '2023-03-31':
            #     print((zandaka[i][7] - zandaka[i][1]) / floatShares)
            # idx = np.where(npArr[:, 4] == date)[0][0]
            # shortSqueeze.append([date,npArr[idx][1], npArr[idx][2]])
            shortSqueeze.append(date)
        else:
            if (zandaka[i][7] - zandaka[i][1]) / floatShares >= 0.036496933449182034:
                continue
            date = zandaka[i][0]
            # idx = np.where(npArr[:, 4] == date)[0][0]
            # resistance.append([date,npArr[idx][2]])
            resistance.append(date)
    return shortSqueeze, resistance

attrDict = GetAttrJP("float_shares_outstanding")
checkedList = []
tradable = []
for symbol, close in closeJPDict.items():
    if symbol in checkedList: continue
    # if symbol != "1941": continue
    # if symbol != "9101": continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if symbol not in rironkabukaDict: continue
    rironkabuka = rironkabukaDict[symbol]
    if close > rironkabuka: continue
    if symbol not in dividendDict:
        dividend = dividendModule.GetDividendData(symbol, 'JPY')
        dividendDict[symbol] = dividend
    else:
        dividend = dividendDict[symbol]
    if dividend < 1: continue
    dividendToPrice = dividend/close
    # print(symbol, 'divToPrice', dividendToPrice)
    # if dividendToPrice <= 0.0888373889532638:
    #     continue
    if zandaka[0][3] < 1: continue
    if zandaka[0][1] / zandaka[0][3] >= 1: continue

    if symbol not in dataDictJP: continue
    npArr = dataDictJP[symbol]
    floatShares = attrDict[symbol]
    # shortSqueeze, resistance = CheckShortSqueeze(zandaka, npArr, floatShares)
    
    # tradable.append(symbol)
    # if len(shortSqueeze) > 0:
    #     if len(resistance) > 0:
    #         # print(symbol, shortSqueeze[:6])
    #         # print(symbol, resistance[:6])
    #         print(symbol, shortSqueeze[:7])
    #         print(symbol, resistance[:7])
print(tradable)

import pandas as pd
portfolioPath = f'{rootPath}/data/PortfolioRiron.csv'
import os
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    keepOpenList = list(df.Symbol.values)

tradeList = []
for symbol in keepOpenList:
    if symbol in tradable:
        tradeList.append(symbol)
print(tradeList)
for symbol in tradeList:
    zandaka = zandakaDict[symbol]
    npArr = dataDictJP[symbol]
    floatShares = attrDict[symbol]
    shortSqueeze, resistance = CheckShortSqueeze(zandaka, npArr, floatShares)
    
    if len(shortSqueeze) > 0:
        if len(resistance) > 0:
            # print(symbol, shortSqueeze[:6])
            # print(symbol, resistance[:6])
            print(symbol, shortSqueeze[:7])
            print(symbol, resistance[:7])