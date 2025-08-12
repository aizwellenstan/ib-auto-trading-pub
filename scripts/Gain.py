import sys
sys.path.append('.')

from modules.portfolio import GetSharpeSortino
from modules.aiztradingview import GetDividends, GetAll
import pandas as pd
import os
import numpy as np
from modules.data import GetNpData

portfolioPath = "./data/Gain.csv"
ignorePath = "./data/Ignore.csv"
noTradePath = "./data/NoTrade.csv"
noTradeLtsPath = "./data/NoTradeLts.csv"

def CheckSharpeSortino(npArr):
    if npArr[0][0] < 0.01 or npArr[0][1] < 0.01: return False
    if npArr[0][0] >= npArr[1][0]:
        if npArr[0][3] >= npArr[1][3]:
            return True
    return False

def DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList):
    if len(dataDict) > 1:
        df = pd.DataFrame()
        df['Symbol'] = dataDict.keys()
        v = np.array(list(dataDict.values()))
        df['Sharpe'] = v[:, 0]
        df['Sortino'] = v[:, 1]
        df.to_csv(portfolioPath)
    df = pd.DataFrame(ignoreList, columns = ['Symbol'])
    df.to_csv(ignorePath)
    df = pd.DataFrame(noTradeList, columns = ['Symbol'])
    df.to_csv(noTradePath)
    print("dump")

dataDict = {}
ignoreList = []
noTradeList = []
noTradeLtsList = []
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    df = df[['Symbol', 'Sharpe', 'Sortino']]
    dataDict = df.set_index('Symbol').T.to_dict('list')

if os.path.exists(ignorePath):
    df = pd.read_csv(ignorePath)
    ignoreList = list(df.Symbol.values)

if os.path.exists(noTradePath):
    df = pd.read_csv(noTradePath)
    noTradeList = list(df.Symbol.values)

if os.path.exists(noTradeLtsPath):
    df = pd.read_csv(noTradeLtsPath)
    noTradeLtsList = list(df.Symbol.values)

divs = GetAll()

sharpeDict = {}
sortinoDict = {}
count = 0
dataDict = {}
ignoreList = []
noTradeList = []
# benchmarkList = ['AAPL','MSFT','GOOG','AMZN','TSLA','UNH','V','MA','COST','BRK.A','SPY']
benchmarkList = ['AMZN','BRK.A','SPY']
gainDict = {}
dump = False
for symbol in divs:
    if dump:
        DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
        dump = False
    if symbol in noTradeLtsList: 
        if symbol not in noTradeList:
            noTradeList.append(symbol)
        continue
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    print(symbol)
    if symbol in dataDict:
        sharpeDict[symbol] = dataDict[symbol][0]
        sortinoDict[symbol] = dataDict[symbol][1]
    else:
        npArr = []
        for benchmark in benchmarkList:
            if symbol in ignoreList: continue
            if symbol in noTradeList: continue
            npArr = GetSharpeSortino(benchmark, symbol)
            if len(npArr) < 2: 
                ignoreList.append(symbol)
                dump = True
                npArr = []
                continue
            if not CheckSharpeSortino(npArr):
                noTradeList.append(symbol)
                dump = True
                npArr = []
                continue
        npData = GetNpData(symbol)
        if len(npData) < 1: continue
        gain = npData[-1][3] / npData[0][0]
        gainSpeed = gain/len(npData)
        if gainSpeed < 0.1462602936447545:
            noTradeList.append(symbol)
            dump = True
            npArr = []
            continue
        gainDict[symbol] = gainSpeed

    if len(npArr) > 1:
        sharpeDict[symbol] = npArr[0][0]
        sortinoDict[symbol] = npArr[0][1]
        dataDict[symbol] = [npArr[0][0],npArr[0][1]]
        print(symbol)
            

DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)

sharpeDict = dict(sorted(sharpeDict.items(), key=lambda item: item[1], reverse=True))
sortinoDict = dict(sorted(sortinoDict.items(), key=lambda item: item[1], reverse=True))

print(sharpeDict)
print(sortinoDict)

gainDict = dict(sorted(gainDict.items(), key=lambda item: item[1], reverse=True))
gainList = []
for k, v in gainDict.items():
    gainList.append(k)
print(gainList)