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
sys.path.append('../')
from aizfinviz import get_insider
from modules.supertrend import supertrend
import requests

ib = IB()

# # IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=11)

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)
cash = 1402.23

day = ib.reqCurrentTime().day
# 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
risk = 0.06#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837

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

df = pd.read_csv (r'./csv/trades_novollimit.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))

fillterDf = pd.read_csv (r'./csv/symbolLst.csv', index_col=0)
fillterDf.drop
fillterSymLst = json.loads(fillterDf.to_json(orient = 'records'))

arkfund_df = pd.read_csv (r'./csv/ark-fund.csv', index_col=0)
arkfund_df.drop
arkfund_list = json.loads(arkfund_df.to_json(orient = 'records'))

# sectorDf = pd.read_csv (r'./csv/sector.csv', index_col=0)
# sectorDf.drop
# secLst = json.loads(sectorDf.to_json(orient = 'records'))
# sectorLst = sectorDf.groupby('sector')['symbol'].apply(list)

try:
    # hisBarsQQQD1arr = [] 
    # saveQQQD1 = False
    # if(saveQQQD1):
    #     contractQQQ = Stock("QQQ", 'SMART', 'USD')
    #     hisBarsQQQD1 = ib.reqHistoricalData(
    #         contractQQQ, endDateTime='', durationStr='365 D',
    #         barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    #     while(len(hisBarsQQQD1)<6):
    #         print("timeout")
    #         hisBarsQQQD1 = ib.reqHistoricalData(
    #             contractQQQ, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    #     hisBarsQQQD1arr = hisBarsQQQD1
    #     pickle.dump(hisBarsQQQD1arr, open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "wb"), protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "rb")
    #     gc.disable()
    #     hisBarsQQQD1arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsQQQD1arr finished")

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

    hisBarsStocksW1arr = []
    saveStocksW1arr = False
    if(saveStocksW1arr):
        for trade in fillterSymLst:
            symbol = trade['symbol']
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsW1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='52 W',
                barSizeSetting='1W', whatToShow='ASK', useRTH=True)
            maxTrys = 0
            while(len(hisBarsW1)<6 and maxTrys<=20):
                print("timeout")
                hisBarsW1 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='52 W',
                    barSizeSetting='1W', whatToShow='ASK', useRTH=True)
                maxTrys += 1
            hisBarsStocksW1arr.append({'s': symbol,'d': hisBarsW1})
        pickle.dump(hisBarsStocksW1arr, open("./pickle/pro/compressed/hisBarsStocksW1arr.p", "wb"),protocol=-1)
        print("pickle dump finished")
    else:
        output = open("./pickle/pro/compressed/hisBarsStocksW1arr.p", "rb")
        gc.disable()
        hisBarsStocksW1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksW1arr finished")

    hisBarsStocksD1arr = []
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

    # hisBarsStocksH8arr = []
    # saveStocksH8arr = False
    # if(saveStocksH8arr):
    #     for trade in fillterSymLst:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsH8 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='8 hours', whatToShow='ASK', useRTH=True)
    #         maxTrys = 0
    #         while(len(hisBarsH8)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsH8 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='8 hours', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
    #         hisBarsStocksH8arr.append({'s': symbol,'d': hisBarsH8})
    #     pickle.dump(hisBarsStocksH8arr, open("./pickle/pro/compressed/hisBarsStocksH8arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksH8arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksH8arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksH8arr finished")

    # hisBarsStocksH4arr = []
    # saveStocksH4arr = False
    # if(saveStocksH4arr):
    #     for trade in fillterSymLst:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsH4 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)
    #         maxTrys = 0
    #         while(len(hisBarsH4)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsH4 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
    #         hisBarsStocksH4arr.append({'s': symbol,'d': hisBarsH4})
    #     pickle.dump(hisBarsStocksH4arr, open("./pickle/pro/compressed/hisBarsStocksH4arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksH4arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksH4arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksH4arr finished")

    # hisBarsStocksH3arr = []
    # saveStocksH3arr = False
    # if(saveStocksH3arr):
    #     for trade in fillterSymLst:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsH3 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)
    #         maxTrys = 0
    #         while(len(hisBarsH3)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsH3 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
    #         hisBarsStocksH3arr.append({'s': symbol,'d': hisBarsH3})
    #     pickle.dump(hisBarsStocksH3arr, open("./pickle/pro/compressed/hisBarsStocksH3arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksH3arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksH3arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksH3arr finished")

    # hisBarsStocksH2arr = []
    # saveStocksH2arr = False
    # if(saveStocksH2arr):
    #     for trade in fillterSymLst:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsH2 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='2 hours', whatToShow='ASK', useRTH=True)
    #         maxTrys = 0
    #         while(len(hisBarsH2)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsH2 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='2 hours', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
    #         hisBarsStocksH2arr.append({'s': symbol,'d': hisBarsH2})
    #     pickle.dump(hisBarsStocksH2arr, open("./pickle/pro/compressed/hisBarsStocksH2arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksH2arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksH2arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksH2arr finished")

    # hisBarsStocksH1arr = []
    # saveStocksH1arr = False
    # if(saveStocksH1arr):
    #     for trade in fillterSymLst:
    #         symbol = trade['symbol']
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsH1 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)
    #         maxTrys = 0
    #         while(len(hisBarsH1)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsH1 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
    #         hisBarsStocksH1arr.append({'s': symbol,'d': hisBarsH1})
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
    tpVal = 25.2
    maxProfit = 0 #41.07
    maxTpVal = 0
    maxMarCapLimit = 0
    maxVolavgLimit = 0
    max_vol_limit = 0

    tradeHisBarsM5arr = []
    tradeHisBarsQQQarr = []
    hisBarsD1arr = []

    vol_limit = 1
    while(vol_limit<10):
        total = 0
        net = 0
        win = 0
        loss = 0
        totalNetProfit = 0
        totalNetLoss = 0
        for trade in trades:
            symbol = trade['symbol']
            if not list(filter(lambda x:x['symbol'] == symbol,fillterSymLst)): continue
            if symbol == "SPCE" or symbol == "CSCO" or symbol == "SHIP": continue
            backtestTime = trade['time']
            op = trade['op']
            # if(op>13.60 and op < 50): continue
            sl = trade['sl']
            tp = normalizeFloat(op+(op-sl)*tpVal,op,sl)
            vol = int(cash * risk / op)
            # vol = trade['vol']
            trade['result'] = ''
            trade['total'] = 0
            if(vol<vol_limit): continue
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

            dataD1 = []
            for hisBarsStockD1 in hisBarsStocksD1arr:
                if symbol == hisBarsStockD1['symbol']:
                    dataD1 = hisBarsStockD1['data']
                    break

            if(len(dataD1) < 6):continue
            hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
            hisBarsD1 = hisBarsD1[::-1]

            plotLinesRes = plotLines(hisBarsD1)
            if(plotLinesRes < 0):
                continue

            buy = 0

            # Ark-fund
            ark_fund = False
            ark_fund_sell = False

            TRADE_STATUS_URL = "http://127.0.0.1:8000/api/v1/stock/trades?symbol="+symbol
            res = requests.get(TRADE_STATUS_URL, timeout=10)
            html = res.text
            if res.status_code == 200 and "no trades listed" not in html:
                r = res.json()['trades']
                for i in r:
                    date = dt.strptime(i['date'], '%Y-%m-%d')
                    date_end = date + timedelta(days=1)
                    if date_end.isoweekday()==5:
                        date_end += timedelta(days=3)
                    direction = i['direction']
                    if date >= backtestTime and backtestTime <= date_end:
                        if direction == 'Sell':
                            ark_fund_sell = True

            # for trade in arkfund_list:
            #     if trade['Ticker'] == symbol:
            #         date = dt.strptime(trade['Date'], '%Y-%m-%d')
            #         date_end = date + timedelta(days=1)
            #         if date_end.isoweekday()==5:
            #             date_end += timedelta(days=3)
            #         direction = trade['Direction']
            #         if date >= backtestTime and backtestTime <= date_end:
            #             if direction == 'Sell':
            #                 ark_fund_sell = True
        
            if ark_fund_sell: continue

            opEndTime = ''

            dataM30 = []
            for hisBarsStockM30 in hisBarsStocksM30arr:
                if symbol == hisBarsStockM30['symbol']:
                    dataM30 = hisBarsStockM30['data']
                    break

            if(len(dataM30) < 6):continue
            hisBarsM30 = list(filter(lambda x:x.date <= backtestTime,dataM30))

            

            dataW1 = []
            for hisBarsStockW1 in hisBarsStocksW1arr:
                if symbol == hisBarsStockW1['s']:
                    dataW1 = hisBarsStockW1['d']
                    break
            if(len(dataW1) < 6):
                print(symbol,'W1 no data')
                continue
            hisBarsW1 = list(filter(lambda x:x.date <= backtestTime.date(),dataW1))
            hisBarsW1 = hisBarsW1[::-1]

            hisBarsD1closeArr = []
            for d in hisBarsD1:
                hisBarsD1closeArr.append(d.close)

            sma25D1 = sma(hisBarsD1closeArr[1:26], 25)
            
            bias = (hisBarsD1[1].close-sma25D1)/sma25D1
            bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

            biasSignal = False
            biasval = 0.0482831585
            if (
                bias < -biasval 
                and bias2 < -biasval
            ):
                buy += 1
                biasSignal = True

            # 3 bar play
            if(
                hisBarsW1[2].close > hisBarsW1[2].open
                and hisBarsW1[2].close - hisBarsW1[2].open
                    > hisBarsW1[3].high - hisBarsW1[3].low
                and hisBarsW1[1].high - hisBarsW1[1].low
                    < hisBarsW1[2].high - hisBarsW1[2].low
            ):
                buy += 1

            bp3_d1 = False
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
                                bp3_d1 = True
                k += 1

            turnArround = False
            if(
                hisBarsM30[2].close < hisBarsM30[2].open
                and hisBarsM30[1].close > hisBarsM30[1].open
            ):
                buy += 1
                turnArround = True

            k = 1
            maxUsedBar = 5
            while(k<=1):
                if(k<27/maxUsedBar):
                    signalCandleClose4 = hisBarsD1[k*3+1].close
                    signalCandleOpen4 = hisBarsD1[k*4].open
                    bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
                    smallCandleRange4 = hisBarsD1[k*5].high - hisBarsD1[k*5].low
                    endCandleRange4 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

                    if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
                        if (signalCandleClose4 > signalCandleOpen4
                            and abs(hisBarsD1[k*2+1].close - hisBarsD1[k*3].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                            ):
                                buy += 1
                k += 1
            
            if buy < 1: continue
            if biasSignal and buy == 1:
                tp = normalizeFloat(op+(op-sl)*20.5,op,sl)
            if turnArround and buy == 1:
                tp = normalizeFloat(op+(op-sl)*22.5,op,sl)
            if bp3_d1 and buy == 1:
                tp = normalizeFloat(op+(op-sl)*25.9,op,sl)
            if ark_fund and buy == 1:
                tp = normalizeFloat(op+(op-sl)*25.2,op,sl)

            testhisBarsM30 = list(filter(lambda x:x.date >= backtestTime,dataM30))
            trade['status'] = ''
            for i in testhisBarsM30:
                if i.high >= op:
                    trade['status'] = i.date
                    break

            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                endTime = triggeredTime+timedelta(minutes=15)
                for i in testhisBarsM30:
                    if i.date >= triggeredTime:
                        if i.date == triggeredTime:
                            if i.high >= tp:
                                net = (tp-op)*vol - fee
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
                                trade['total'] = net
                                trade['result'] = 'loss'
                                totalNetLoss += net
                                loss += 1
                                total += net
                                break

                            if i.high >= tp:
                                net = (tp-op)*vol - fee
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
            max_vol_limit = vol_limit
        print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
        print('max_vol_limit',str(max_vol_limit))
        vol_limit += 1
                    
    # df = pd.DataFrame(trades)
    # df.to_csv('./trades_status.csv')

    # singleTrade = sorted(singleTrade, key=lambda x:x['profit'], reverse=True)
    # df = pd.DataFrame(trades)
    # df.to_csv('./csv/result/trades_status.csv')

    # singleTradeDf = pd.DataFrame(singleTrade)
    # singleTradeDf.to_csv('./csv/result/single_trade.csv')
except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)