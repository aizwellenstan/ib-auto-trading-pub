rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetCloseDividends
from modules.dividend import GetDividend
from modules.dividendCalendar import GetExDividend, GetExDividendDf
import pandas as pd
import os
from ib_insync import *
ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=16)

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

def CheckIPOPriceM(symbol):
    npArr = GetDataM(symbol)
    if len(npArr) < 1: return True
    if npArr[-1][3] < npArr[0][3]:
        return False
    return True

ignoreList = []
ignorePath = f'{rootPath}/data/IgnoreAllGurosu.csv'
if os.path.exists(ignorePath):
    df = pd.read_csv(ignorePath)
    ignoreList = list(df.Symbol.values)

noTradeList = []
noTradePath = f'{rootPath}/data/NoTradeAllGurosu.csv'
if os.path.exists(noTradePath):
    df = pd.read_csv(noTradePath)
    noTradeList = list(df.Symbol.values)

# https://www.nasdaq.com/market-activity/dividends
symbols = GetExDividend()
print(symbols)
closeDict = GetClose()
closeDividendsDict = GetCloseDividendsDf()
portfolioDict = {}
dividendDict = {}
for symbol in symbols:
    checkDiv = False
    div = GetDividend(symbol)
    if len(div) < 1: continue
    div = div['amount'].values
    div = div[0]
    if symbol not in closeDividendsDict: continue
    # if (
    #     symbol not in closeDividendsDict and
    #     symbol in ignoreList or
    #     symbol in noTradeList or
    #     not CheckIPOPriceM(symbol)
    # ):
    #     # if div < 0.63: continue
    #     if div < 1.45: continue
    close = closeDict[symbol]
    dividendToPrice = div/close
    if dividendToPrice < 0.07: continue
    portfolioDict[symbol] = dividendToPrice
    dividendDict[symbol] = div

portfolioDict = dict(sorted(portfolioDict.items(), key=lambda item: item[1], reverse=True))
print(portfolioDict)
portfolioList = list(portfolioDict.keys())
print(portfolioList)

resDict = {}
for symbol in portfolioList:
    resDict[symbol] = dividendDict[symbol]

exDividendPath = f'{rootPath}/data/ExDividend.csv'
if len(resDict) > 0:
    df = pd.DataFrame()
    df['Symbol'] = resDict.keys()
    df['Divdend'] = resDict.values()
    df.to_csv(exDividendPath)
