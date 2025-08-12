from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from datetime import datetime as dt, timedelta
import json
import pickle
import pandas_datareader.data as web
import numpy as np
from scipy.signal import lfilter
import gc
from aizfinviz import get_insider

ib = IB()

# # IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
# ib.connect('127.0.0.1', 7497, clientId=10)

# cashDf = pd.DataFrame(ib.accountValues())
# # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
# #    print(cashDf)
# # cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
# cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
# cashDf = cashDf.loc[cashDf['currency'] == 'USD']
# cash = float(cashDf['value'])
# print(cash)

# day = ib.reqCurrentTime().day
# # 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
# risk = 0.06#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837

def sma(x, period):
    y = lfilter(np.ones(period), 1, x)/period
    return y[-1]

def ema(x, period):
    dataArr = np.array([sum(x[0: period]) / period] + x[period:])
    alpha = 2/(period + 1.)
    wtArr = (1 - alpha)**np.arange(len(dataArr))
    xArr = (dataArr[1:] * alpha * wtArr[-2::-1]).cumsum() / wtArr[-2::-1]
    emaArr = dataArr[0] * wtArr +np.hstack((0, xArr))
    y = np.hstack((np.empty(period - 1) * np.nan, emaArr)).tolist()
    return y[-1]

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

def countSlopingCrosses(hisBars, fromBar :int, toBar :int, brk :int, rng :float, pk :bool, body: bool):
    t :int = 0
    x :int = 0
    lastCross :int = 0
    flag :bool = False
    slope :float = 0
    val :float = 0
    try:
        if(pk):
            slope = ((hisBarsD1[fromBar].high - hisBarsD1[toBar].high)/(fromBar - toBar))
        else:
            slope = ((hisBarsD1[fromBar].low - hisBarsD1[toBar].low)/(fromBar - toBar))
        i = fromBar
        while(i>0):
            flag = True
            if(pk):
                val = (slope * (i - fromBar)) + hisBarsD1[fromBar].high 
                if(hisBarsD1[i].high + rng >= val):
                    t += 1
                if(body and hisBarsD1[i].open > val):
                    flag = False
                    x += 1
                if(flag and hisBarsD1[i].close > val):
                    x += 1
            else:
                val = (slope * (i - fromBar)) + hisBarsD1[fromBar].low
                if(hisBarsD1[i].low - rng <= val):
                    t += 1
                if(body and hisBarsD1[i].open < val):
                    flag = False
                    x += 1
                if(flag and hisBarsD1[i].close < val):
                    x += 1
                if(x > brk and brk > 0):
                    lastCross = i
                    break
            i -= 1
        return(str(t) + "," + str(lastCross))
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return ""

