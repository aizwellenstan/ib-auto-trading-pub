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
from modules.data import GetNpData

from ib_insync import *
ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=12)

def GetData(symbol):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        data = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='60 Y',
            barSizeSetting='1M', whatToShow='ASK', useRTH=False)
        df = pd.DataFrame(data)
        df = df[['open','high','low','close']]
        npArr = df.to_numpy()
        
        return npArr
    except:
        return []

def CheckIPOPrice(symbol):
    npArr = GetData(symbol)
    if len(npArr) < 1: return True
    if npArr[-1][3] < npArr[0][3]:
        return False
    return True

portfolioPath = f'{rootPath}/data/DividendToPrice.csv'
ignorePath = f'{rootPath}/data/Ignore.csv'
noTradePath = f'{rootPath}/data/NoTrade.csv'
resPath = f'{rootPath}/data/Portfolio.csv'

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
    if npArr[0][0] < 0.50: return False
    # if npArr[0][0] < npArr[1][0]: return False
    # if npArr[0][2] < -15.17: return False
    return True

def CheckPerformance(symbol):
    npArr = GetNpData(symbol)
    checkIdx = 7327
    if len(npArr) < checkIdx: checkIdx = len(npArr)
    for i in range(0, checkIdx):
        if npArr[-1][3]/npArr[i][0] < 1:
            return False
    return True

dividendDict = {}
ignoreList = []
noTradeList = []

def GetDividendData(symbol, update=False):
    global ignoreList
    csvPath = f'{rootPath}/backtest/csv/dividend/{symbol}.csv'
    dividend = 0
    df = pd.DataFrame()
    if os.path.exists(csvPath) and not update:
        df = pd.read_csv(csvPath)
        avg = df["amount"].quantile(0.99)
    else:
        df = GetDividend(symbol)
        if len(df) < 1: 
            # ignoreList.append(symbol)
            return 0
    if len(df) < 3: return 0
    df = df.assign(previousDate=df.paymentDate.shift(-1))
    df = df.assign(duration = pd.to_datetime(df.paymentDate)-pd.to_datetime(df.previousDate))
    maxDur = df.duration.max().days
    if maxDur > 366: return 0
    avg = df["amount"].quantile(0.99)
    df = df[(df['paymentDate']>'2021-03-18')]
    dfLenBefore = len(df)
    df = df[df["amount"] < avg * 1.0593220338983054]
    dividend = df.amount.values
    dividend = sum(dividend)
    dfLenAfter = len(df['amount'])
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

closeDict = GetClose()

benchmark = 'BRK.A'
dataDict = {}
dump = False
for symbol, v in closeDict.items():
    if dump:
        DumpCsv(portfolioPath, ignorePath, noTradePath, dataDict, ignoreList, noTradeList)
        dump = False
    if symbol in ignoreList: continue
    if symbol in noTradeList: continue
    dividend = GetDividendData(symbol, True)
    if dividend < 3: continue
    close = closeDict[symbol]
    dividendToPrice = dividend/close
    npArr = GetSharpeSortino(benchmark, symbol)
    if len(npArr) < 2: 
        ignoreList.append(symbol)
        dump = True
        continue
    if not CheckSharpeSortino(npArr) or not CheckIPOPrice(symbol):
    # if not CheckIPOPrice(symbol):
        # noTradeList.append(symbol)
        dump = True
        continue
    # if not CheckPerformance(symbol): continue
    dataDict[symbol] = dividendToPrice
    dump = True
    break

dataDict = dict(sorted(dataDict.items(), key=lambda item: item[1], reverse=True))
newDataDict = {}
ignoreList = ['CHRD','BGS']
for k, v in dataDict.items():
    if k in ignoreList:
        continue
    newDataDict[k] = v
dividendList = take(len(newDataDict),newDataDict)
print(dividendList[0:200])
# DumpResCsv(resPath, dividendList[0:200])