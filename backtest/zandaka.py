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
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictForZandaka.p"

zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"
dividendJP = f"{rootPath}/backtest/pickle/pro/compressed/dividendJP.p"

rironkabukaDict = {}
zandakaDict = {}
dividendDict = {}
update = True
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

    # output = open(picklePath, "rb")
    # dataDict = pickle.load(output)
    # output.close()

# Buy when high1 break range
def CheckShortSqueeze(zandaka, npArr, floatShares):
    low = npArr[-1][2]
    shortSqueeze = []
    resistance = []
    for i in range(0, len(zandaka)):
        if (
            zandaka[i][8] > 0
        ):
            if (zandaka[i][7] - zandaka[i][1]) / floatShares <= 0.03060710477327903:
                continue
            
            date = zandaka[i][0]
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
for symbol, close in closeJPDict.items():
    if symbol in checkedList: continue
    # if symbol != "9101": continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if symbol not in rironkabukaDict: continue
    rironkabuka = rironkabukaDict[symbol]
    if close >= rironkabuka - 5: continue
    if symbol not in dividendDict:
        dividend = dividendModule.GetDividendData(symbol, 'JPY')
        dividendDict[symbol] = dividend
    else:
        dividend = dividendDict[symbol]
    if dividend < 1: continue
    dividendToPrice = dividend/close
    if dividendToPrice <= 0.1324354657687991:
        continue
    # print(symbol, 'divToPrice', dividendToPrice)

    if symbol not in dataDictJP: continue
    npArr = dataDictJP[symbol]
    floatShares = attrDict[symbol]
    shortSqueeze, resistance = CheckShortSqueeze(zandaka, npArr, floatShares)
    if len(shortSqueeze) > 0:
        if len(resistance) > 0:
            print(symbol, shortSqueeze[:6])
            print(symbol, resistance[:6])
