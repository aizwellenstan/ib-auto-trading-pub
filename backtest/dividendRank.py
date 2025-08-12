rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.dividend import GetDividend
import pandas as pd
from modules.aiztradingview import GetClose
from modules.dict import take
from modules.data import GetNpData
import os
from modules.portfolio import GetSharpeSortino
# from scipy import stats
# import numpy as np

portfolioPath = f'{rootPath}/data/DividendToPrice.csv'
ignorePath = f'{rootPath}/data/Ignore.csv'
noTradePath = f'{rootPath}/data/NoTrade.csv'

def DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList):
    if len(dataDict) > 1:
        df = pd.DataFrame()
        df['Symbol'] = dataDict.keys()
        df['DivdendToPrice'] = dataDict.values()
        df.to_csv(portfolioPath)
    df = pd.DataFrame(ignoreList, columns = ['Symbol'])
    df.to_csv(ignorePath)
    df = pd.DataFrame(noTradeList, columns = ['Symbol'])
    df.to_csv(noTradePath)

def CheckSharpeSortino(npArr):
    if npArr[0][3] < 0.01: return False
    if npArr[0][2] < -15.17: return False
    return True

dividendDict = {}
ignoreList = []
noTradeList = []

def GetDividendData(symbol):
    global ignoreList
    csvPath = f'{rootPath}/backtest/csv/dividend/{symbol}.csv'
    dividend = 0
    if os.path.exists(csvPath):
        df = pd.read_csv(csvPath)
        df = df[(df['paymentDate']>'2021-03-18')]
        # df = df.loc[df['type'] == "CASH"]
        # df = df[(np.abs(stats.zscore(df['amount'])) < 3)]
        # avg = df["amount"].quantile(0.99)
        # df = df[df["amount"] < avg]
        dividend = df.amount.values
        dividend = sum(dividend)
    else:
        df = GetDividend(symbol)
        if len(df) < 1: 
            ignoreList.append(symbol)
            return 0
        df = df[(df['paymentDate']>'2021-03-18')]
        df = df.loc[df['type'] == "CASH"]
        # df[(np.abs(stats.zscore(df['amount'])) < 3)]
        # avg = df["amount"].quantile(0.99)
        # df = df[df["amount"] < avg]
        dividend = df.amount.values
        dividend = sum(dividend)
    return dividend

# benchmark = 'BRK.A'
# symbol = 'TEI'
# npArr = GetSharpeSortino(benchmark, symbol)
# print(npArr)

# import sys
# sys.exit(0)
        
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    df = df[['Symbol', 'DivdendToPrice']]
    dividendDict = df.set_index('Symbol').DivdendToPrice.to_dict()

if os.path.exists(ignorePath):
    df = pd.read_csv(ignorePath)
    ignoreList = list(df.Symbol.values)

if os.path.exists(noTradePath):
    df = pd.read_csv(noTradePath)
    noTradeList = list(df.Symbol.values)

# print(dividendDict)
# print(ignoreList)
# print(noTradeList)

closeDict = GetClose()

benchmark = 'BRK.A'
dataDict = {}
dump = False
for symbol, v in dividendDict.items():
    if dump:
        # DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
        dump = False
    # if symbol in ignoreList: continue
    # if symbol in noTradeList: continue
    dividend = GetDividendData(symbol)
    close = closeDict[symbol]
    dividendToPrice = dividend/close
    # npArr = GetSharpeSortino(benchmark, symbol)
    # if len(npArr) < 2: 
    #     ignoreList.append(symbol)
    #     dump = True
    #     continue
    # if not CheckSharpeSortino(npArr):
    # #     noTradeList.append(symbol)
    # #     dump = True
    #     continue
    # print(symbol,v,npArr[0][3])
    dataDict[symbol] = dividendToPrice
    dump = True

dataDict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=True))
# print(take(500,dataDict))
print(dataDict)

dividend = GetDividendData('XOMAP')
print(dividend)

paidDividendDict = {}
total = 0
for symbol in dataDict:
    dividend = GetDividendData(symbol)
    paidDividendDict[symbol] = dividend

    if symbol == "GECCN": break
print(paidDividendDict)

import sys
sys.exit(0)

dividendDict = {}
ignoreList = []
dump = False
for symbol, close in closeDict.items():
    if dump:
        # DumpCsv(portfolioPath, ignorePath, dividendDict, ignoreList)
        dump = False
    df = GetDividend(symbol)
    if len(df) < 1: 
        ignoreList.append(symbol)
        dump = True
        continue
    df.to_csv(f'{rootPath}/backtest/csv/dividend/{symbol}.csv')
    df = df[(df['paymentDate']>'2021-03-18')]
    dividend = df.amount.values
    dividend = sum(dividend)
    dividendToPrice = dividend/close
    dividendDict[symbol] = dividendToPrice
    print(symbol,dividendToPrice)
    dump = True

dividendDict = dict(sorted(dividendDict.items(), key=lambda item: item[1], reverse=True))
print(take(100,dividendDict))