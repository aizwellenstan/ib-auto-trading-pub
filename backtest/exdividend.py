rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr
from modules.data import GetDf
from modules.businessday import GetBusinessDays
from datetime import datetime
from modules.dividendCalendar import GetExDividendByDate
import pickle
from modules.dividend import GetDividend
import numpy as np
from datetime import datetime, timedelta
from modules.dict import take
from modules.csvDump import LoadDict

optionPath = f"{rootPath}/data/TradableOption.csv"
tradableOption = LoadDict(optionPath, "Length")
tradableOptionList = []
for symbol, length in tradableOption.items():
    if length < 390: continue
    tradableOptionList.append(symbol)
# from modules.dividendCalendar import GetExDividend
# import pandas as pd
# import os


maxBalance = 0
maxBackDate = 0
from numba.typed import Dict
from numba import types, njit, range
tradesPicklePath = "./pickle/pro/compressed/dividendTrades.p"
trades = []
updateTrades = False
if updateTrades:
    dividendCalendarDict = {}
    picklePath = "./pickle/pro/compressed/dividendCalendar.p"
    update = False
    if update:
        startDate = '2020-03-18'
        endDate = datetime.strftime(datetime.now(),'%Y-%m-%d')
        dates = GetBusinessDays(startDate, endDate)
        for date in dates:
            exDivList = GetExDividendByDate(date)
            if len(exDivList) < 1: continue
            dateStr = datetime.strftime(date,'%Y-%m-%d')
            dividendCalendarDict[dateStr] = exDivList
        pickle.dump(dividendCalendarDict, open(picklePath, "wb"))
    else:
        import gc
        output = open(picklePath, "rb")
        # gc.disable()
        dividendCalendarDict = pickle.load(output)
        output.close()
        # gc.enable()

    dataDict = {}
    picklePath = "./pickle/pro/compressed/dataDictDividends.p"
    update = False
    if update:
        closeDict = GetClose()
        for symbol, close in closeDict.items():
            df = GetDf(symbol)
            if len(df) < 1: continue
            df = df.assign(Date=df.index.date.astype(str),format='%Y-%m-%d')
            df = df[['Open','High','Low','Close','Dividends','Date']]
            npArr = df.to_numpy()
            print(symbol)
            dataDict[symbol] = npArr
        pickle.dump(dataDict, open(picklePath, "wb"))
    else:
        import gc
        output = open(picklePath, "rb")
        # gc.disable()
        dataDict = pickle.load(output)
        output.close()
        # gc.enable()
    balance = 2700
    totalDividends = 0
    backDate = 1
    sellBackDict = {}
    for date, exdivList in dividendCalendarDict.items():
        dateTime = datetime.strptime(date,'%Y-%m-%d')
        for sellBackDate, cash in sellBackDict.items():
            sellBackDateTime = datetime.strptime(sellBackDate,'%Y-%m-%d')
            if dateTime > sellBackDateTime + timedelta(days=backDate):
                balance += cash
                newDict = dict(sellBackDict)
                del newDict[sellBackDate]
                sellBackDict = newDict
        # if date!='2023-01-18': continue
        divToPriceDict = {}
        npArrIdxDict = {}
        for symbol in exdivList:
            if symbol not in dataDict: continue
            if symbol not in tradableOptionList: continue
            # if symbol not in marketCapDict: continue
            # marketCap = marketCapDict[symbol]
            # if marketCap < marketCapLimit: continue
            npArr = dataDict[symbol]
            if len(npArr) < 180: continue
            dateFilter = np.array([date])
            res = np.in1d(npArr[:, 5], dateFilter)
            idx = 0
            for j in range(0, len(res)):
                if res[j]:
                    idx = j
            div = npArr[idx][4]
            price = npArr[idx-backDate][3]
            dividendToPrice = div/price
            divToPriceDict[symbol] = dividendToPrice
            npArrIdxDict[symbol] = idx
        divToPriceDict = dict(sorted(divToPriceDict.items(), key=lambda item: item[1], reverse=True))
        if len(divToPriceDict) < 1: continue
        divToPriceList = list(divToPriceDict.keys())
        symbol = divToPriceList[0]
        idx = npArrIdxDict[symbol]
        npArr = dataDict[symbol]
        op = npArr[idx-backDate][0]
        # vol = balance/op
        vol = int(balance/2/op)
        close = npArr[idx][0]
        div = npArr[idx][4]
        balance -= op*vol
        sellBack = close*vol
        sellBackDict[date] = sellBack
        totalDividends += div*vol
        trades.append([
            divToPriceDict[divToPriceList[0]],
            op,
            close,
            div
        ])
    for sellBackDate, cash in sellBackDict.items():
        sellBackDateTime = datetime.strptime(sellBackDate,'%Y-%m-%d')
        balance += cash
    balance += totalDividends
    # print('balance:',balance,'totalDividends',totalDividends)
    
    if balance > maxBalance:
        maxBalance = balance
        maxBackDate = backDate
    # maxMarketCapLimit = marketCapLimit
    print(maxBalance,maxBackDate)
    print(trades)

    
    pickle.dump(trades, open(tradesPicklePath, "wb"))
else:
    import gc
    output = open(tradesPicklePath, "rb")
    # gc.disable()
    trades = pickle.load(output)
    output.close()

from numba import njit

# # @njit
def main():
    balance = 1
    divs = 0
    divToPriceList = np.empty(0)
    for trade in trades:
        divToPriceList = np.append(divToPriceList, trade[0])
    divToPriceList.sort()

    maxBalance = 1
    maxDivToPriceLimit = 0
    for divToPriceLimit in divToPriceList:
        balance = 1
        divs = 0
        for trade in trades:
            if trade[0] < divToPriceLimit: continue
            gain = trade[2] / trade[1]
            vol = 1 / trade[1]
            fee = vol * 2
            div = trade[3] * vol
            divs += div
            # balance -= fee
            balance *= gain
        # balance += divs
        if balance > maxBalance:
            maxBalance = balance
            maxDivToPriceLimit = divToPriceLimit
            print(maxBalance, maxDivToPriceLimit)
main()
    

# totalBalance = 1
# for symbol, close in closeDict.items():
#     df = GetDf(symbol)
#     if len(df) < 1: continue
#     df = df.assign(preExDiv=df.Dividends.shift(-1))
#     df = df[['Open','High','Low','Close','preExDiv']]
#     npArr = df.to_numpy()

#     balance = 1
#     for i in range(0, len(npArr)):
#         div = npArr[i][4]
#         if div > 0:
#             op = npArr[i][3]
#             vol = balance/op
#             close = npArr[i+1][0]
#             balance -= op*vol
#             balance += (close+div)*vol 
#     totalBalance += balance
#     print(totalBalance)