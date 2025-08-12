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

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=8)

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)

day = ib.reqCurrentTime().day
# 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
risk = 0.06#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

df = pd.read_csv (r'./trades.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))

def countSlopingCrosses(hisBars, fromBar :int, toBar :int, brk :int, rng :float, pk :bool, body: bool):
    t :int = 0
    x :int = 0
    lastCross :int = 0
    flag :bool = False
    slope :float = 0
    val :float = 0
    try:
        if(pk):
            slope = ((hisBars[fromBar].high - hisBars[toBar].high)/(fromBar - toBar))
        else:
            slope = ((hisBars[fromBar].low - hisBars[toBar].low)/(fromBar - toBar))
        i = fromBar
        while(i>0):
            flag = True
            if(pk):
                val = (slope * (i - fromBar)) + hisBars[fromBar].high 
                if(hisBars[i].high + rng >= val):
                    t += 1
                if(body and hisBars[i].open > val):
                    flag = False
                    x += 1
                if(flag and hisBars[i].close > val):
                    x += 1
            else:
                val = (slope * (i - fromBar)) + hisBars[fromBar].low
                if(hisBars[i].low - rng <= val):
                    t += 1
                if(body and hisBars[i].open < val):
                    flag = False
                    x += 1
                if(flag and hisBars[i].close < val):
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
                if(hisBars[i+1].high > hisBars[i].high and hisBars[i+1].high >= hisBars[i+2].high):
                    pk0C = pk0B
                    pk0B = pk0A
                    pk0A = i+1
                    if (level < 1):
                        pkArr[p] = i+1
                        p+=1
                    elif (pk0C > 0 and hisBars[pk0B].high > hisBars[pk0A].high 
                            and hisBars[pk0B].high >= hisBars[pk0C].high):
                        pk1C = pk1B
                        pk1B = pk1A
                        pk1A = pk0B
                        if ( level < 2 ):
                            pkArr[p] = pk0B
                            p+=1;      
                        elif (pk1C > 0 and hisBars[pk1B].high > hisBars[pk1A].high 
                                and hisBars[pk1B].high >= hisBars[pk1C].high):
                            pkArr.append(0)
                            pkArr[p] = pk1B
                            p+=1

                if (hisBars[i+1].low < hisBars[i].low 
                        and hisBars[i+1].low <= hisBars[i+2].low):
                    tr0C = tr0B
                    tr0B = tr0A
                    tr0A = i+1
                    if (level < 1):
                        trArr[t] = i+1
                        t+=1
                    elif (tr0C > 1 and hisBars[tr0B].low < hisBars[tr0A].low 
                            and hisBars[tr0B].low <= hisBars[tr0C].low):
                        tr1C = tr1B
                        tr1B = tr1A
                        tr1A = tr0B
                        if ( level < 2 ):
                            trArr[t] = tr0B
                            t += 1
                        elif (tr1C > 0 and hisBars[tr1B].low < hisBars[tr1A].low 
                                and hisBars[tr1B].low <= hisBars[tr1C].low):
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
                        slope = (hisBars[pkArr[i]].high - hisBars[pkArr[j]].high) / (pkArr[i] - pkArr[j])
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
                        slope = (hisBars[trArr[i]].low - hisBars[trArr[j]].low) / (trArr[i] - trArr[j])
                        slopeLower = slope
                    j += 1
                i += 1
    
        if(slopeUpper > 0 or slopeLower > 0): 
            print("slopeUpper "+str(slopeUpper))
            print("slopeLower "+str(slopeLower))
            return 1
        if(slopeUpper < 0 or slopeLower < 0): return -1
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

try:
    fee = 1.001392062 * 2
    tpVal = 20.189
    maxProfit = 0 #41.07
    maxTpVal = 0
    maxMarCapLimit = 0
    maxVolavgLimit = 0
    tradeHisBarsM5arr = []
    tradeHisBarsQQQarr = []
    hisBarsD1arr = []
    hisBarsH8arr = []
    hisBarsH4arr = []
    hisBarsH3arr = []
    hisBarsH2arr = []
    hisBarsH1arr = []
    hisBarsM30arr = []
    hisBarsM20arr = []
    hisBarsM15arr = []
    hisBarsM10arr = []
    hisBarsM5arr = []
    hisBarsM3arr = []
    hisBarsM2arr = []
    saveData = False
    if(saveData):
        for trade in trades:
            symbol = trade['symbol']
            backtestTime = trade['time']
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
            opEndTime = ''
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM5 = ib.reqHistoricalData(
                contract, endDateTime=opEndTime, durationStr='90 D',
                barSizeSetting='5 mins', whatToShow='BID', useRTH=True)

            while(len(hisBarsM5)<6):
                print("timeout")
                hisBarsM5 = ib.reqHistoricalData(
                    contract, endDateTime=opEndTime, durationStr='90 D',
                    barSizeSetting='5 mins', whatToShow='BID', useRTH=True)

            hisBarsM5 = [data for data in hisBarsM5 if data.date >= backtestTime]
            tradeHisBarsM5arr.append(hisBarsM5)

        pickle.dump(tradeHisBarsM5arr, open("./pickle/tradeHisBarsM5arr.p", "wb"))
        print("pickle dump finished")
    else:
        tradeHisBarsM5arr = pickle.load(open("./pickle/tradeHisBarsM5arr.p", "rb"))
        print(tradeHisBarsM5arr[0][0].date)

    saveQQQ = False
    if(saveQQQ):
        for trade in trades:
            symbol = trade['symbol']
            backtestTime = trade['time']
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
            opEndTime = ''
            contractQQQ = Stock("QQQ", 'SMART', 'USD')

            hisBarsQQQ = ib.reqHistoricalData(
                contractQQQ, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            while(len(hisBarsQQQ)<6):
                print("timeout")
                hisBarsQQQ = ib.reqHistoricalData(
                contractQQQ, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            hisBarsQQQ = hisBarsQQQ[::-1]
            print(backtestTime,hisBarsQQQ[0].date)
            tradeHisBarsQQQarr.append(hisBarsQQQ)
            print("data get")

        pickle.dump(tradeHisBarsM5arr, open("./pickle/tradeHisBarsQQQarr.p", "wb"))
        print("pickle dump finished")
    else:
        tradeHisBarsQQQarr = pickle.load(open("./pickle/tradeHisBarsQQQarr.p", "rb"))
        print(tradeHisBarsQQQarr[0][0].date)

    saveHisBarsD1 = False
    if(saveHisBarsD1):
        for trade in trades:
            symbol = trade['symbol']
            backtestTime = trade['time']
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
            opEndTime = ''
            contract= Stock(symbol, 'SMART', 'USD')

            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            while(len(hisBarsD1)<6):
                print("timeout")
                hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=backtestTime, durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            hisBarsD1 = hisBarsD1[::-1]
            print(backtestTime,hisBarsD1[0].date)
            hisBarsD1arr.append(hisBarsD1)
            print("data get")

        pickle.dump(hisBarsD1arr, open("./pickle/hisBarsD1arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsD1arr = pickle.load(open("./pickle/hisBarsD1arr.p", "rb"))
        print(hisBarsD1arr[0][0].date)

    # saveHisBarsH8 = False
    # if(saveHisBarsH8):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsH8 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='8 hours', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsH8)<6):
    #             print("timeout")
    #             hisBarsH8 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='8 hours', whatToShow='ASK', useRTH=True)

    #         hisBarsH8 = hisBarsH8[::-1]
    #         print(backtestTime,hisBarsH8[0].date)
    #         hisBarsH8arr.append(hisBarsH8)
    #         print("data get")

    #     pickle.dump(hisBarsH8arr, open("./pickle/hisBarsH8arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsH8arr = pickle.load(open("./pickle/hisBarsH8arr.p", "rb"))
    #     print(hisBarsH8arr[0][0].date)

    # saveHisBarsH4 = False
    # if(saveHisBarsH4):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsH4 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsH4)<6):
    #             print("timeout")
    #             hisBarsH4 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)

    #         hisBarsH4 = hisBarsH4[::-1]
    #         print(backtestTime,hisBarsH4[0].date)
    #         hisBarsH4arr.append(hisBarsH4)
    #         print("data get")

    #     pickle.dump(hisBarsH4arr, open("./pickle/hisBarsH4arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsH4arr = pickle.load(open("./pickle/hisBarsH4arr.p", "rb"))
    #     print(hisBarsH4arr[0][0].date)

    # saveHisBarsH3 = False
    # if(saveHisBarsH3):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsH3 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsH3)<6):
    #             print("timeout")
    #             hisBarsH3 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)

    #         hisBarsH3 = hisBarsH3[::-1]
    #         print(backtestTime,hisBarsH3[0].date)
    #         hisBarsH3arr.append(hisBarsH3)
    #         print("data get")

    #     pickle.dump(hisBarsH3arr, open("./pickle/hisBarsH3arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsH3arr = pickle.load(open("./pickle/hisBarsH3arr.p", "rb"))
    #     print(hisBarsH3arr[0][0].date)

    # saveHisBarsH2 = False
    # if(saveHisBarsH2):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsH2 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='2 hours', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsH2)<6):
    #             print("timeout")
    #             hisBarsH2 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='2 hours', whatToShow='ASK', useRTH=True)

    #         hisBarsH2 = hisBarsH2[::-1]
    #         print(backtestTime,hisBarsH2[0].date)
    #         hisBarsH2arr.append(hisBarsH2)
    #         print("data get")

    #     pickle.dump(hisBarsH2arr, open("./pickle/hisBarsH2arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsH2arr = pickle.load(open("./pickle/hisBarsH2arr.p", "rb"))
    #     print(hisBarsH2arr[0][0].date)

    # saveHisBarsH1 = False
    # if(saveHisBarsH1):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsH1 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsH1)<6):
    #             print("timeout")
    #             hisBarsH1 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)

    #         hisBarsH1 = hisBarsH1[::-1]
    #         print(backtestTime,hisBarsH1[0].date)
    #         hisBarsH1arr.append(hisBarsH1)
    #         print("data get")

    #     pickle.dump(hisBarsH1arr, open("./pickle/hisBarsH1arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsH1arr = pickle.load(open("./pickle/hisBarsH1arr.p", "rb"))
    #     print(hisBarsH1arr[0][0].date)

    # saveHisBarsM30 = False
    # if(saveHisBarsM30):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM30 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM30)<6):
    #             print("timeout")
    #             hisBarsM30 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM30 = hisBarsM30[::-1]
    #         print(backtestTime,hisBarsM30[0].date)
    #         hisBarsM30arr.append(hisBarsM30)
    #         print("data get")

    #     pickle.dump(hisBarsM30arr, open("./pickle/hisBarsM30arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM30arr = pickle.load(open("./pickle/hisBarsM30arr.p", "rb"))
    #     print(hisBarsM30arr[0][0].date)

    # saveHisBarsM20 = False
    # if(saveHisBarsM20):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM20 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM20)<6):
    #             print("timeout")
    #             hisBarsM20 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM20 = hisBarsM20[::-1]
    #         print(backtestTime,hisBarsM20[0].date)
    #         hisBarsM20arr.append(hisBarsM20)
    #         print("data get")

    #     pickle.dump(hisBarsM20arr, open("./pickle/hisBarsM20arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM20arr = pickle.load(open("./pickle/hisBarsM20arr.p", "rb"))
    #     print(hisBarsM20arr[0][0].date)

    # saveHisBarsM15 = False
    # if(saveHisBarsM15):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM15 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM15)<6):
    #             print("timeout")
    #             hisBarsM15 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='365 D',
    #             barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM15 = hisBarsM15[::-1]
    #         print(backtestTime,hisBarsM15[0].date)
    #         hisBarsM15arr.append(hisBarsM15)
    #         print("data get")

    #     pickle.dump(hisBarsM15arr, open("./pickle/hisBarsM15arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM15arr = pickle.load(open("./pickle/hisBarsM15arr.p", "rb"))
    #     print(hisBarsM15arr[0][0].date)

    # saveHisBarsM10 = False
    # if(saveHisBarsM10):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM10 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='180 D',
    #             barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM10)<6):
    #             print("timeout")
    #             hisBarsM10 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='180 D',
    #             barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM10 = hisBarsM10[::-1]
    #         print(backtestTime,hisBarsM10[0].date)
    #         hisBarsM10arr.append(hisBarsM10)
    #         print("data get")

    #     pickle.dump(hisBarsM10arr, open("./pickle/hisBarsM10arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM10arr = pickle.load(open("./pickle/hisBarsM10arr.p", "rb"))
    #     print(hisBarsM10arr[0][0].date)

    # saveHisBarsM5 = False
    # if(saveHisBarsM5):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM5 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='90 D',
    #             barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM5)<6):
    #             print("timeout")
    #             hisBarsM5 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='90 D',
    #             barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM5 = hisBarsM5[::-1]
    #         print(backtestTime,hisBarsM5[0].date)
    #         hisBarsM5arr.append(hisBarsM5)
    #         print("data get")

    #     pickle.dump(hisBarsM5arr, open("./pickle/hisBarsM5arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM5arr = pickle.load(open("./pickle/hisBarsM5arr.p", "rb"))
    #     print(hisBarsM5arr[0][0].date)

    # saveHisBarsM3 = False
    # if(saveHisBarsM3):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM3 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='60 D',
    #             barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM3)<6):
    #             print("timeout")
    #             hisBarsM3 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='60 D',
    #             barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM3 = hisBarsM3[::-1]
    #         print(backtestTime,hisBarsM3[0].date)
    #         hisBarsM3arr.append(hisBarsM3)
    #         print("data get")

    #     pickle.dump(hisBarsM3arr, open("./pickle/hisBarsM3arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM3arr = pickle.load(open("./pickle/hisBarsM3arr.p", "rb"))
    #     print(hisBarsM3arr[0][0].date)

    # saveHisBarsM2 = False
    # if(saveHisBarsM2):
    #     for trade in trades:
    #         symbol = trade['symbol']
    #         backtestTime = trade['time']
    #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    #         opEndTime = ''
    #         contract= Stock(symbol, 'SMART', 'USD')

    #         hisBarsM2 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='30 D',
    #             barSizeSetting='2 mins', whatToShow='ASK', useRTH=True)

    #         while(len(hisBarsM2)<6):
    #             print("timeout")
    #             hisBarsM2 = ib.reqHistoricalData(
    #             contract, endDateTime=backtestTime, durationStr='30 D',
    #             barSizeSetting='2 mins', whatToShow='ASK', useRTH=True)

    #         hisBarsM2 = hisBarsM2[::-1]
    #         print(backtestTime,hisBarsM2[0].date)
    #         hisBarsM2arr.append(hisBarsM2)
    #         print("data get")

    #     pickle.dump(hisBarsM2arr, open("./pickle/hisBarsM2arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsM2arr = pickle.load(open("./pickle/hisBarsM2arr.p", "rb"))
    #     print(hisBarsM2arr[0][0].date)

    end = dt.now()
    start = end - timedelta(days=50)

    tradeSymList = []

    # drop duplicat sym for req data from yahoo
    for trade in trades:
        symbol = trade['symbol']
        if symbol not in tradeSymList:
            tradeSymList.append(symbol)

    tradableList = []
    fetchTradableList = False
    if(fetchTradableList):
        for symbol in tradeSymList:
            dataReader = web.get_quote_yahoo(symbol)
            marketCap = 0
            if('marketCap' in dataReader):
                marketCap = dataReader['marketCap'][0]
            # if(marketCap < 21744275): continue
            if(marketCap < 1): continue
            volDf = web.DataReader(symbol, "yahoo", start, end)
            volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
            # if(volavg < 1987664): continue
            if(volavg < 1): continue
            tradableList.append({
                'symbol': symbol,
                'marketCap': marketCap,
                'volavg': volavg
            })
        print(tradableList)
    else:
        tradableList = [
            {
                "symbol":"DRIO",
                "marketCap":252887872,
                "volavg":227373.33333333334
            },
            {
                "symbol":"AFIB",
                "marketCap":457566112,
                "volavg":278543.3333333333
            },
            {
                "symbol":"BFLY",
                "marketCap":2247645696,
                "volavg":2610820.0
            },
            {
                "symbol":"SUMR",
                "marketCap":27497594,
                "volavg":67036.66666666667
            },
            {
                "symbol":"BCEL",
                "marketCap":332756832,
                "volavg":214113.33333333334
            },
            {
                "symbol":"HOL",
                "marketCap":378750016,
                "volavg":779256.6666666666
            },
            {
                "symbol":"DLPN",
                "marketCap":65102912,
                "volavg":1693600.0
            },
            {
                "symbol":"TUR",
                "marketCap":358854496,
                "volavg":278833.3333333333
            },
            {
                "symbol":"FNKO",
                "marketCap":1309415680,
                "volavg":1225486.6666666667
            },
            {
                "symbol":"PRTA",
                "marketCap":1283835904,
                "volavg":299430.0
            },
            {
                "symbol":"LUMO",
                "marketCap":87321344,
                "volavg":25276.666666666668
            },
            {
                "symbol":"CERT",
                "marketCap":4024877568,
                "volavg":501573.3333333333
            },
            {
                "symbol":"WAFU",
                "marketCap":30973882,
                "volavg":620250.0
            },
            {
                "symbol":"TLS",
                "marketCap":2192277248,
                "volavg":717316.6666666666
            },
            {
                "symbol":"X",
                "marketCap":6992309760,
                "volavg":24911243.333333332
            },
            {
                "symbol":"HGEN",
                "marketCap":1186625024,
                "volavg":1363226.6666666667
            },
            {
                "symbol":"GTH",
                "marketCap":1881413760,
                "volavg":282583.3333333333
            },
            {
                "symbol":"QURE",
                "marketCap":1594964864,
                "volavg":409193.3333333333
            },
            {
                "symbol":"IQ",
                "marketCap":11255203840,
                "volavg":14975030.0
            },
            {
                "symbol":"ORPH",
                "marketCap":202409200,
                "volavg":15406.666666666666
            },
            {
                "symbol":"ING",
                "marketCap":54260740096,
                "volavg":5301096.666666667
            },
            {
                "symbol":"GP",
                "marketCap":345776096,
                "volavg":159440.0
            },
            {
                "symbol":"CAN",
                "marketCap":1328443136,
                "volavg":8109560.0
            },
            {
                "symbol":"ABCL",
                "marketCap":7268944896,
                "volavg":882190.0
            },
            {
                "symbol":"TIGR",
                "marketCap":3239165696,
                "volavg":8075886.666666667
            },
            {
                "symbol":"VLDR",
                "marketCap":1830460160,
                "volavg":3364056.6666666665
            },
            {
                "symbol":"BOWX",
                "marketCap":741404992,
                "volavg":654310.0
            },
            {
                "symbol":"STLA",
                "marketCap":61141372928,
                "volavg":2691123.3333333335
            },
            {
                "symbol":"TME",
                "marketCap":26641051648,
                "volavg":19764970.0
            },
            {
                "symbol":"VIPS",
                "marketCap":15697612800,
                "volavg":13328890.0
            },
            {
                "symbol":"HYLN",
                "marketCap":1805019008,
                "volavg":4331443.333333333
            },
            {
                "symbol":"VERY",
                "marketCap":134767504,
                "volavg":22476.666666666668
            },
            {
                "symbol":"RICE",
                "marketCap":466829504,
                "volavg":237140.0
            },
            {
                "symbol":"FTCV",
                "marketCap":371609440,
                "volavg":614800.0
            },
            {
                "symbol":"ALLT",
                "marketCap":686815296,
                "volavg":169020.0
            },
            {
                "symbol":"KZIA",
                "marketCap":124400312,
                "volavg":58433.333333333336
            },
            {
                "symbol":"AGC",
                "marketCap":736875008,
                "volavg":1416390.0
            },
            {
                "symbol":"GROW",
                "marketCap":93708032,
                "volavg":341450.0
            },
            {
                "symbol":"MUDS",
                "marketCap":539600896,
                "volavg":3507273.3333333335
            },
            {
                "symbol":"EVLO",
                "marketCap":716277760,
                "volavg":157590.0
            },
            {
                "symbol":"AFMD",
                "marketCap":1055113088,
                "volavg":1992766.6666666667
            },
            {
                "symbol":"TIRX",
                "marketCap":80588496,
                "volavg":2574583.3333333335
            },
            {
                "symbol":"MFNC",
                "marketCap":228732672,
                "volavg":95316.66666666667
            },
            {
                "symbol":"INO",
                "marketCap":1572710400,
                "volavg":8469566.666666666
            },
            {
                "symbol":"GSK",
                "marketCap":95853395968,
                "volavg":3992153.3333333335
            },
            {
                "symbol":"INFY",
                "marketCap":81624276992,
                "volavg":5427043.333333333
            },
            {
                "symbol":"CRCT",
                "marketCap":7475529728,
                "volavg":882640.0
            },
            {
                "symbol":"HOG",
                "marketCap":7428076544,
                "volavg":2783890.0
            },
            {
                "symbol":"SBLK",
                "marketCap":1936166528,
                "volavg":2076710.0
            },
            {
                "symbol":"NNDM",
                "marketCap":1766636160,
                "volavg":19362800.0
            },
            {
                "symbol":"SLV",
                "marketCap":8843554816,
                "volavg":24782183.333333332
            },
            {
                "symbol":"SKLZ",
                "marketCap":6726391808,
                "volavg":27060533.333333332
            },
            {
                "symbol":"RHE",
                "marketCap":20343052,
                "volavg":9296726.666666666
            },
            {
                "symbol":"FSLY",
                "marketCap":5458231296,
                "volavg":5295556.666666667
            },
            {
                "symbol":"MVIS",
                "marketCap":2464051200,
                "volavg":41417633.333333336
            },
            {
                "symbol":"M",
                "marketCap":5698168832,
                "volavg":15768986.666666666
            },
            {
                "symbol":"CLF",
                "marketCap":10047968256,
                "volavg":24163103.333333332
            },
            {
                "symbol":"AA",
                "marketCap":7394844160,
                "volavg":6818473.333333333
            },
            {
                "symbol":"VALE",
                "marketCap":110414823424,
                "volavg":32629186.666666668
            },
            {
                "symbol":"CUE",
                "marketCap":437391520,
                "volavg":701630.0
            },
            {
                "symbol":"T",
                "marketCap":210130190336,
                "volavg":55475246.666666664
            },
            {
                "symbol":"PRTY",
                "marketCap":1027012800,
                "volavg":3339010.0
            },
            {
                "symbol":"GOLD",
                "marketCap":42869145600,
                "volavg":16722826.666666666
            },
            {
                "symbol":"ET",
                "marketCap":26764550144,
                "volavg":19754410.0
            },
            {
                "symbol":"GGB",
                "marketCap":9986937856,
                "volavg":23106310.0
            },
            {
                "symbol":"SLB",
                "marketCap":43809677312,
                "volavg":13460740.0
            },
            {
                "symbol":"DVN",
                "marketCap":17978064896,
                "volavg":10530423.333333334
            },
            {
                "symbol":"TLRY",
                "marketCap":5280972800,
                "volavg":24492350.0
            },
            {
                "symbol":"JMIA",
                "marketCap":2877917952,
                "volavg":7100496.666666667
            },
            {
                "symbol":"AMC",
                "marketCap":11761313792,
                "volavg":127067256.66666667
            },
            {
                "symbol":"WFC",
                "marketCap":193473134592,
                "volavg":26819176.666666668
            },
            {
                "symbol":"XLF",
                "marketCap":33562077184,
                "volavg":48929166.666666664
            },
            {
                "symbol":"BAC",
                "marketCap":363253465088,
                "volavg":40778586.666666664
            },
            {
                "symbol":"PLUG",
                "marketCap":18103298048,
                "volavg":39983003.333333336
            },
            {
                "symbol":"F",
                "marketCap":57998528512,
                "volavg":89647013.33333333
            },
            {
                "symbol":"UBER",
                "marketCap":94917910528,
                "volavg":23346823.333333332
            },
            {
                "symbol":"AAL",
                "marketCap":15547122688,
                "volavg":36053233.333333336
            },
            {
                "symbol":"FCEL",
                "marketCap":3166252544,
                "volavg":24049866.666666668
            },
            {
                "symbol":"FSR",
                "marketCap":3903836928,
                "volavg":19316080.0
            },
            {
                "symbol":"LEDS",
                "marketCap":56079072,
                "volavg":11962370.0
            },
            {
                "symbol":"FUBO",
                "marketCap":3336087296,
                "volavg":14403013.333333334
            },
            {
                "symbol":"NIO",
                "marketCap":63279644672,
                "volavg":74499686.66666667
            },
            {
                "symbol":"CLOV",
                "marketCap":3104246528,
                "volavg":25111526.666666668
            },
            {
                "symbol":"UWMC",
                "marketCap":14269962240,
                "volavg":5955783.333333333
            },
            {
                "symbol":"NVVE",
                "marketCap":199138576,
                "volavg":1034080.0
            },
            {
                "symbol":"FF",
                "marketCap":449242688,
                "volavg":431593.3333333333
            },
            {
                "symbol":"SM",
                "marketCap":2344180224,
                "volavg":3626293.3333333335
            },
            {
                "symbol":"MGM",
                "marketCap":21029277696,
                "volavg":8107836.666666667
            },
            {
                "symbol":"PDSB",
                "marketCap":271795264,
                "volavg":2121333.3333333335
            },
            {
                "symbol":"MOXC",
                "marketCap":205655904,
                "volavg":2247053.3333333335
            },
            {
                "symbol":"TAK",
                "marketCap":54037041152,
                "volavg":2147040.0
            },
            {
                "symbol":"REAL",
                "marketCap":1586045312,
                "volavg":3000426.6666666665
            },
            {
                "symbol":"PRVB",
                "marketCap":482281472,
                "volavg":3363710.0
            },
            {
                "symbol":"GTX",
                "marketCap":601210688,
                "volavg":497093.23333333334
            },
            {
                "symbol":"DOYU",
                "marketCap":2562838784,
                "volavg":2541040.0
            },
            {
                "symbol":"HRTX",
                "marketCap":1216521984,
                "volavg":2204240.0
            },
            {
                "symbol":"OCGN",
                "marketCap":1642697856,
                "volavg":103634946.66666667
            },
            {
                "symbol":"ZH",
                "marketCap":5227612160,
                "volavg":1531333.3333333333
            },
            {
                "symbol":"AMWL",
                "marketCap":2993353472,
                "volavg":3958663.3333333335
            },
            {
                "symbol":"BTBT",
                "marketCap":408311584,
                "volavg":1877383.3333333333
            },
            {
                "symbol":"KODK",
                "marketCap":558944960,
                "volavg":2294893.3333333335
            },
            {
                "symbol":"WKEY",
                "marketCap":161405216,
                "volavg":865383.3333333334
            },
            {
                "symbol":"WNW",
                "marketCap":178500000,
                "volavg":529630.0
            },
            {
                "symbol":"AEVA",
                "marketCap":2059779840,
                "volavg":1397393.3333333333
            },
            {
                "symbol":"CLVS",
                "marketCap":536418464,
                "volavg":3986180.0
            },
            {
                "symbol":"BPTH",
                "marketCap":39603084,
                "volavg":185020.0
            },
            {
                "symbol":"AMR",
                "marketCap":365207552,
                "volavg":190040.0
            }
            ]
    # df = pd.read_csv (r'./fillter.csv')
    df = pd.read_csv (r'./fillter_all.csv')
    df.drop
    fillters = json.loads(df.to_json(orient = 'records'))

    marketCapLimitArr = []
    volavgLimitArr = []
    for fillter in fillters:
        if(fillter['marketCap'] != None and fillter['marketCap'] > 0):
            marketCapLimitArr.append(
                int(fillter['marketCap'])
                ) 
        if(fillter['volavg'] != None and fillter['volavg']>0):
            volavgLimitArr.append(int(fillter['volavg']))

    marketCapLimitArr.reverse()
    volavgLimitArr.reverse()

    total = 0
    net = 0
    win = 0
    loss = 0
    totalNetProfit = 0
    totalNetLoss = 0
    a = 0
    for trade in trades:
        a += 1
        symbol = trade['symbol']
        if not list(filter(lambda x:x["symbol"]== symbol,tradableList)): continue
        marketCap = 0
        volavg = 0
        for sym in tradableList:
            if(symbol == sym['symbol']):
                marketCap = float(sym['marketCap'])
                volavg = float(sym['volavg'])
                # tpVal = volavg/175751849.851#1563121.35747
                # tpVal = marketCap/175751849.851
                tpVal = marketCap/188785133.098#175751849.851
                if(tpVal<20.189): tpVal=20.189

        # if(symbol == 'AMC'): continue
        
        marketCapLimit = 178499997
        volavgLimit = 922216
        if(marketCap < marketCapLimit): continue
        if(volavg < volavgLimit): continue

        backtestTime = trade['time']
        op = trade['op']
        if(op>13.60 and op < 50): continue
        sl = trade['sl']
        # tp = trade['tp']
        tp = op+(op-sl)*tpVal
        trade['tp'] = tp
        vol = trade['vol']
        trade['result'] = ''
        trade['total'] = 0
        if(vol<3): continue
        backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

        opEndTime = ''

        hisBarsQQQ = tradeHisBarsQQQarr[a-1]
        hisBarsD1 = hisBarsD1arr[a-1]
        # hisBarsH8 = hisBarsH8arr[a-1]
        # hisBarsH4 = hisBarsH4arr[a-1]
        # hisBarsH3 = hisBarsH3arr[a-1]
        # hisBarsH2 = hisBarsH2arr[a-1]
        # hisBarsH1 = hisBarsH1arr[a-1]
        # hisBarsM30 = hisBarsM30arr[a-1]
        # hisBarsM20 = hisBarsM20arr[a-1]
        # hisBarsM15 = hisBarsM15arr[a-1]
        # hisBarsM10 = hisBarsM10arr[a-1]
        # hisBarsM5 = hisBarsM5arr[a-1]
        # hisBarsM3 = hisBarsM3arr[a-1]
        # hisBarsM2 = hisBarsM2arr[a-1]

        sma25QQQ = sum(map(lambda x: x.close, hisBarsQQQ[2:27]))/25
        sma25D1 = sum(map(lambda x: x.close, hisBarsD1[2:27]))/25

        if(hisBarsQQQ[1].close/sma25QQQ > 1.021):
            continue
        
        # Inside day
        if(
            hisBarsQQQ[1].close < hisBarsQQQ[1].open
            and hisBarsQQQ[0].open > hisBarsQQQ[1].low
            and hisBarsQQQ[0].open < hisBarsQQQ[1].high
            and hisBarsQQQ[0].open 
                < hisBarsQQQ[1].low + (hisBarsQQQ[1].high
                                            -hisBarsQQQ[1].low) * 0.88
        ): continue


        if(hisBarsQQQ[0].open > hisBarsQQQ[1].close * 1.014):
            continue

        # Relative strength
        if(
            (hisBarsQQQ[1].close > hisBarsQQQ[1].open
            and hisBarsD1[1].close < hisBarsD1[1].open)
            or
            (hisBarsQQQ[1].close > hisBarsQQQ[3].open
            and hisBarsD1[1].close < hisBarsD1[3].open)
        ): continue

        # Previous day inside bar
        if(
            (hisBarsD1[1].high < hisBarsD1[2].high
            and hisBarsD1[1].low > hisBarsD1[2].low)
        ): continue

        plotLinesRes = plotLines(hisBarsQQQ)
        if(plotLinesRes < 0):
            continue
        plotLinesRes = plotLines(hisBarsD1)
        if(plotLinesRes < 0):
            continue

        # entry
        res = 0

        bias = (hisBarsD1[1].close-sma25D1)/sma25D1
        bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

        biasval = 0.0482831585
        if (bias < -biasval and bias2 < -biasval):
            res += 1

        x = 1
        while(x < 17):
            if (hisBarsD1[x*2+1].close < hisBarsD1[x*3].open
                and hisBarsD1[x+1].close < hisBarsD1[x*2].open
                and hisBarsD1[1].close > hisBarsD1[1].open):
                res += 1
            x += 1

        ATR = ((hisBarsD1[1].high - hisBarsD1[1].low) +
                (hisBarsD1[2].high - hisBarsD1[2].low) +
                (hisBarsD1[3].high - hisBarsD1[3].low) +
                (hisBarsD1[4].high - hisBarsD1[4].low) +
                (hisBarsD1[5].high - hisBarsD1[5].low)) / 5
        currentLongRange = hisBarsD1[1].close - hisBarsD1[0].open
        # k = 1
        # while(k <= 3):
        #     signalCandleClose3 = hisBarsD1[k*2+1].close
        #     signalCandleOpen3 = hisBarsD1[k*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsD1[k*4].high - hisBarsD1[k*4].low
        #     endCandleRange3 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 6.054347826086946):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsD1[k+1].close - hisBarsD1[k*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsD1[2].high < hisBarsD1[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsD1[1].close < hisBarsD1[1].open):
        #                 if (hisBarsD1[1].high - hisBarsD1[1].close
        #                     > (hisBarsD1[1].high - hisBarsD1[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(k<2):
        #         signalCandleClose4 = hisBarsD1[k*3+1].close
        #         signalCandleOpen4 = hisBarsD1[k*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsD1[k*5].high - hisBarsD1[k*5].low
        #         endCandleRange4 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsD1[k*2+1].close - hisBarsD1[k*3].open) < bigCandleRange4
        #                 and abs(hisBarsD1[k+1].close - hisBarsD1[k*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsD1[1].close < hisBarsD1[1].open):
        #                     if (hisBarsD1[1].high - hisBarsD1[1].close
        #                             > (hisBarsD1[1].high - hisBarsD1[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     k += 1

        # l = 1
        # while(l <= 3):
        #     signalCandleClose3 = hisBarsH8[l*2+1].close
        #     signalCandleOpen3 = hisBarsH8[l*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsH8[l*4].high - hisBarsH8[l*4].low
        #     endCandleRange3 = abs(hisBarsH8[1].close - hisBarsH8[l].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 6.054347826086946):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsH8[l+1].close - hisBarsH8[l*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsH8[2].high < hisBarsH8[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsH8[1].close < hisBarsH8[1].open):
        #                 if (hisBarsH8[1].high - hisBarsH8[1].close
        #                     > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(l<2):
        #         signalCandleClose4 = hisBarsH8[l*3+1].close
        #         signalCandleOpen4 = hisBarsH8[l*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsH8[l*5].high - hisBarsH8[l*5].low
        #         endCandleRange4 = abs(hisBarsH8[1].close - hisBarsH8[l].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsH8[l*2+1].close - hisBarsH8[l*3].open) < bigCandleRange4
        #                 and abs(hisBarsH8[l+1].close - hisBarsH8[l*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsH8[1].close < hisBarsH8[1].open):
        #                     if (hisBarsH8[1].high - hisBarsH8[1].close
        #                             > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     l += 1

        # m = 1
        # while(m <= 1):
        #     signalCandleClose3 = hisBarsH4[m*2+1].close
        #     signalCandleOpen3 = hisBarsH4[m*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsH4[m*4].high - hisBarsH4[m*4].low
        #     endCandleRange3 = abs(hisBarsH4[1].close - hisBarsH4[m].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsH4[m+1].close - hisBarsH4[m*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsH4[2].high < hisBarsH4[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsH4[1].close < hisBarsH4[1].open):
        #                 if (hisBarsH4[1].high - hisBarsH4[1].close
        #                     > (hisBarsH4[1].high - hisBarsH4[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(m<2):
        #         signalCandleClose4 = hisBarsH4[m*3+1].close
        #         signalCandleOpen4 = hisBarsH4[m*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsH4[m*5].high - hisBarsH4[m*5].low
        #         endCandleRange4 = abs(hisBarsH4[1].close - hisBarsH4[m].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsH4[m*2+1].close - hisBarsH4[m*3].open) < bigCandleRange4
        #                 and abs(hisBarsH4[m+1].close - hisBarsH4[m*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsH4[1].close < hisBarsH4[1].open):
        #                     if (hisBarsH4[1].high - hisBarsH4[1].close
        #                             > (hisBarsH4[1].high - hisBarsH4[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     m += 1

        # n = 1
        # while(n <= 1):
        #     signalCandleClose3 = hisBarsH3[n*2+1].close
        #     signalCandleOpen3 = hisBarsH3[n*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsH3[n*4].high - hisBarsH3[n*4].low
        #     endCandleRange3 = abs(hisBarsH3[1].close - hisBarsH3[n].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsH3[n+1].close - hisBarsH3[n*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsH3[2].high < hisBarsH3[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsH3[1].close < hisBarsH3[1].open):
        #                 if (hisBarsH3[1].high - hisBarsH3[1].close
        #                     > (hisBarsH3[1].high - hisBarsH3[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(n<2):
        #         signalCandleClose4 = hisBarsH3[n*3+1].close
        #         signalCandleOpen4 = hisBarsH3[n*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsH3[n*5].high - hisBarsH3[n*5].low
        #         endCandleRange4 = abs(hisBarsH3[1].close - hisBarsH3[n].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsH3[n*2+1].close - hisBarsH3[n*3].open) < bigCandleRange4
        #                 and abs(hisBarsH3[n+1].close - hisBarsH3[n*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsH3[1].close < hisBarsH3[1].open):
        #                     if (hisBarsH3[1].high - hisBarsH3[1].close
        #                             > (hisBarsH3[1].high - hisBarsH3[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     n += 1

        # o = 1
        # while(o <= 1):
        #     signalCandleClose3 = hisBarsH2[o*2+1].close
        #     signalCandleOpen3 = hisBarsH2[o*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsH2[o*4].high - hisBarsH2[o*4].low
        #     endCandleRange3 = abs(hisBarsH2[1].close - hisBarsH2[o].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsH2[o+1].close - hisBarsH2[o*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsH2[2].high < hisBarsH2[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsH2[1].close < hisBarsH2[1].open):
        #                 if (hisBarsH2[1].high - hisBarsH2[1].close
        #                     > (hisBarsH2[1].high - hisBarsH2[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(o<2):
        #         signalCandleClose4 = hisBarsH2[o*3+1].close
        #         signalCandleOpen4 = hisBarsH2[o*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsH2[o*5].high - hisBarsH2[o*5].low
        #         endCandleRange4 = abs(hisBarsH2[1].close - hisBarsH2[o].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsH2[o*2+1].close - hisBarsH2[o*3].open) < bigCandleRange4
        #                 and abs(hisBarsH2[o+1].close - hisBarsH2[o*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsH2[1].close < hisBarsH2[1].open):
        #                     if (hisBarsH2[1].high - hisBarsH2[1].close
        #                             > (hisBarsH2[1].high - hisBarsH2[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     o += 1

        # p = 1
        # while(p <= 1):
        #     signalCandleClose3 = hisBarsH1[p*2+1].close
        #     signalCandleOpen3 = hisBarsH1[p*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsH1[p*4].high - hisBarsH1[p*4].low
        #     endCandleRange3 = abs(hisBarsH1[1].close - hisBarsH1[p].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsH1[p+1].close - hisBarsH1[p*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsH1[2].high < hisBarsH1[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsH1[1].close < hisBarsH1[1].open):
        #                 if (hisBarsH1[1].high - hisBarsH1[1].close
        #                     > (hisBarsH1[1].high - hisBarsH1[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(p<2):
        #         signalCandleClose4 = hisBarsH1[p*3+1].close
        #         signalCandleOpen4 = hisBarsH1[p*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsH1[p*5].high - hisBarsH1[p*5].low
        #         endCandleRange4 = abs(hisBarsH1[1].close - hisBarsH1[p].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsH1[p*2+1].close - hisBarsH1[p*3].open) < bigCandleRange4
        #                 and abs(hisBarsH1[p+1].close - hisBarsH1[p*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsH1[1].close < hisBarsH1[1].open):
        #                     if (hisBarsH1[1].high - hisBarsH1[1].close
        #                             > (hisBarsH1[1].high - hisBarsH1[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     p += 1

        # q = 1
        # while(q <= 1):
        #     signalCandleClose3 = hisBarsM30[q*2+1].close
        #     signalCandleOpen3 = hisBarsM30[q*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM30[q*4].high - hisBarsM30[q*4].low
        #     endCandleRange3 = abs(hisBarsM30[1].close - hisBarsM30[q].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM30[q+1].close - hisBarsM30[q*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM30[2].high < hisBarsM30[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM30[1].close < hisBarsM30[1].open):
        #                 if (hisBarsM30[1].high - hisBarsM30[1].close
        #                     > (hisBarsM30[1].high - hisBarsM30[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(q<2):
        #         signalCandleClose4 = hisBarsM30[q*3+1].close
        #         signalCandleOpen4 = hisBarsM30[q*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM30[q*5].high - hisBarsM30[q*5].low
        #         endCandleRange4 = abs(hisBarsM30[1].close - hisBarsM30[q].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM30[q*2+1].close - hisBarsM30[q*3].open) < bigCandleRange4
        #                 and abs(hisBarsM30[q+1].close - hisBarsM30[q*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM30[1].close < hisBarsM30[1].open):
        #                     if (hisBarsM30[1].high - hisBarsM30[1].close
        #                             > (hisBarsM30[1].high - hisBarsM30[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     q += 1

        # r = 1
        # while(r <= 1):
        #     signalCandleClose3 = hisBarsM20[r*2+1].close
        #     signalCandleOpen3 = hisBarsM20[r*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM20[r*4].high - hisBarsM20[r*4].low
        #     endCandleRange3 = abs(hisBarsM20[1].close - hisBarsM20[r].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM20[r+1].close - hisBarsM20[r*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM20[2].high < hisBarsM20[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM20[1].close < hisBarsM20[1].open):
        #                 if (hisBarsM20[1].high - hisBarsM20[1].close
        #                     > (hisBarsM20[1].high - hisBarsM20[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(r<2):
        #         signalCandleClose4 = hisBarsM20[r*3+1].close
        #         signalCandleOpen4 = hisBarsM20[r*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM20[r*5].high - hisBarsM20[r*5].low
        #         endCandleRange4 = abs(hisBarsM20[1].close - hisBarsM20[r].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM20[r*2+1].close - hisBarsM20[r*3].open) < bigCandleRange4
        #                 and abs(hisBarsM20[r+1].close - hisBarsM20[r*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM20[1].close < hisBarsM20[1].open):
        #                     if (hisBarsM20[1].high - hisBarsM20[1].close
        #                             > (hisBarsM20[1].high - hisBarsM20[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     r += 1

        # s = 1
        # while(s <= 1):
        #     signalCandleClose3 = hisBarsM20[s*2+1].close
        #     signalCandleOpen3 = hisBarsM20[s*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM20[s*4].high - hisBarsM20[s*4].low
        #     endCandleRange3 = abs(hisBarsM20[1].close - hisBarsM20[s].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM20[s+1].close - hisBarsM20[s*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM20[2].high < hisBarsM20[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM20[1].close < hisBarsM20[1].open):
        #                 if (hisBarsM20[1].high - hisBarsM20[1].close
        #                     > (hisBarsM20[1].high - hisBarsM20[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(s<2):
        #         signalCandleClose4 = hisBarsM20[s*3+1].close
        #         signalCandleOpen4 = hisBarsM20[s*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM20[s*5].high - hisBarsM20[s*5].low
        #         endCandleRange4 = abs(hisBarsM20[1].close - hisBarsM20[s].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM20[s*2+1].close - hisBarsM20[s*3].open) < bigCandleRange4
        #                 and abs(hisBarsM20[s+1].close - hisBarsM20[s*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM20[1].close < hisBarsM20[1].open):
        #                     if (hisBarsM20[1].high - hisBarsM20[1].close
        #                             > (hisBarsM20[1].high - hisBarsM20[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     s += 1

        # t = 1
        # while(t <= 1):
        #     signalCandleClose3 = hisBarsM15[t*2+1].close
        #     signalCandleOpen3 = hisBarsM15[t*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM15[t*4].high - hisBarsM15[t*4].low
        #     endCandleRange3 = abs(hisBarsM15[1].close - hisBarsM15[t].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM15[t+1].close - hisBarsM15[t*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM15[2].high < hisBarsM15[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM15[1].close < hisBarsM15[1].open):
        #                 if (hisBarsM15[1].high - hisBarsM15[1].close
        #                     > (hisBarsM15[1].high - hisBarsM15[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(t<2):
        #         signalCandleClose4 = hisBarsM15[t*3+1].close
        #         signalCandleOpen4 = hisBarsM15[t*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM15[t*5].high - hisBarsM15[t*5].low
        #         endCandleRange4 = abs(hisBarsM15[1].close - hisBarsM15[t].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM15[t*2+1].close - hisBarsM15[t*3].open) < bigCandleRange4
        #                 and abs(hisBarsM15[t+1].close - hisBarsM15[t*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM15[1].close < hisBarsM15[1].open):
        #                     if (hisBarsM15[1].high - hisBarsM15[1].close
        #                             > (hisBarsM15[1].high - hisBarsM15[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     t += 1

        # u = 1
        # while(u <= 1):
        #     signalCandleClose3 = hisBarsM10[u*2+1].close
        #     signalCandleOpen3 = hisBarsM10[u*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM10[u*4].high - hisBarsM10[u*4].low
        #     endCandleRange3 = abs(hisBarsM10[1].close - hisBarsM10[u].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM10[u+1].close - hisBarsM10[u*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM10[2].high < hisBarsM10[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM10[1].close < hisBarsM10[1].open):
        #                 if (hisBarsM10[1].high - hisBarsM10[1].close
        #                     > (hisBarsM10[1].high - hisBarsM10[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(u<2):
        #         signalCandleClose4 = hisBarsM10[u*3+1].close
        #         signalCandleOpen4 = hisBarsM10[u*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM10[u*5].high - hisBarsM10[u*5].low
        #         endCandleRange4 = abs(hisBarsM10[1].close - hisBarsM10[u].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM10[u*2+1].close - hisBarsM10[u*3].open) < bigCandleRange4
        #                 and abs(hisBarsM10[u+1].close - hisBarsM10[u*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM10[1].close < hisBarsM10[1].open):
        #                     if (hisBarsM10[1].high - hisBarsM10[1].close
        #                             > (hisBarsM10[1].high - hisBarsM10[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     u += 1

        # v = 1
        # while(v <= 1):
        #     signalCandleClose3 = hisBarsM5[v*2+1].close
        #     signalCandleOpen3 = hisBarsM5[v*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM5[v*4].high - hisBarsM5[v*4].low
        #     endCandleRange3 = abs(hisBarsM5[1].close - hisBarsM5[v].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM5[v+1].close - hisBarsM5[v*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM5[2].high < hisBarsM5[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM5[1].close < hisBarsM5[1].open):
        #                 if (hisBarsM5[1].high - hisBarsM5[1].close
        #                     > (hisBarsM5[1].high - hisBarsM5[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(v<2):
        #         signalCandleClose4 = hisBarsM5[v*3+1].close
        #         signalCandleOpen4 = hisBarsM5[v*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM5[v*5].high - hisBarsM5[v*5].low
        #         endCandleRange4 = abs(hisBarsM5[1].close - hisBarsM5[v].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM5[v*2+1].close - hisBarsM5[v*3].open) < bigCandleRange4
        #                 and abs(hisBarsM5[v+1].close - hisBarsM5[v*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM5[1].close < hisBarsM5[1].open):
        #                     if (hisBarsM5[1].high - hisBarsM5[1].close
        #                             > (hisBarsM5[1].high - hisBarsM5[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     v += 1

        # w = 1
        # while(w <= 1):
        #     signalCandleClose3 = hisBarsM3[w*2+1].close
        #     signalCandleOpen3 = hisBarsM3[w*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM3[w*4].high - hisBarsM3[w*4].low
        #     endCandleRange3 = abs(hisBarsM3[1].close - hisBarsM3[w].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM3[w+1].close - hisBarsM3[w*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM3[2].high < hisBarsM3[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM3[1].close < hisBarsM3[1].open):
        #                 if (hisBarsM3[1].high - hisBarsM3[1].close
        #                     > (hisBarsM3[1].high - hisBarsM3[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(w<2):
        #         signalCandleClose4 = hisBarsM3[w*3+1].close
        #         signalCandleOpen4 = hisBarsM3[w*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM3[w*5].high - hisBarsM3[w*5].low
        #         endCandleRange4 = abs(hisBarsM3[1].close - hisBarsM3[w].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM3[w*2+1].close - hisBarsM3[w*3].open) < bigCandleRange4
        #                 and abs(hisBarsM3[w+1].close - hisBarsM3[w*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM3[1].close < hisBarsM3[1].open):
        #                     if (hisBarsM3[1].high - hisBarsM3[1].close
        #                             > (hisBarsM3[1].high - hisBarsM3[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     w += 1

        # x = 1
        # while(x <= 1):
        #     signalCandleClose3 = hisBarsM2[x*2+1].close
        #     signalCandleOpen3 = hisBarsM2[x*3].open
        #     bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #     smallCandleRange3 = hisBarsM2[x*4].high - hisBarsM2[x*4].low
        #     endCandleRange3 = abs(hisBarsM2[1].close - hisBarsM2[x].open)

        #     if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
        #         if (signalCandleClose3 > signalCandleOpen3
        #             and abs(hisBarsM2[x+1].close - hisBarsM2[x*2].open) < bigCandleRange3
        #             and endCandleRange3 < bigCandleRange3*0.5
        #             and hisBarsM2[2].high < hisBarsM2[3].high
        #             and currentLongRange < ATR/4):
        #             if (hisBarsM2[1].close < hisBarsM2[1].open):
        #                 if (hisBarsM2[1].high - hisBarsM2[1].close
        #                     > (hisBarsM2[1].high - hisBarsM2[1].low)*0.13):
        #                     res += 1
        #             else:
        #                 res += 1

        #     if(x<2):
        #         signalCandleClose4 = hisBarsM2[x*3+1].close
        #         signalCandleOpen4 = hisBarsM2[x*4].open
        #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #         smallCandleRange4 = hisBarsM2[x*5].high - hisBarsM2[x*5].low
        #         endCandleRange4 = abs(hisBarsM2[1].close - hisBarsM2[x].open)

        #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
        #             if (signalCandleClose4 > signalCandleOpen4
        #                 and abs(hisBarsM2[x*2+1].close - hisBarsM2[x*3].open) < bigCandleRange4
        #                 and abs(hisBarsM2[x+1].close - hisBarsM2[x*2].open) < bigCandleRange4
        #                 and endCandleRange4 < bigCandleRange4*0.5
        #                     and currentLongRange < ATR/4):
        #                 if (hisBarsM2[1].close < hisBarsM2[1].open):
        #                     if (hisBarsM2[1].high - hisBarsM2[1].close
        #                             > (hisBarsM2[1].high - hisBarsM2[1].low)*0.13):
        #                         res += 1
        #                 else:
        #                     res += 1
        #     x += 1

        if res < 1: continue

        hisBarsM5 = tradeHisBarsM5arr[a-1]

        opendHisBarsM5 = hisBarsM5

        endTime = hisBarsM5[-1].date
        
        trade['status'] = ''
        for i in opendHisBarsM5:
            if i.high >= op:
                trade['status'] = i.date
                break

        trade['result'] = ''
        if trade['status'] != '':
            triggeredTime = trade['status']
            for i in hisBarsM5:
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
        maxMarCapLimit = marketCapLimit
        maxVolavgLimit = volavgLimit
    print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
    print('maxMarCapLimit',str(maxMarCapLimit),'maxVolavgLimit',str(maxVolavgLimit))
                    
    df = pd.DataFrame(trades)
    df.to_csv('./trades_status.csv')
except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)