import sys
rootPath = "../../"
sys.path.append(rootPath)

from modules.portfolio import GetSharpeSortino, GetComb
from modules.aiztradingview import GetDividends
import pandas as pd
import os
import numpy as np

portfolioPath = f"{rootPath}/data/Portfolio50.csv"
ignorePath = f"{rootPath}/data/Ignore.csv"
noTradePath = f"{rootPath}/data/NoTrade.csv"

def CheckSharpeSortino(npArr):
    if npArr[0][0] < 0.01 or npArr[0][1] < 0.01: return False
    if npArr[0][0] > npArr[1][0] or npArr[0][1] > npArr[1][1]:
        return True
    return False

def DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList):
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
    
dataDict = {}
ignoreList = []
noTradeList = []
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

divs = GetDividends()

sharpeDict = {}
sortinoDict = {}
count = 0
base = "GPCO"
for symbol in divs:
    count += 1
    if count > 40:
        if len(dataDict) > 1:
            DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
            count = 0
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    # if symbol in dataDict:
    #     sharpeDict[symbol] = dataDict[symbol][0]
    #     sortinoDict[symbol] = dataDict[symbol][1]
    #     print(symbol)
    # else:
    npArr = GetComb(base,symbol)
    if len(npArr) < 2: 
        ignoreList.append(symbol)
        continue
    if CheckSharpeSortino(npArr):
        sharpeDict[symbol] = npArr[0][0]
        sortinoDict[symbol] = npArr[0][1]
        dataDict[symbol] = [npArr[0][0],npArr[0][1]]
        print(symbol)
    else:
        noTradeList.append(symbol)
        continue

DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)

sharpeDict = dict(sorted(sharpeDict.items(), key=lambda item: item[1], reverse=True))
sortinoDict = dict(sorted(sortinoDict.items(), key=lambda item: item[1], reverse=True))

print(sharpeDict)
print(sortinoDict)