def plotLines(hisBars, brk :int = 2, body :bool = False, tch :int = 4, level :int = 3, lineLife :int = 4):
    slopeUpper :float = 0
    slopeLower :float = 0
    pkArr :int = [1]
    trArr :int = [1]
    pk0A :int = 0
    pk0B :int = 0
    pk0C :int = 0
    pk1A :int = 0
    pk1B :int = 0
    pk1C :int = 0
    p :int = 0
    tr0A :int = 0
    tr0B :int = 0
    tr0C :int = 0
    tr1A :int = 0
    tr1B :int = 0
    tr1C :int = 0
    t :int = 0 
    slope :float
    i = 1
    hisBarsLen :int = len(hisBars)
    try:
        if(hisBarsLen > 90):
            while(i < hisBarsLen-30):
                if(hisBarsD1[i+1].high > hisBarsD1[i].high and hisBarsD1[i+1].high >= hisBarsD1[i+2].high):
                    pk0C = pk0B
                    pk0B = pk0A
                    pk0A = i+1
                    if (level < 1):
                        pkArr[p] = i+1
                        p+=1
                    elif (pk0C > 0 and hisBarsD1[pk0B].high > hisBarsD1[pk0A].high 
                            and hisBarsD1[pk0B].high >= hisBarsD1[pk0C].high):
                        pk1C = pk1B
                        pk1B = pk1A
                        pk1A = pk0B
                        if ( level < 2 ):
                            pkArr[p] = pk0B
                            p+=1;      
                        elif (pk1C > 0 and hisBarsD1[pk1B].high > hisBarsD1[pk1A].high 
                                and hisBarsD1[pk1B].high >= hisBarsD1[pk1C].high):
                            pkArr.append(0)
                            pkArr[p] = pk1B
                            p+=1

                if (hisBarsD1[i+1].low < hisBarsD1[i].low 
                        and hisBarsD1[i+1].low <= hisBarsD1[i+2].low):
                    tr0C = tr0B
                    tr0B = tr0A
                    tr0A = i+1
                    if (level < 1):
                        trArr[t] = i+1
                        t+=1
                    elif (tr0C > 1 and hisBarsD1[tr0B].low < hisBarsD1[tr0A].low 
                            and hisBarsD1[tr0B].low <= hisBarsD1[tr0C].low):
                        tr1C = tr1B
                        tr1B = tr1A
                        tr1A = tr0B
                        if ( level < 2 ):
                            trArr[t] = tr0B
                            t += 1
                        elif (tr1C > 0 and hisBarsD1[tr1B].low < hisBarsD1[tr1A].low 
                                and hisBarsD1[tr1B].low <= hisBarsD1[tr1C].low):
                            trArr.append(0)
                            trArr[t] = tr1B
                            t += 1
                i += 1
        u :str
        x :int 
        a :int 
        j :int
        a = len(pkArr)
        if (a > 1):
            pkArr.sort(reverse = True)
            i = 0
            while(i < a):
                j = i + 1
                while(j < a):
                    u = countSlopingCrosses(hisBars, pkArr[i], pkArr[j], brk, 0, True, body)
                    t = int([x.strip() for x in u.split(',')][0])
                    x = int([x.strip() for x in u.split(',')][1])
                    if ( t > tch and x <= lineLife ):
                        slope = (hisBarsD1[pkArr[i]].high - hisBarsD1[pkArr[j]].high) / (pkArr[i] - pkArr[j])
                        slopeUpper = slope
                    j += 1
                i += 1
    
        if (len(trArr) > 1):
            trArr.sort(reverse = True)
            a = len(trArr)
            i = 0
            while(i < a):
                j = i + 1
                while(j < a):
                    u = countSlopingCrosses(hisBars, trArr[i], trArr[j], brk, 0, False, body)
                    t = int([x.strip() for x in u.split(',')][0])
                    x = int([x.strip() for x in u.split(',')][1])
                    if( t > tch and x <= lineLife ):
                        slope = (hisBarsD1[trArr[i]].low - hisBarsD1[trArr[j]].low) / (trArr[i] - trArr[j])
                        slopeLower = slope
                    j += 1
                i += 1
    
        if(slopeUpper > 0 or slopeLower > 0): 
            # print("slopeUpper "+str(slopeUpper))
            # print("slopeLower "+str(slopeLower))
            return 1
        if(slopeUpper < 0 or slopeLower < 0): return -1
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

