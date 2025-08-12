rootPath = '../'
import sys
sys.path.append('../')
import pandas as pd
import numpy as np
import os

from modules.aiztradingview import GetAll
from modules.data import GetNpDataInspection
from modules.dict import take


portfolioPath = "./data/DividendsLongTern.csv"
ignorePath = "./data/Ignore.csv"
noTradePath = "./data/NoTrade.csv"

def DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList):
    if len(dataDict) > 1:
        df = pd.DataFrame()
        df['Symbol'] = dataDict.keys()
        df['Performance'] = dataDict.values()
        df.to_csv(portfolioPath)
    df = pd.DataFrame(ignoreList, columns = ['Symbol'])
    df.to_csv(ignorePath)
    df = pd.DataFrame(noTradeList, columns = ['Symbol'])
    df.to_csv(noTradePath)
    print("dump")

symbolList = GetAll()

dataDict = {}
ignoreList = []
noTradeList = []

if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    df = df[['Symbol', 'Performance']]
    dataDict = df.set_index('Symbol').Performance.to_dict()

if os.path.exists(ignorePath):
    df = pd.read_csv(ignorePath)
    ignoreList = list(df.Symbol.values)

if os.path.exists(noTradePath):
    df = pd.read_csv(noTradePath)
    noTradeList = list(df.Symbol.values)

print(ignoreList)

dump = False
for symbol in ignoreList:
    if "." in symbol:
        if dump:
            DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
            dump = False
        npArr = GetNpDataInspection(symbol)
        if len(npArr) < 1: 
            ignoreList.append(symbol)
            dump = True
            continue
        performance = npArr[-1][3]/npArr[0][0]
        if performance < 1:
            noTradeList.append(symbol)
            dump = True
        else:
            dataDict[symbol] = performance

# dump = False
# for symbol in symbolList:
#     if dump:
#         DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
#         dump = False
#     npArr = GetNpDataInspection(symbol)
#     if len(npArr) < 1: 
#         ignoreList.append(symbol)
#         dump = True
#         continue
#     performance = npArr[-1][3]/npArr[0][0]
#     if performance < 1:
#         noTradeList.append(symbol)
#         dump = True
#     else:
#         dataDict[symbol] = performance

# dataDict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=True))
# print(dataDict)

# if os.path.exists(portfolioPath):
#     df = pd.read_csv(portfolioPath)
#     df = df[['Symbol', 'Performance']]
#     dataDict = df.set_index('Symbol').Performance.to_dict()

# dataDict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=True))
# print(dataDict)