rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetCloseJP, GetClose
import yfinance as yf

import pandas as pd
from modules.dict import take
from modules.data import GetNpData
import os
from modules.portfolio import GetSharpeSortino
from modules.data import GetNpData
from datetime import datetime
from modules.dividend import GetDividend
from modules.rironkabukaDividends import GetExpectGain

from ib_insync import *
ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=3)

def GetData(symbol, currency):
    try:
        if currency != 'JPY':
            stockInfo = yf.Ticker(symbol)
        else:
            stockInfo = yf.Ticker(symbol+'.T')
        data = stockInfo.history(period="max")
        return data
    except: return []

def GetDataM(symbol):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        data = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='60 Y',
            barSizeSetting='1M', whatToShow='ASK', useRTH=False)
        df = pd.DataFrame(data)
        df = df[['open','high','low','close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def CheckIPOPrice(symbol, currency):
    df = GetData(symbol, currency)
    if len(df) < 1: return False
    print( df.iloc[-1].Close , df.iloc[0].Open)
    if df.iloc[-1].Close < df.iloc[0].Open:
        return False
    return True

def CheckIPOPriceM(symbol):
    npArr = GetDataM(symbol)
    if len(npArr) < 1: return True
    if npArr[-1][3] < npArr[0][3]:
        return False
    return True

portfolioPath = f'{rootPath}/data/ExceptGainToPrice.csv'
ignorePath = f'{rootPath}/data/IgnoreAllGurosu.csv'
noTradePath = f'{rootPath}/data/NoTradeAllGurosu.csv'
resPath = f'{rootPath}/data/PortfolioAllGurosu.csv'

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

def DumpResCsv(resPath, resList):
    df = pd.DataFrame(resList, columns = ['Symbol'])
    df.to_csv(resPath)

def CheckSharpeSortino(npArr):
    if npArr[0][3] < 0.01: return False
    # if npArr[0][0] < 0.50: return False
    return True

dividendDict = {}
ignoreList = []
noTradeList = []

def GetDividendData(df, currency):
    dividend = 0
    try:
        df = df.loc[df['Dividends'] > 0]
    except: return 0
    df = df.assign(date=df.index.date)
    df = df.assign(previousDate=df.date.shift(1))
    df = df.assign(duration = df.index.date-df.previousDate)
    dividendKey = "Dividends"
    if len(df) < 3: return 0
    maxDur = df.duration.max().days
    if maxDur > 366: return 0
    avg = df[dividendKey].quantile(0.99)
    df = df[(df.index.date>datetime.strptime('2021-03-18','%Y-%m-%d').date())]
    dfLenBefore = len(df)
    df = df[df[dividendKey] < avg * 1.0593220338983054]
    dividend = df[dividendKey].values
    dividend = sum(dividend)
    dfLenAfter = len(df[dividendKey])
    if dfLenAfter > 0:
        avgDividend = dividend/dfLenAfter
        dividend += (dfLenBefore-dfLenAfter)*avgDividend
    
    return dividend

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

closeDictJP = GetCloseJP()

dataDict = {}
dump = False
# currency = 'JPY'
# for symbol, v in closeDictJP.items():
#     if dump:
#         DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
#         dump = False
#     if symbol in ignoreList: continue
#     if symbol in noTradeList: continue
#     df = GetData(symbol, currency)
#     if len(df) < 1:
#         ignoreList.append(symbol)
#         continue
#     dividend = GetDividendData(df, currency)
#     if dividend < 3: continue
#     close = closeDictJP[symbol]
#     dividendToPrice = dividend/close
#     if not CheckIPOPrice(symbol, currency):
#         noTradeList.append(symbol)
#         dump = True
#         continue
#     dataDict[symbol] = dividendToPrice
#     dump = True

closeDict = GetClose()
benchmark = 'BRK.A'
currency = 'USD'
for symbol, v in closeDict.items():
    if dump:
        DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
        dump = False
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    npArr = GetSharpeSortino(benchmark, symbol)
    if len(npArr) < 2: 
        ignoreList.append(symbol)
        dump = True
        continue
    if (
        not CheckSharpeSortino(npArr) 
        or not CheckIPOPriceM(symbol)
    ):
        noTradeList.append(symbol)
        dump = True
        continue
    gain = GetExpectGain(symbol)
    if gain <= 0:
        noTradeList.append(symbol)
        dump = True
        continue
    # df = GetData(symbol, currency)
    # dividend = GetDividendData(df, currency)
    # if dividend < 3: continue
    close = closeDict[symbol]
    print(gain)
    dataDict[symbol] = gain
    dump = True

dataDict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=True))
newDataDict = {}
ignoreList = []
for k, v in dataDict.items():
    if k in ignoreList:
        continue
    newDataDict[k] = v
dividendList = take(len(newDataDict),newDataDict)
DumpResCsv(resPath, dividendList)