df = pd.read_csv (r'./csv/trades.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))

fillterDf = pd.read_csv (r'./csv/symbolLst.csv', index_col=0)
fillterDf.drop
fillterSymLst = json.loads(fillterDf.to_json(orient = 'records'))
# sectorLst = fillterDf.groupby('sector')['symbol'].apply(list)

try:
    hisBarsQQQD1arr = [] 
    hisBarsStocksD1arr = []

    saveQQQD1 = False
    if(saveQQQD1):
        contractQQQ = Stock("QQQ", 'SMART', 'USD')
        hisBarsQQQD1 = ib.reqHistoricalData(
            contractQQQ, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        while(len(hisBarsQQQD1)<6):
            print("timeout")
            hisBarsQQQD1 = ib.reqHistoricalData(
                contractQQQ, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        hisBarsQQQD1arr = hisBarsQQQD1
        pickle.dump(hisBarsQQQD1arr, open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "wb"), protocol=-1)
        print("pickle dump finished")
    else:
        output = open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "rb")
        gc.disable()
        hisBarsQQQD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsQQQD1arr finished")

    # hisBarsQQQM30arr = []
    # saveQQQM30 = False
    # if(saveQQQM30):
    #     contractQQQ = Stock("QQQ", 'SMART', 'USD')
    #     hisBarsQQQM30 = ib.reqHistoricalData(
    #         contractQQQ, endDateTime='', durationStr='90 D',
    #         barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

    #     while(len(hisBarsQQQM30)<6):
    #         print("timeout")
    #         hisBarsQQQM30 = ib.reqHistoricalData(
    #             contractQQQ, endDateTime='', durationStr='90 D',
    #             barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

    #     hisBarsQQQM30arr = hisBarsQQQM30
    #     pickle.dump(hisBarsQQQM30arr, open("./pickle/pro/compressed/hisBarsQQQM30arr.p", "wb"), protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsQQQM30arr.p", "rb")
    #     gc.disable()
    #     hisBarsQQQM30arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsQQQM30arr finished")

    # saveQQQM5 = False
    # if(saveQQQM5):
    #     contractQQQ = Stock("QQQ", 'SMART', 'USD')
    #     hisBarsQQQM5 = ib.reqHistoricalData(
    #         contractQQQ, endDateTime='', durationStr='90 D',
    #         barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

    #     while(len(hisBarsQQQM5)<6):
    #         print("timeout")
    #         hisBarsQQQM5 = ib.reqHistoricalData(
    #             contractQQQ, endDateTime=backtestTime, durationStr='90 D',
    #             barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

    #     hisBarsQQQM5arr = hisBarsQQQM5
    #     pickle.dump(hisBarsQQQM5arr, open("./pickle/pro/compressed/hisBarsQQQM5arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsQQQM5arr.p", "rb")
    #     gc.disable()
    #     hisBarsQQQM5arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsQQQM5arr finished")

    # hisBarsStocksMN1arr = []
    # saveStocksMN1arr = False
    # if(saveStocksMN1arr):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsMN1 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='365 D',
    #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    #         maxTrys = 0
    #         while(len(hisBarsMN1)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsMN1 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='12 M',
    #                 barSizeSetting='1M', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
            
    #         hisBarsStocksMN1arr.append({symbol: hisBarsMN1})

    #     pickle.dump(hisBarsStocksMN1arr, open("./pickle/pro/compressed/hisBarsStocksMN1arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksMN1arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksMN1arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksMN1arr finished")

    # hisBarsStocksW1arr = []
    # saveStocksW1arr = False
    # if(saveStocksW1arr):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsW1 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='365 D',
    #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    #         maxTrys = 0
    #         while(len(hisBarsW1)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsW1 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='52 W',
    #                 barSizeSetting='1W', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
            
    #         hisBarsStocksW1arr.append({symbol: hisBarsW1})

    #     pickle.dump(hisBarsStocksW1arr, open("./pickle/pro/compressed/hisBarsStocksW1arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksW1arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksW1arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksW1arr finished")

    saveStocksD1arr = False
    if(saveStocksD1arr):
        for trade in trades:
            symbol = trade['symbol']
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            maxTrys = 0
            while(len(hisBarsD1)<6 and maxTrys<=20):
                print("timeout")
                hisBarsD1 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='365 D',
                    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                maxTrys += 1
            
            hisBarsStocksD1arr.append({symbol: hisBarsD1})

        pickle.dump(hisBarsStocksD1arr, open("./pickle/pro/compressed/hisBarsStocksD1arr.p", "wb"),protocol=-1)
        print("pickle dump finished")
    else:
        output = open("./pickle/pro/compressed/hisBarsStocksD1arr.p", "rb")
        gc.disable()
        hisBarsStocksD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksD1arr finished")

    # hisBarsStocksH1arr = []
    # saveStocksH1arr = True
    # if(saveStocksH1arr):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsH1 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='365 D',
    #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    #         maxTrys = 0
    #         while(len(hisBarsH1)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsH1 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='365 D',
    #                 barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
            
    #         hisBarsStocksH1arr.append({symbol: hisBarsH1})

    #     pickle.dump(hisBarsStocksH1arr, open("./pickle/pro/compressed/hisBarsStocksH1arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksH1arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksH1arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksH1arr finished")

    hisBarsStocksM30arr = []
    saveStocksM30arr = False
    if(saveStocksM30arr):
        for symbol in symbolLst:
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM30 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='90 D',
                barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

            maxTrys = 0
            while(len(hisBarsM30)<6 and maxTrys<=20):
                print("timeout")
                hisBarsM30 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='90 D',
                    barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)
                maxTrys += 1
            
            hisBarsStocksM30arr.append(
                {
                    'symbol': symbol,
                    'data': hisBarsM30
                }
            )

        pickle.dump(hisBarsStocksM30arr, open("./pickle/pro/compressed/hisBarsStocksM30arr.p", "wb"),protocol=-1)
        print("pickle dump finished")
    else:
        output = open("./pickle/pro/compressed/hisBarsStocksM30arr.p", "rb")
        gc.disable()
        hisBarsStocksM30arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksM30arr finished")

    # hisBarsStocksM15arr = []
    # saveStocksM15arr = True
    # if(saveStocksM15arr):
    #     for symbol in fillterSymLst:
    #         symbol = symbol['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsM15 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)

    #         maxTrys = 0
    #         while(len(hisBarsM15)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsM15 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
            
    #         hisBarsStocksM15arr.append(
    #             {
    #                 'symbol': symbol,
    #                 'data': hisBarsM15
    #             }
    #         )

    #     pickle.dump(hisBarsStocksM15arr, open("./pickle/pro/compressed/hisBarsStocksM15arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksM15arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksM15arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksM15arr finished")

    # hisBarsStocksM5arr = []
    # saveStocksM5arr = False
    # if(saveStocksM5arr):
    #     for symbol in fillterSymLst:
    #         symbol = symbol['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsM5 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

    #         maxTrys = 0
    #         while(len(hisBarsM5)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsM5 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
            
    #         hisBarsStocksM5arr.append(
    #             {
    #                 'symbol': symbol,
    #                 'data': hisBarsM5
    #             }
    #         )

    #     pickle.dump(hisBarsStocksM5arr, open("./pickle/pro/compressed/hisBarsStocksM5arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksM5arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksM5arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksM5arr finished")

    fee = 1.001392062 * 2
    tpVal = 23.3
    maxProfit = 0 #41.07
    maxTpVal = 0
    maxMarCapLimit = 0
    maxVolavgLimit = 0
    maxBrk = 0
    maxTch = 0
    maxLevel = 0
    maxLineLife = 0

    tradeHisBarsM5arr = []
    tradeHisBarsQQQarr = []
    hisBarsD1arr = []

    brk = 1
    while(brk <= 100):
        tch = 1
        while(tch <= 100):
            level = 2
            while(level <= 100):
                lineLife = 1
                while(lineLife <= 100):
                    total = 0
                    net = 0
                    win = 0
                    loss = 0
                    totalNetProfit = 0
                    totalNetLoss = 0
                    # singleTrade = []
                    for trade in trades:
                        symbol = trade['symbol']
                        if not list(filter(lambda x:x['symbol'] == symbol,fillterSymLst)): continue
                        # if symbol == "AMC": continue
                        backtestTime = trade['time']
                        op = trade['op']
                        if(op>13.60 and op < 50): continue
                        sl = trade['sl']
                        tp = trade['tp']
                        vol = trade['vol']
                        trade['result'] = ''
                        trade['total'] = 0
                        if(vol<3): continue
                        backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

                        opEndTime = ''

                        dataM30 = []
                        for hisBarsStockM30 in hisBarsStocksM30arr:
                            if symbol == hisBarsStockM30['symbol']:
                                dataM30 = hisBarsStockM30['data']
                                break

                        if(len(dataM30) < 6):continue
                        testhisBarsM30 = list(filter(lambda x:x.date >= backtestTime,dataM30))
                        hisBarsM30 = list(filter(lambda x:x.date <= backtestTime,dataM30))

                        hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),hisBarsQQQD1arr))
                        hisBarsQQQD1 = hisBarsQQQD1[::-1]

                        # hisBarsQQQM30 = list(filter(lambda x:x.date <= backtestTime,hisBarsQQQM30arr))
                        # hisBarsQQQM30 = hisBarsQQQM30[::-1]

                        # hisBarsQQQM5 = list(filter(lambda x:x.date <= backtestTime+timedelta(minutes=10),hisBarsQQQM5arr))
                        # hisBarsQQQM5 = hisBarsQQQM5[::-1]

                        # dataMN1 = []
                        # for hisBarsStockMN1 in hisBarsStocksMN1arr:
                        #     if "symbol" in hisBarsStockMN1.keys():
                        #         if symbol == hisBarsStockMN1['symbol']:
                        #             dataMN1 = hisBarsStockMN1['data']
                        #             break

                        # if(len(dataMN1) < 6):continue
                        # hisBarsMN1 = list(filter(lambda x:x.date <= backtestTime.date(),dataMN1))
                        # hisBarsMN1 = hisBarsMN1[::-1]

                        dataD1 = []
                        for hisBarsStockD1 in hisBarsStocksD1arr:
                            if symbol == hisBarsStockD1['symbol']:
                                dataD1 = hisBarsStockD1['data']
                                break

                        if(len(dataD1) < 6):continue
                        hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
                        hisBarsD1 = hisBarsD1[::-1]

                        # dataM5 = []
                        # for hisBarsStockM5 in hisBarsStocksM5arr:
                        #     if symbol == hisBarsStockM5['symbol']:
                        #         dataM5 = hisBarsStockM5['data']
                        #         break

                        # if(len(dataM5) < 6):continue
                        # hisBarsM5 = list(filter(lambda x:x.date <= backtestTime+timedelta(minutes=10),dataM5))
                        # hisBarsM5 = hisBarsM5[::-1]

                        hisBarsD1closeArr = []
                        for d in hisBarsD1:
                            hisBarsD1closeArr.append(d.close)

                        # hisBarsM30closeArr = []
                        # for d in hisBarsM30:
                        #     hisBarsM30closeArr.append(d.close)

                        sma25D1 = sma(hisBarsD1closeArr[1:26], 25)
                        ema21D1 = ema(hisBarsD1closeArr[1:22], 21)
                        sma5D1second = sma(hisBarsD1closeArr[2:7], 5)
                        sma5D1third = sma(hisBarsD1closeArr[3:8], 5)

                        # ema20D1 = ema(hisBarsD1closeArr[1:21], 20)
                        # ema20D1second = ema(hisBarsD1closeArr[2:22], 20)
                        # ema20D1third = ema(hisBarsD1closeArr[3:23], 20)
                        # ema20D1forth = ema(hisBarsD1closeArr[4:24], 20)
                        # ema20D1fifth = ema(hisBarsD1closeArr[5:25], 20)
                        # ema20D1sixth = ema(hisBarsD1closeArr[6:26], 20)

                        buy = 0
                        bias = (hisBarsD1[1].close-sma25D1)/sma25D1
                        bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

                        biasval = 0.0482831585
                        if (
                            bias < -biasval 
                            and bias2 < -biasval
                        ):
                            buy += 1

                        if(
                            hisBarsD1[2].close - hisBarsD1[2].low
                            > (hisBarsD1[2].high - hisBarsD1[2].low) * 0.46
                            and hisBarsD1[1].close - hisBarsD1[1].low
                            > (hisBarsD1[1].high - hisBarsD1[1].low) * 0.98
                            and bias < -biasval
                            and bias2 < -biasval
                        ):
                            buy += 1

                        k = 1
                        while(k < 5):
                            maxUsedBar = 4
                            if(k<27/maxUsedBar):
                                signalCandleClose3 = hisBarsD1[k*2+1].close
                                signalCandleOpen3 = hisBarsD1[k*3].open
                                bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                                smallCandleRange3 = hisBarsD1[k*4].high - hisBarsD1[k*4].low
                                endCandleRange3 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

                                if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 6.054347826086946):
                                    if (signalCandleClose3 > signalCandleOpen3
                                        and abs(hisBarsD1[k+1].close - hisBarsD1[k*2].open) < bigCandleRange3
                                        and endCandleRange3 < bigCandleRange3*0.5
                                        and hisBarsD1[2].high < hisBarsD1[3].high
                                        ):
                                            buy += 1
                            k += 1

                        if(
                            ema21D1 > sma25D1
                            and sma5D1second <= sma5D1third
                            and hisBarsD1[1].low>hisBarsD1[2].low
                            and hisBarsD1[2].low>hisBarsD1[3].low
                            and hisBarsD1[3].low>hisBarsD1[4].low
                            and hisBarsD1[4].low>hisBarsD1[5].low
                            and hisBarsD1[5].low>hisBarsD1[6].low
                            and bias < -biasval
                            and bias2 < -biasval
                        ):
                            buy += 1
                            
                        # Morning star
                        if(
                            hisBarsD1[2].high < hisBarsD1[3].low
                            and hisBarsD1[1].low > hisBarsD1[2].high
                        ):
                            buy += 1

                        # if(
                        #     hisBarsD1[1].open > ema20D1
                        #     and hisBarsD1[1].close > ema20D1
                        #     and hisBarsD1[2].open > ema20D1second
                        #     and hisBarsD1[2].close > ema20D1second
                        #     and hisBarsD1[3].open > ema20D1third
                        #     and hisBarsD1[3].close > ema20D1third
                        #     and hisBarsD1[4].open > ema20D1forth
                        #     and hisBarsD1[4].close > ema20D1forth
                        #     and hisBarsD1[5].open > ema20D1fifth
                        #     and hisBarsD1[5].close > ema20D1fifth
                        #     and hisBarsD1[6].open > ema20D1sixth
                        #     and hisBarsD1[6].close > ema20D1sixth
                        #     and (
                        #             # (
                        #             #     hisBarsD1[1].close > hisBarsD1[1].open
                        #             #     and hisBarsD1[1].high -hisBarsD1[1].close
                        #             #         > (hisBarsD1[1].high -hisBarsD1[1].low) * 0.45
                        #             # )
                        #             # or
                        #             (
                        #                 hisBarsD1[1].close < hisBarsD1[1].open
                        #                 and hisBarsD1[1].high -hisBarsD1[1].open
                        #                     > (hisBarsD1[1].high -hisBarsD1[1].low) * 0.45
                        #             )
                        #     )
                        # ):
                        #     buy += 1


                        # insider = get_insider(symbol)
                        # if(len(insider) > 0):
                        #     for insiderData in insider:
                        #         if 'SEC Form 4' in insiderData.keys():
                        #             date = insiderData['Date']
                        #             date = dt.strptime(date, '%b %d')
                        #             date = date.replace(year = dt.now().year)
                        #             time = insiderData['SEC Form 4']
                        #             time = dt.strptime(time, '%b %d %H:%M %p')
                        #             time = time.replace(year = dt.now().year)
                                    
                        #             if(date.date()==time.date()):
                        #                 limitTime = time+timedelta(days=1)
                        #                 weekday = limitTime.weekday()
                        #                 if(weekday == 6):
                        #                     limitTime = time+timedelta(days=2)

                        #                 if(
                        #                     backtestTime <= limitTime
                        #                     and backtestTime >= time
                        #                 ):
                        #                     relationship = insiderData['Relationship']
                        #                     if "CEO" in relationship or "Chief Executive Officer" in relationship:
                        #                         transaction = insiderData['Transaction']
                        #                         print(transaction)
                        #                         if transaction == "Buy":
                        #                             buy += 1

                        ## 3 bar play

                        # if(
                        #     hisBarsD1[3].close > hisBarsD1[3].open
                        #     and hisBarsD1[2].high < hisBarsD1[3].high
                        #     and hisBarsD1[2].low > hisBarsD1[3].low
                        # ):  buy += 1

                        # if(
                        #     hisBarsM30[2].close > hisBarsM30[2].open
                        #     and hisBarsM30[1].high < hisBarsM30[2].high
                        #     and hisBarsM30[1].low > hisBarsM30[2].low
                        #     and hisBarsM30[2].close - hisBarsM30[2].open
                        #         > (hisBarsM30[3].high - hisBarsM30[3].low)
                        # ):  buy += 1




                        # preBias = hisBarsD1[0].open/hisBarsD1[1].open

                        # Pre Relative Strength
                        # preQQQBias = hisBarsQQQD1[0].open/hisBarsQQQD1[1].open

                        # if preBias > preQQQBias:
                        #     buy += 1

                        # Sector Leader
                        # curSectorLst = []
                        # for sym in fillterSymLst:
                        #     if sym['symbol'] == symbol:
                        #         curSectorLst = sectorLst[sym['sector']]
                        
                        # maxSectorpreBias = 0
                        # for secSym in curSectorLst:
                        #     if secSym == symbol:
                        #         continue
                        #     dataSectorD1 = []
                        #     for hisBarsStockD1 in hisBarsStocksD1arr:
                        #         if hisBarsStockD1['symbol'] == secSym:
                        #             dataSectorD1 = hisBarsStockD1['data']
                        #             break
                        #     if(len(dataSectorD1)>6):
                        #         sectorpreBias = dataSectorD1[0].open/dataSectorD1[1].open
                        #         if sectorpreBias > maxSectorpreBias:
                        #             maxSectorpreBias = sectorpreBias

                        # if(
                        #     maxSectorpreBias != 0 
                        #     and preBias > preQQQBias 
                        #     and preBias > maxSectorpreBias
                        # ):
                        #     buy += 1
                            


                        # # Relative Strength
                        # biasQQQM5bar1 = hisBarsQQQM5[1].close/hisBarsQQQM5[1].open
                        # biasQQQM5bar2 = hisBarsQQQM5[2].close/hisBarsQQQM5[2].open
                        # biasM5bar1 = hisBarsM5[1].close/hisBarsM5[1].open
                        # biasM5bar2 = hisBarsM5[2].close/hisBarsM5[2].open

                        # if(
                        #     biasM5bar2 > biasQQQM5bar2
                        #     and biasM5bar1 > biasQQQM5bar1
                        # ):
                        #     buy += 1

                        

                        # x = 1
                        # while(x < 2):
                        # if(
                        #     hisBarsD1[x*3+1].close < hisBarsD1[x*4].open
                        #     and hisBarsD1[x*2+1].close < hisBarsD1[x*3].open
                        #     and hisBarsD1[x+1].close < hisBarsD1[x*2].open
                        #     and hisBarsD1[1].close > hisBarsD1[1].open):
                        #     buy += 1
                            # x += 1

                        # if(
                        #     hisBarsD1[4].close < hisBarsD1[4].open
                        #     and hisBarsD1[3].close < hisBarsD1[3].open
                        #     and hisBarsD1[2].close > hisBarsD1[2].open
                        #     and hisBarsD1[1].close > hisBarsD1[1].open
                        #     and hisBarsD1[1].close > hisBarsD1[4].open
                        # ):
                        #     buy += 1

                        
                        # ATR = ((hisBarsD1[1].high - hisBarsD1[1].low) +
                        #         (hisBarsD1[2].high - hisBarsD1[2].low) +
                        #         (hisBarsD1[3].high - hisBarsD1[3].low) +
                        #         (hisBarsD1[4].high - hisBarsD1[4].low) +
                        #         (hisBarsD1[5].high - hisBarsD1[5].low)) / 5

                        # currentLongRange = hisBarsD1[1].close - hisBarsD1[0].open

                        # k = 1
                        # maxUsedBar = 5
                        # if(k<27/maxUsedBar):
                        #     signalCandleClose4 = hisBarsD1[k*3+1].close
                        #     signalCandleOpen4 = hisBarsD1[k*4].open
                        #     bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
                        #     smallCandleRange4 = hisBarsD1[k*5].high - hisBarsD1[k*5].low
                        #     endCandleRange4 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

                        #     if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
                        #         if (signalCandleClose4 > signalCandleOpen4
                        #             and abs(hisBarsD1[k*2+1].close - hisBarsD1[k*3].open) < bigCandleRange4
                        #             # and abs(hisBarsD1[k+1].close - hisBarsD1[k*2].open) < bigCandleRange4
                        #             and endCandleRange4 < bigCandleRange4*0.5
                        #             ):
                        #                 buy += 1
                        #     k += 1

                        if buy < 1: continue

                        # # Inside day
                        # if(
                        #     hisBarsQQQD1[1].close < hisBarsQQQD1[1].open
                        #     and hisBarsQQQD1[0].open > hisBarsQQQD1[1].low
                        #     and hisBarsQQQD1[0].open < hisBarsQQQD1[1].high
                        #     # and hisBarsQQQD1[0].open 
                        #     #     < hisBarsQQQD1[1].low + (hisBarsQQQD1[1].high
                        #     #                                 -hisBarsQQQD1[1].low) * 0.28
                        # ): continue

                        # # Relative strength
                        # if(
                        #     (hisBarsQQQD1[1].close > hisBarsQQQD1[1].open
                        #     and hisBarsD1[1].close < hisBarsD1[1].open)
                        # ): continue

                        # # Previous day inside bar
                        # if(
                        #     (hisBarsD1[1].high < hisBarsD1[2].high
                        #     and hisBarsD1[1].low > hisBarsD1[2].low)
                        # ): continue

                        # sma25 = sum(map(lambda x: x.close, hisBarsD1[1:26]))/25

                        # if(
                        #     hisBarsD1[0].open/sma25 > 1.176
                        # ): continue

                        plotLinesRes = plotLines(hisBarsD1,brk=brk,body=False,tch=tch,level=level,lineLife=lineLife)
                        if(plotLinesRes < 0):
                            continue
                        
                        trade['status'] = ''
                        for i in testhisBarsM30:
                            if i.high >= op:
                                trade['status'] = i.date
                                break

                        trade['result'] = ''
                        if trade['status'] != '':
                            triggeredTime = trade['status']
                            for i in testhisBarsM30:
                                if i.date >= triggeredTime:
                                    if i.date == triggeredTime:
                                        if i.high >= tp:
                                            net = (tp-op)*vol - fee
                                            # singleTrade.append(
                                            #     {
                                            #         'profit': net,
                                            #         'symbol': symbol,
                                            #         'time': triggeredTime
                                            #     }
                                            # )
                                            trade['total'] = net
                                            if(net > 0):
                                                trade['result'] = 'profit'
                                                totalNetProfit += net
                                                win += 1
                                            else:
                                                trade['result'] = 'loss'
                                                totalNetLoss += net
                                                loss += 1
                                            total += net
                                            break
                                    else:
                                        if i.low <= sl:
                                            net = (sl-op)*vol - fee
                                            # singleTrade.append(
                                            #     {
                                            #         'profit': net,
                                            #         'symbol': symbol,
                                            #         'time': triggeredTime
                                            #     }
                                            # )
                                            trade['total'] = net
                                            trade['result'] = 'loss'
                                            totalNetLoss += net
                                            loss += 1
                                            total += net
                                            break

                                        if i.high >= tp:
                                            net = (tp-op)*vol - fee
                                            # singleTrade.append(
                                            #     {
                                            #         'profit': net,
                                            #         'symbol': symbol,
                                            #         'time': triggeredTime
                                            #     }
                                            # )
                                            trade['total'] = net
                                            if(net > 0):
                                                trade['result'] = 'profit'
                                                totalNetProfit += net
                                                win += 1
                                            else:
                                                trade['result'] = 'loss'
                                                totalNetLoss += net
                                                loss += 1
                                            total += net
                                            break
                                        
                                        # if i.date >= endTime:
                                        #     print(symbol," closeAtPre ",i.date)
                                        #     if(i.open > op):
                                        #         net = (i.open-op)*vol - 2
                                        #         trade['total'] = net
                                        #         if(net > 0):
                                        #             trade['result'] = 'profit closeAtPre'
                                        #             totalNetProfit += net
                                        #             win += 1
                                        #         else:
                                        #             trade['result'] = 'loss closeAtPre'
                                        #             totalNetLoss += net
                                        #             loss += 1
                                        #         total += net
                                        #     else:
                                        #         net = (i.open-op)*vol - 2
                                        #         trade['total'] = net
                                        #         trade['result'] = 'loss closeAtPre'
                                        #         totalNetLoss += net
                                        #         loss += 1
                                        #         total += net
                                        #     break
                    winrate = 0
                    if(win+loss>0):
                        winrate = win/(win+loss)
                    profitfactor =0
                    if(abs(totalNetLoss)>0):
                        profitfactor = totalNetProfit/abs(totalNetLoss)
                    elif(totalNetProfit>0):
                        profitfactor = 99.99
                    print("total",str(total),
                            "wr",winrate*100,"%",
                            "profitfactor",str(profitfactor))
                    if(total > maxProfit): # and winrate>0.067
                        maxProfit = total
                        maxTpVal = tpVal
                        maxBrk = brk
                        maxTch = tch
                        maxLevel = level
                        maxLineLife = lineLife
                    print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
                    print('maxBrk',str(maxBrk),'maxTch',str(maxTch),
                    'maxLevel',str(maxLevel),'maxLineLife',str(maxLineLife))
                    lineLife += 1
                level += 1
            tch += 1
        brk += 1
                    
    df = pd.DataFrame(trades)
    df.to_csv('./trades_status.csv')

    # singleTrade = sorted(singleTrade, key=lambda x:x['profit'], reverse=True)
    # df = pd.DataFrame(trades)
    # df.to_csv('./csv/result/trades_status.csv')

    # singleTradeDf = pd.DataFrame(singleTrade)
    # singleTradeDf.to_csv('./csv/result/single_trade.csv')
except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)