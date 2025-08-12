rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
from modules.movingAverage import SmaArr

from modules.csvDump import LoadCsv
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import pickle
from modules.dict import take
from modules.csvDump import LoadDict

optionPath = f"{rootPath}/data/tradableOption.csv"
optionDict = LoadDict(optionPath, "Length")

dataPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataDictUS = LoadPickle(dataPathUS)

def Backtest(dataDict, length, 
    sampleArrJP, gainnerDict):
    balance = 1
    maxBalance = 1
    attrList = []
    ddList = []
    mddList = []
    sma25Dict = {}

    topPerf = 0
    toSymbol = ""

    for i in range(5, length):
        isShort = False
        topPerf = 99
        topSymbol = ""
        today = sampleArrJP[i][5]
        # print(today,i)
        perfDict = {}
        
        if not isShort:
            for symbol, npArr in dataDict.items():
                if npArr[i-1][0] == 0: continue
                if npArr[i][0] < npArr[i-1][3]: continue
                # if npArr[i-1][3] > npArr[i-1][1]: continue
                # # if symbol not in gainnerDict[i]: continue
                # if npArr[i-1][3] / npArr[i-3][2] >= 1.5317460317460319: continue
                # if npArr[i-2][4] < 1: continue
                # if npArr[i-4][4] < 1: continue
                # if npArr[i-1][2] * npArr[i-1][4] < 4107114847: continue
                
                # if (
                #     npArr[i-3][3] / npArr[i-3][0] > 1.21 and
                #     npArr[i-3][4] / npArr[i-4][4] > 7 and
                #     npArr[i-3][0] < npArr[i-4][2]
                # ): continue

                # if (
                #     (npArr[i-1][1] - npArr[i-1][2]) / 
                #     (abs(npArr[i-1][3]-npArr[i-1][0]) + 1)
                # ) >= 151.92919921875: continue

                # if (
                #     (npArr[i-1][3] - npArr[i-1][2]) / 
                #     (abs(npArr[i-1][3]-npArr[i-1][0]) + 1)
                # ) >= 68.70204960111414: continue

                # if (
                #     abs(npArr[i-1][3] - npArr[i-3][0]) /
                #     (abs(npArr[i-3][3] - npArr[i-5][0]) + 1)
                # ) >= 165.22058251568: continue

                # if (
                #     abs(npArr[i-1][3] - npArr[i-3][0]) /
                #     (abs(npArr[i-4][3] - npArr[i-6][0]) + 1)
                # ) >= 88.06833117614251: continue

                # if (
                #     abs(npArr[i-1][3] - npArr[i-5][0]) /
                #     (abs(npArr[i-2][3] - npArr[i-6][0]) + 1)
                # ) >= 79.0909090909091: continue

                # if (
                #     abs(npArr[i-1][3] - npArr[i-5][0]) /
                #     (abs(npArr[i-4][3] - npArr[i-8][0]) + 1)
                # ) >= 101.7412903636711: continue

                # if (
                #     abs(npArr[i-1][3] - npArr[i-5][0]) /
                #     (abs(npArr[i-6][3] - npArr[i-10][0]) + 1)
                # ) >= 643.1508052708639: continue

                # if (
                #     abs(npArr[i-1][3] - npArr[i-6][0]) /
                #     (abs(npArr[i-2][3] - npArr[i-7][0]) + 1)
                # ) >= 41.325315739215526: continue

                # change = npArr[i-2][3] / npArr[i-2][0]
                # if change > 0:
                #     if (
                #         (
                #             npArr[i-1][3] / npArr[i-1][0] -
                #             change
                #         ) / change
                #     ) >= 0.2514813523875914: continue

                # change = abs(npArr[i-2][3] - npArr[i-2][0])
                # if change > 0:
                #     if (
                #         abs(npArr[i-1][3] - npArr[i-1][0]) /
                #         change
                #     ) >= 14.9: continue

                # deltaPeriod = 2
                # b = 0
                # s = 0
                # for j in range(i-deltaPeriod, i):
                #     if npArr[j][3] > npArr[j][0]:
                #         b += npArr[j][4]
                #     elif npArr[j][3] < npArr[j][0]:
                #         s += npArr[j][4]
                # b2 = 0
                # s2 = 0
                # for j in range(i-deltaPeriod-1, i-1):
                #     if npArr[j][3] > npArr[j][0]:
                #         b2 += npArr[j][4]
                #     elif npArr[j][3] < npArr[j][0]:
                #         s2 += npArr[j][4]

                # d2 = b2 - s2
                # if d2 != 0:
                #     delta = ((b-s) - d2) / d2
                #     if delta >= 27.555973387330056: continue

                # deltaPeriod = 3
                # b = 0
                # s = 0
                # for j in range(i-deltaPeriod, i):
                #     if npArr[j][3] > npArr[j][0]:
                #         b += npArr[j][4]
                #     elif npArr[j][3] < npArr[j][0]:
                #         s += npArr[j][4]
                # b2 = 0
                # s2 = 0
                # for j in range(i-deltaPeriod-1, i-1):
                #     if npArr[j][3] > npArr[j][0]:
                #         b2 += npArr[j][4]
                #     elif npArr[j][3] < npArr[j][0]:
                #         s2 += npArr[j][4]

                # d2 = b2 - s2
                # if d2 != 0:
                #     delta = ((b-s) - d2) / d2
                #     if delta >= 113.20631341600902: continue

                # if symbol not in sma25Dict:
                #     closeArr = npArr[:,3]
                #     sma25 = SmaArr(closeArr, 25)
                #     sma25Dict[symbol] = sma25
                # else:
                #     sma25 = sma25Dict[symbol]
                # bias = (
                #     (npArr[i-1][3] - sma25[i-1]) / 
                #     sma25[i-1]
                # )
                # if bias < -0.2: continue
                # # if bias >= 0.7702747072343219: continue

                # try:
                #     peArr = np.empty(0)
                #     for j in range(2, 8):
                #         peArr = np.append(peArr, npArr[i-j][3])
                #     avgHighLow = split_list_average_high_low(peArr)
                #     if peArr[0]/avgHighLow[1] > 1.61: continue
                # except: pass

                perf = (
                    abs(npArr[i-1][3] - npArr[i-1][0]) /
                    (abs(npArr[i-2][3] - npArr[i-2][0]) + 1)
                )

                if perf < topPerf:
                    topPerf = perf
                    topSymbol = symbol
                perfDict[symbol] = perf
        # if topSymbol == "": continue
        # npArr = dataDict[topSymbol]
        # # sl = npArr[i][0] * 0.98
        # # if npArr[i-1][7] < npArr[i][0]:
        # #     sl = npArr[i-1][7]
        # sl = npArr[i][0] * 0.95
        # close = npArr[i][3]
        # if npArr[i][2] < sl: close = sl
        # gain = close / npArr[i][0]
        # lastBalance = balance
        # balance *= gain
        # print(topSymbol, balance, sampleArrJP[i][5])

        perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1]))
        tradeList = []
        count = 0
        for k, v in perfDict.items():
            tradeList.append(k)
            count += 1
            # if count > 1: break
        tradeListLen = len(tradeList)
        if tradeListLen < 1: continue
        vol = balance/tradeListLen
        lastBalance = balance
        balance = 0
        for symbol in tradeList:
            npArr = dataDict[symbol]
            op = npArr[i][0]
            tp = npArr[i][3]
            gain = tp / op * vol
            balance += gain
        # print(tradeList, balance, sampleArrJP[i][5])
        
        if balance < lastBalance:
            ddList.append(balance/lastBalance)
        if balance > maxBalance:
            maxBalance = balance
        elif balance < maxBalance:
            mddList.append(balance/maxBalance)
    ddList.sort()
    # print("Daily Draw Down:", ddList[0])
    mddList.sort()
    # print("MDD:", mddList[0])
    return mddList[0]

