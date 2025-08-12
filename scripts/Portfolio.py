import sys
sys.path.append('.')

from modules.portfolio import GetSharpeSortino
from modules.aiztradingview import GetDividends, GetAll
import pandas as pd
import os
import numpy as np

portfolioPath = "./data/Portfolio.csv"
ignorePath = "./data/Ignore.csv"
noTradePath = "./data/NoTrade.csv"
noTradeLtsPath = "./data/NoTradeLts.csv"

def CheckSharpeSortino(npArr):
    if npArr[0][0] < 0.01 or npArr[0][1] < 0.01: return False
    if npArr[0][0] >= npArr[1][0]:
        # if npArr[0][3] >= npArr[1][3]:
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

divs = GetDividends()

sharpeDict = {}
sortinoDict = {}
count = 0
dataDict = {}
# ignoreList = []
# noTradeList = []
# benchmarkList = ['AAPL','MSFT','GOOG','AMZN','TSLA','UNH','V','MA','COST','BRK.A','SPY']
benchmarkList = ['SPY']
dump = False
for symbol in divs:
    if dump:
        DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
        dump = False
    if symbol in noTradeLtsList: continue
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