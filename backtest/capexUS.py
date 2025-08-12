rootPath = ".."
import sys
sys.path.append(rootPath)
from modules.loadPickle import LoadPickle
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from modules.dict import take
from modules.gainner import GetGainner
from modules.atr import ATR
import pandas as pd
from modules.dataHandler.bsUS import GetBS
from modules.dataHandler.cfUS import GetCF
from modules.csvDump import LoadDict

dataPath = f"{rootPath}/backtest/pickle/pro/compressed/dataWithVolumeUS.p"
dataDict = LoadPickle(dataPath)

def Backtest(dataDict, length, sampleArr, 
    totalGainnerList):
    trades = []

    for i in range(31, length):
        isShort = False
        topPerf = 0
        topSymbol = ""
        perfDict = {}
        hhCount = 0
        llCount = 0
        today = sampleArr[i][5]
        print(today,i)

        yesterdayStr = sampleArr[i-1][5]
        yesterday = datetime.strptime(yesterdayStr, "%Y-%m-%d")
        for symbol, npArr in dataDict.items():
            if i > 180:
                if symbol not in totalGainnerList[i-1]: continue

            total_assets = GetBS(symbol, 'Total Assets', npArr[i-1][5])
            if total_assets == "": continue
            if float(total_assets) == 0: continue
            capex = GetCF(symbol, 'Capital Expenditures', npArr[i-1][5])
            if capex == "": continue
            if float(capex) == 0: continue
            perfDict[symbol] = float(total_assets) / float(capex)

        perfDict = dict(sorted(perfDict.items(), key=lambda item: item[1]))
        tradeList = []
        categoryList = []
        tradeList = []
        for symbol in list(perfDict.keys()):
            tradeList.append(symbol)
            if len(tradeList) > 1: break
        tradeListLen = len(tradeList)
        currentTime = datetime.strptime(sampleArr[i][5], '%Y-%m-%d')
        currentMonth = currentTime.month
        if tradeListLen < 1 or currentMonth in [9]: 
            trades.append([sampleArr[i][5], "capex", "AAPL", 0])
            continue

        weightDict = {}
        atrDict = {}
        for symbol in tradeList:
            npArr = dataDict[symbol]
            atr = ATR(npArr[:,1][:i],npArr[:,2][:i],npArr[:,3][:i])
            atrDict[symbol] = atr
        atrTotal = sum(atrDict.values())
        weightTotal = 0
        for symbol, atr in atrDict.items():
            weight = atrTotal / atr
            weightTotal += weight

        for symbol, atr in atrDict.items():
            weight = atrTotal / atr / weightTotal
            weightDict[symbol] = weight

        for symbol in tradeList:
            trades.append([sampleArr[i][5], "capex", symbol, weightDict[symbol]])
        print(tradeList, sampleArr[i][5])
    trades = pd.DataFrame(trades, columns=["da", "strategy_name", "code", "weight"])
    trades.set_index("da", inplace=True)
    trades.to_csv("capexUS.csv")

def main(market = 'us'):
    length = len(dataDict["AAPL"])
    sampleArr = dataDict["AAPL"]
    
    df = pd.read_csv(f"{rootPath}/data/ib_cfd_{market}.csv")
    cfd = df['Symbol'].values.tolist()
    cleanDataDict = {}
    totalGainnerList = GetGainner(dataDict, market)

    optionPath = f"{rootPath}/data/tradableOption.csv"
    optionDict = LoadDict(optionPath, "Length")

    shortIntrestPathUS = f"{rootPath}/backtest/pickle/pro/compressed/dataDictShortIntrest.p"
    shortIntrestDict = LoadPickle(shortIntrestPathUS)

    for symbol, npArr in dataDict.items():
        npArr = dataDict[symbol]
        if len(npArr) < length: continue
        if symbol not in cfd: continue
        if symbol not in shortIntrestDict: continue
        cleanDataDict[symbol] = npArr

    Backtest(cleanDataDict, length, sampleArr, 
        totalGainnerList)

main()