length = len(dataDictUS["AAPL"])
dataDict = dataDictUS

sampleArrJP = dataDictUS["AAPL"]
sampleArrJP = sampleArrJP[-length:]

cleanDataDict = {}
sampleArr = dataDict["QQQ"]
# optionList = []
# for symbol, optionLen in optionDict.items():
#     optionList.append(symbol)
cleanDataDict = {}
# 0.8904027034538516
# 1.2427562773020495
# for symbol, npArr in dataDict.items():
#     if symbol != "AAPL": continue
#     # if symbol not in ["AAPL","MSFT","GOOG",
#     # "GOOGL","NVDA","AMZN","TSLA","META"]: continue
#     if len(npArr) < length: continue
#     if symbol == "GOOG": continue
#     # if symbol not in optionList: continue
#     cleanDataDict[symbol] = npArr
symbolList = []
for symbol, optionLen in optionDict.items():
    cleanDataDict = {}
    if symbol not in dataDict: continue
    cleanDataDict[symbol] = dataDict[symbol]
    if len(dataDict[symbol]) < length: continue
    gainnerDict = {}
    mdd = Backtest(cleanDataDict, length, 
        sampleArr, gainnerDict)
    if mdd < 0.8904027034538516: continue
    symbolList.append(symbol)
    print(symbolList)
    print(symbol, mdd)