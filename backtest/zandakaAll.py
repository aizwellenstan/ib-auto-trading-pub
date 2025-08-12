rootPath = '..'
import sys
sys.path.append(rootPath)
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

    # output = open(picklePath, "rb")
    # dataDict = pickle.load(output)
    # output.close()

# Buy when high break range
def CheckShortSqueeze(zandaka, npArr):
    low = npArr[-1][2]
    shortSqueeze = []
    resistance = []
    
    for i in range(0, len(zandaka)-1):
        if (
            zandaka[i][7] > 0
            # zandaka[i][2] > 0 and
            # zandaka[i][7] > zandaka[i+1][7] and
            # zandaka[i+1][7] > 0 and
            # zandaka[i+1][2] < 0
        ):
            # if zandaka[i][7]/floatShares <= 0.0030979434310469383:
            # if zandaka[i][7]/floatShares <= 0.00444519250356861:
            #     continue
            # if zandaka[i][7]/floatShares <= 0.007359926205565303:
            #     continue
            # if zandaka[i][7]/floatShares <= 0.009066591066717113:
            #     continue
            
            # if zandaka[i][2]/floatShares <= 0.00013745184419180725:
            #     continue
            # if -zandaka[i][2]/floatShares <= 0.00018192188100054404:
            #     continue
            date = zandaka[i][0]
            # backtestDate = "2023-04-07"
            # if date == backtestDate:
            #     print(backtestDate)
            #     print(zandaka[i][7]/floatShares)
            #     print(zandaka[i+1][6])
                # print('{0:.10f}'.format(zandaka[i][4]/floatShares))
                # 9101 0.01665573805999305
            #     print(zandaka[i][2]/floatShares)
            for j in range(0, len(npArr)):
                if not npArr[j][4] == date: continue
                # if npArr[j][1] > low:
                checkBreak = False
                for k in range(j+1, len(npArr)-1):
                    if npArr[k][3] > npArr[j][1]: 
                        checkBreak = True
                        break
                if not checkBreak:
                    shortSqueeze.append([date,npArr[j][1], npArr[j][2]])
                # else:
                    # print(date,npArr[j][1])
                break
        else:
            if -zandaka[i][7]/floatShares <= 0.00147114882279304164:
                continue
            date = zandaka[i][0]
            # print(date, -zandaka[i][7]/floatShares)
            for j in range(0, len(npArr)):
                if not npArr[j][4] == date: continue
                if npArr[j][1] > low:
                    checkBreak = False
                    for k in range(j+1, len(npArr)):
                        if npArr[k][3] > npArr[j][1]: 
                            checkBreak = True
                            break
                    if not checkBreak:
                        resistance.append([date,npArr[j][2]])
                break
    return shortSqueeze, resistance
    print(shortSqueeze)
    # print(resistance)
    # import sys
    # sys.exit(0)
    # high1 = npArr[-1][1]
    # resistance = []
    # for i in range(0, len(zandaka)):
    #     if zandaka[i][7] < 0: continue
    #     if zandaka[i][7]/floatShares <= 0.0030979434310469383:
    #         continue
    #     date = zandaka[i][0]
    #     for j in range(0, len(npArr)):
    #         if not npArr[j][4] == date: continue
    #         # print(npArr[j][1], npArr[j][2])
    #         resistance = npArr[j][2]
    #         if resistance > high1:
    #             # resistance.append(npArr[j][2])
    #             resistance.append([date,npArr[j][1], npArr[j][2]])
    #         else:
    #             print(date,npArr[j][1], npArr[j][2], "SHORT SQUEEZE")
    # print(resistance)

attrDict = GetAttrJP("float_shares_outstanding")
tradeList = ["8789","3878","4936","2395"]
for symbol, close in closeJPDict.items():
    # if symbol != "9101": continue
    # if symbol != "4519": continue
    if symbol not in tradeList: continue
    if symbol not in zandakaDict: continue
    zandaka = zandakaDict[symbol]
    if len(zandaka) < 1: continue
    if symbol not in rironkabukaDict: continue
    rironkabuka = rironkabukaDict[symbol]
    if close > rironkabuka: continue
    if symbol not in dataDictJP: continue
    npArr = dataDictJP[symbol]
    floatShares = attrDict[symbol]
    shortSqueeze, resistance = CheckShortSqueeze(zandaka, npArr)
    if len(shortSqueeze) > 1:
        print(symbol, shortSqueeze)
        print(symbol, resistance)
    