rootPath = '..'
import sys
sys.path.append(rootPath)
from modules.aiztradingview import GetClose, GetAttr
from modules.data import GetDf
from modules.businessday import GetBusinessDays
from datetime import datetime
from modules.dividendCalendar import GetExDividendByDate, GetExDividendPaymentByDate
import pickle
from modules.dividend import GetDividend
import numpy as np
from datetime import datetime, timedelta
from modules.dict import take
# from modules.dividendCalendar import GetExDividend
# import pandas as pd
# import os

dividendCalendarDict = {}
picklePath = "./pickle/pro/compressed/dividendCalendarInt.p"
update = False
if update:
    startDate = '2020-03-18'
    endDate = datetime.strftime(datetime.now(),'%Y-%m-%d')
    dates = GetBusinessDays(startDate, endDate)
    for date in dates:
        exDivList = GetExDividendPaymentByDate(date)
        if len(exDivList) < 1: continue
        dateStr = datetime.strftime(date,'%Y-%m-%d')
        explode = dateStr.split('-')
        dateNum = int(explode[0]+explode[1]+explode[2])
        dataList = []
        for i in range(0, len(exDivList)):
            payment_Date = exDivList.iloc[i].payment_Date
            explode = payment_Date.split('/')
            if len(explode) < 3: continue
            paymentNum = int(explode[2]+explode[0]+explode[1])
            dataList.append([exDivList.iloc[i].symbol,paymentNum])
        dividendCalendarDict[dateNum] = dataList
        print(dividendCalendarDict)
    pickle.dump(dividendCalendarDict, open(picklePath, "wb"))
else:
    import gc
    output = open(picklePath, "rb")
    # gc.disable()
    dividendCalendarDict = pickle.load(output)
    output.close()
    # gc.enable()

dataDict = {}
picklePath = "./pickle/pro/compressed/dataDictDividendsSimple.p"
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
    # gc.enable()
    dataDict = pickle.load(output)
    output.close()
    # gc.disable()
    
# newDict = {}
# for symbol, npArr in dataDict.items():
#     dateArr = npArr[:,5]
#     dateNumArr = []
#     for date in dateArr:
#         explode = date.split('-')
#         num = int(explode[0]+explode[1]+explode[2])
#         dateNumArr.append(num)
#     npArr = np.c_[npArr[:,0],npArr[:,3],npArr[:,4],dateNumArr]
#     print(npArr)
#     newDict[symbol] = npArr

# picklePath = "./pickle/pro/compressed/dataDictDividendsSimple.p"
# pickle.dump(newDict, open(picklePath, "wb"))

# import sys
# sys.exit(0)

# exDivList = ['CMC', 'CODI', 'DSL', 'DLY', 'DBL', 'FT', 'MIO', 'PHT', 'MAV',
#        'MHI', 'GIM', 'TEI', 'VCIF']
# dataDict = {}
# for symbol in exDivList:
#     df = GetDf(symbol)
#     if len(df) < 1: continue
#     df = df.assign(Date=df.index.date.astype(str),format='%Y-%m-%d')
#     df = df[['Open','High','Low','Close','Dividends','Date']]
#     npArr = df.to_numpy()
#     print(symbol)
#     dataDict[symbol] = npArr

from numba.typed import Dict
from numba import types
from numba import njit
# newMarCapDict = Dict.empty(key_type=types.unicode_type,value_type=types.uint64)
# # marketCapDict = GetAttr("market_cap_basic")
# marketCapDict = GetAttr("number_of_shareholders")
# for symbol, v in marketCapDict.items():
#     if symbol not in dataDict: continue
#     newMarCapDict[np.unicode_(symbol)] = np.uint64(marketCapDict[symbol])
# marketCapDict = newMarCapDict
# marketCapList = np.uint64(list(marketCapDict.values()))
# marketCapList.sort()
# marketCapList = marketCapList[::-1]

