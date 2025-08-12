rootPath = ".."
import sys
sys.path.append(rootPath)
import modules.kabudragon as kabudragon
import modules.aiztradingview as aiztradingview
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

closeJPDict = aiztradingview.GetCloseJP()
dataDictJP = {}
picklePathJP = f"{rootPath}/backtest/pickle/pro/compressed/dataDictJP.p"

zandakaPath = f"{rootPath}/backtest/pickle/pro/compressed/zandaka.p"
rironkabukaPath = f"{rootPath}/backtest/pickle/pro/compressed/rironkabuka.p"

# closeDict = GetClose()
# dataDict = {}
# picklePath = f"{rootPath}/backtest/pickle/pro/compressed/dataDict.p"

rironkabukaDict = {}
zandakaDict = {}
update = False
if update:
    for symbol, close in closeJPDict.items():
        # if symbol in ignoreList: continue
        npArr = GetNpDataDate(symbol, "JPY")
        if len(npArr) < 1: continue
        dataDictJP[symbol] = npArr
        rironkabuka = GetRironkabuka(symbol)
        zandaka = GetZandaka(symbol)
        rironkabukaDict[symbol] = rironkabuka
        zandakaDict[symbol] = zandaka
    pickle.dump(dataDictJP, open(picklePathJP, "wb"))
    print("pickle dump finished")
    
    # pickle.dump(zandakaDict, open(zandakaPath, "wb"))
    pickle.dump(rironkabukaDict, open(rironkabukaPath, "wb"))
    print(rironkabukaDict)
    print(zandakaDict)
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
    print("rr")
    print(rironkabukaDict)

dekizou = kabudragon.GetDekizou()
for symbol in dekizou:
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if zandaka[0][1] > zandaka[0][6]: continue
    if symbol not in closeJPDict: continue
    close = closeJPDict[symbol]
    if symbol not in rironkabukaDict: continue
    rironkabuka = rironkabukaDict[symbol]
    if close > rironkabuka: continue
    print(symbol, zandaka[0][0], zandaka[0][6])