# from modules.csvDump import LoadDict
# divPath = f'{rootPath}/data/DividendToPriceRiron.csv'
# divToPriceDict = LoadDict(divPath, 'DivdendToPrice')
# divToPriceList = np.float32(list(divToPriceDict.values()))
# divToPriceList.sort()
# print(divToPriceList)

# 108349 9d c

# 0.054 1d c 5355
# 0.054 9d c 167092
# 0.054 18d o 209509
# # @njit
# def main(marketCapList):

# newDividendCalendarDict = {}
# for date, exdivList in dividendCalendarDict.items():
#     if date < 20220104: continue
#     if date > 20221003: continue
#     newDividendCalendarDict[date] = exdivList
# dividendCalendarDict = newDividendCalendarDict

# # @njit
def Backtest(dividendCalendarDict, dataDict):
    maxBalance = 0
    maxBackDate = 0
    maxMarketCapLimit = 0
    maxDivToPriceLimit = 0
    for i in range(6, 180):
        divToPriceLimit = 0.001
        while divToPriceLimit < 0.15:
            balance = 2700
            totalDividends = 0
            backDate = i
            sellBackDict = {}
            dividendDict = {}
            for date, exdivList in dividendCalendarDict.items():
                for sellBackDate, cash in sellBackDict.items():
                    sellBackDateTime = datetime.strptime(str(sellBackDate),'%Y%m%d')
                    dateTime = datetime.strptime(str(date),'%Y%m%d')
                    if dateTime > sellBackDateTime + timedelta(days=backDate):
                        balance += cash
                        newDict = dict(sellBackDict)
                        del newDict[sellBackDate]
                        sellBackDict = newDict
                for paymentDate, cash in dividendDict.items():
                    if date == paymentDate:
                        balance += cash
                        newDict = dict(dividendDict)
                        del newDict[paymentDate]
                        dividendDict = newDict
                divToPriceDict = {}
                npArrIdxDict = {}
                for symbol, paymentDate in exdivList:
                    if paymentDate > 20230124: continue
                    if symbol not in dataDict: continue
                    npArr = dataDict[symbol]
                    if len(npArr) < 180: continue
                    dateFilter = np.array([date])
                    res = np.in1d(npArr[:, 3], dateFilter)
                    idx = 0
                    for j in range(0, len(res)):
                        if res[j]:
                            idx = j
                            break
                    div = npArr[idx][2]
                    price = npArr[idx-backDate][1]
                    dividendToPrice = div/price
                    if dividendToPrice < divToPriceLimit: continue
                    divToPriceDict[symbol] = dividendToPrice
                    npArrIdxDict[symbol] = idx
                if len(divToPriceDict) < 1: continue
                divToPriceDict = dict(sorted(divToPriceDict.items(), key=lambda item: item[1], reverse=True))
                divToPriceList = list(divToPriceDict.keys())
                symbol = divToPriceList[0]
                idx = npArrIdxDict[symbol]
                npArr = dataDict[symbol]
                op = npArr[idx-backDate][0]
                # vol = balance/op
                vol = int(balance/op)
                close = npArr[idx][0]
                div = npArr[idx][2]
                balance -= op*vol
                sellBack = close*vol
                sellBackDict[date] = sellBack
                if date in dividendDict:
                    dividendDict[date] += div*vol
                else:
                    dividendDict[date] = div*vol
                # totalDividends += div*vol
            for sellBackDate, cash in sellBackDict.items():
                balance += cash
            # balance += totalDividends
            # print('balance:',balance,'totalDividends',totalDividends)

            if balance > maxBalance:
                maxBalance = balance
                maxBackDate = backDate
                # maxMarketCapLimit = marketCapLimit
                maxDivToPriceLimit = divToPriceLimit
                print(maxBalance,maxBackDate,maxDivToPriceLimit)
            divToPriceLimit += 0.001

if __name__ == '__main__':
    Backtest(dividendCalendarDict,dataDict)