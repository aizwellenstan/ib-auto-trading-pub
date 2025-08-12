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

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=9)

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)

day = ib.reqCurrentTime().day
risk = 0.06
if(day==5): risk*=0.98

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

df = pd.read_csv (r'./csv/trades.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))

fillterDf = pd.read_csv (r'./csv/sector.csv', index_col=0)
fillterDf.drop
fillterSymLst = json.loads(fillterDf.to_json(orient = 'records'))
sectorLst = fillterDf.groupby('sector')['symbol'].apply(list)

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
        pickle.dump(hisBarsQQQD1arr, open("./pickle/pro/hisBarsQQQD1arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsQQQD1arr = pickle.load(open("./pickle/pro/hisBarsQQQD1arr.p", "rb"))

    saveQQQM5 = False
    if(saveQQQM5):
        contractQQQ = Stock("QQQ", 'SMART', 'USD')
        hisBarsQQQM5 = ib.reqHistoricalData(
            contractQQQ, endDateTime='', durationStr='90 D',
            barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

        while(len(hisBarsQQQM5)<6):
            print("timeout")
            hisBarsQQQM5 = ib.reqHistoricalData(
                contractQQQ, endDateTime=backtestTime, durationStr='90 D',
                barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

        hisBarsQQQM5arr = hisBarsQQQM5
        pickle.dump(hisBarsQQQM5arr, open("./pickle/pro/hisBarsQQQM5arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsQQQM5arr = pickle.load(open("./pickle/pro/hisBarsQQQM5arr.p", "rb"))

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

        pickle.dump(hisBarsStocksD1arr, open("./pickle/pro/hisBarsStocksD1arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsStocksD1arr = pickle.load(open("./pickle/pro/hisBarsStocksD1arr.p", "rb"))

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

        pickle.dump(hisBarsStocksM30arr, open("./pickle/pro/hisBarsStocksM30arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsStocksM30arr = pickle.load(open("./pickle/pro/hisBarsStocksM30arr.p", "rb"))

    hisBarsStocksM5arr = []
    saveStocksM5arr = True
    if(saveStocksM5arr):
        for symbol in fillterSymLst:
            symbol = symbol['symbol']
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM5 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='90 D',
                barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

            maxTrys = 0
            while(len(hisBarsM5)<6 and maxTrys<=20):
                print("timeout")
                hisBarsM5 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='90 D',
                    barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)
                maxTrys += 1
            
            hisBarsStocksM5arr.append(
                {
                    'symbol': symbol,
                    'data': hisBarsM5
                }
            )

        pickle.dump(hisBarsStocksM5arr, open("./pickle/pro/hisBarsStocksM5arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsStocksM5arr = pickle.load(open("./pickle/pro/hisBarsStocksM5arr.p", "rb"))

    
    

    fee = 1.001392062 * 2
    tpVal = 20.189
    maxProfit = 0 #41.07
    maxTpVal = 0
    maxMarCapLimit = 0
    maxVolavgLimit = 0

    tradeHisBarsM5arr = []
    tradeHisBarsQQQarr = []
    hisBarsD1arr = []

    total = 0
    net = 0
    win = 0
    loss = 0
    totalNetProfit = 0
    totalNetLoss = 0
    singleTrade = []
    for trade in trades:
        symbol = trade['symbol']
        if not list(filter(lambda x:x['symbol'] == symbol,fillterSymLst)): continue
        # if symbol == "AMC": continue
        backtestTime = trade['time']
        op = trade['op']
        if(op>13.60 and op < 50): continue
        if(op < 6.31): continue
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
        hisBarsM30 = list(filter(lambda x:x.date >= backtestTime,dataM30))

        hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),hisBarsQQQD1arr))
        hisBarsQQQ = hisBarsQQQD1[::-1]

        hisBarsQQQM5 = list(filter(lambda x:x.date <= backtestTime+timedelta(minutes=10),hisBarsQQQM5arr))
        hisBarsQQQM5 = hisBarsQQQM5[::-1]

        dataD1 = []
        for hisBarsStockD1 in hisBarsStocksD1arr:
            if symbol == hisBarsStockD1['symbol']:
                dataD1 = hisBarsStockD1['data']
                break

        if(len(dataD1) < 6):continue
        hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
        hisBarsD1 = hisBarsD1[::-1]

        dataM5 = []
        for hisBarsStockM5 in hisBarsStocksM5arr:
            if symbol == hisBarsStockM5['symbol']:
                dataM5 = hisBarsStockM5['data']
                break

        if(len(dataM5) < 6):continue
        hisBarsM5 = list(filter(lambda x:x.date <= backtestTime+timedelta(minutes=15),dataM5))
        hisBarsM5 = hisBarsM5[::-1]

        curSectorLst = []
        for sym in fillterSymLst:
            if sym['symbol'] == symbol:
                curSectorLst = sectorLst[sym['sector']]
        print(curSectorLst)

        print(hisBarsQQQM5[0].date, hisBarsM5[0].date, hisBarsM5[1].date)

        sma25D1 = sma(hisBarsD1[1:26], 25)
        sma5D1 = sma(hisBarsD1[1:6], 5)
        ema21 = ema(hisBarsD1[1:22], 21)

        sma25D1 = sum(map(lambda x: x.close, hisBarsD1[1:26]))/25

        res = 0
        bias = (hisBarsD1[1].close-sma25D1)/sma25D1
        bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

        # biasval = 0.0482831585
        # if (
        #     bias < -biasval 
        #     and bias2 < -biasval
        #     and hisBarsQQQ[0].open < hisBarsQQQ[1].close * 0.982
        # ):
        #     res += 1

        # if(
        #     sma5D1third < sma25D1third
        #     and sma5D1second > sma5D1third
        #     and sma5D1second < sma25D1second
        #     and sma5D1 > sma5D1second
        #     and sma5D1 > sma25D1
        # ):
        #     res += 1

        # gapVal = 1.04
        # if(
        #     hisBarsD1[4].open > hisBarsD1[5].close * 1.03
        #     and hisBarsD1[4].close > hisBarsD1[4].open
        #     and hisBarsD1[3].close < hisBarsD1[3].open
        #     and hisBarsD1[2].close < hisBarsD1[2].open
        #     and hisBarsD1[1].close > hisBarsD1[1].open
        #     and hisBarsD1[0].open > hisBarsD1[1].close * 1.03
        # ):
        #     res += 1

        # if(
        #     hisBarsD1[3].close > hisBarsD1[3].open
        #     and hisBarsD1[2].high < hisBarsD1[3].high
        #     and hisBarsD1[2].low > hisBarsD1[3].low
        # ):  res += 1

        # x = 1
        # while(x < 2):
        # if(
        #     hisBarsD1[x*3+1].close < hisBarsD1[x*4].open
        #     and hisBarsD1[x*2+1].close < hisBarsD1[x*3].open
        #     and hisBarsD1[x+1].close < hisBarsD1[x*2].open
        #     and hisBarsD1[1].close > hisBarsD1[1].open):
        #     res += 1
            # x += 1

        # if(
        #     hisBarsD1[4].close < hisBarsD1[4].open
        #     and hisBarsD1[3].close < hisBarsD1[3].open
        #     and hisBarsD1[2].close > hisBarsD1[2].open
        #     and hisBarsD1[1].close > hisBarsD1[1].open
        #     and hisBarsD1[1].close > hisBarsD1[4].open
        # ):
        #     res += 1

        hisBars = hisBarsD1
        # ATR = ((hisBars[1].high - hisBars[1].low) +
        #         (hisBars[2].high - hisBars[2].low) +
        #         (hisBars[3].high - hisBars[3].low) +
        #         (hisBars[4].high - hisBars[4].low) +
        #         (hisBars[5].high - hisBars[5].low)) / 5

        # currentLongRange = hisBars[1].close - hisBars[0].open

        # if(
        #     hisBarsD1[8].close < hisBarsD1[8].open
        #     and hisBarsD1[7].close < hisBarsD1[7].open
        #     and hisBarsD1[6].close < hisBarsD1[6].open
        #     and hisBarsD1[5].close < hisBarsD1[5].open
        #     and hisBarsD1[4].close < hisBarsD1[4].open
        #     and hisBarsD1[3].close < hisBarsD1[3].open
        #     and hisBarsD1[2].close < hisBarsD1[2].open
        #     and hisBarsD1[1].close > hisBarsD1[1].open
        #     # and hisBarsD1[0].open > hisBarsD1[1].high
        #     # and hisBarsD1[0].open > hisBarsD1[2].high
        #     # and hisBarsD1[0].open > hisBarsD1[3].high
        #     # and hisBarsD1[0].open > hisBarsD1[4].high
        #     # and hisBarsD1[0].open > hisBarsD1[5].high
        #     # and hisBarsD1[0].open > hisBarsD1[6].high
        #     # and hisBarsD1[0].open > hisBarsD1[7].high
        #     # and hisBarsD1[0].open > hisBarsD1[8].high
        #     # and hisBarsD1[0].open > hisBarsD1[9].high
        #     # and hisBarsD1[0].open > hisBarsD1[10].high
        #     # and hisBarsD1[0].open > hisBarsD1[11].high
        #     # and hisBarsD1[0].open > hisBarsD1[12].high
        #     # and hisBarsD1[0].open > hisBarsD1[13].high
        #     # and hisBarsD1[0].open > hisBarsD1[14].high
        #     # and hisBarsD1[0].open > hisBarsD1[15].high
        #     # and hisBarsD1[0].open > hisBarsD1[16].high
        #     # and hisBarsD1[0].open > hisBarsD1[17].high
        #     # and hisBarsD1[0].open > hisBarsD1[18].high
        #     # and hisBarsD1[0].open > hisBarsD1[19].high
        #     # and hisBarsD1[0].open > hisBarsD1[20].high
        #     # and hisBarsD1[0].open > hisBarsD1[21].high
        #     # and hisBarsD1[0].open > hisBarsD1[22].high
        #     # and hisBarsD1[0].open > hisBarsD1[23].high
        #     # and hisBarsD1[0].open > hisBarsD1[24].high
        #     # and hisBarsD1[0].open > hisBarsD1[25].high
        #     # and hisBarsD1[0].open > hisBarsD1[26].high
        #     # and hisBarsD1[0].open > hisBarsD1[27].high
        #     # and hisBarsD1[0].open > hisBarsD1[28].high
        #     # and hisBarsD1[0].open > hisBarsD1[29].high
        #     # and hisBarsD1[0].open > hisBarsD1[30].high
        #     # and hisBarsD1[0].open > hisBarsD1[31].high
        #     # and hisBarsD1[0].open > hisBarsD1[32].high
        #     # and hisBarsD1[0].open > hisBarsD1[33].high
        #     # and hisBarsD1[0].open > hisBarsD1[34].high
        #     # and hisBarsD1[0].open > hisBarsD1[35].high
        #     # and hisBarsD1[0].open > hisBarsD1[36].high
        #     # and hisBarsD1[0].open > hisBarsD1[37].high
        #     # and hisBarsD1[0].open > hisBarsD1[38].high
        #     # and hisBarsD1[0].open > hisBarsD1[39].high
        #     # and hisBarsD1[0].open > hisBarsD1[40].high
        #     # and hisBarsD1[0].open > hisBarsD1[41].high
        #     # and hisBarsD1[0].open > hisBarsD1[42].high
        # ):
        #     res += 1

        # k = 1
        # while(k < 5):
        #     maxUsedBar = 4
        #     if(k<27/maxUsedBar):
        #         signalCandleClose3 = hisBars[k*2+1].close
        #         signalCandleOpen3 = hisBars[k*3].open
        #         bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
        #         smallCandleRange3 = hisBars[k*4].high - hisBars[k*4].low
        #         endCandleRange3 = abs(hisBars[1].close - hisBars[k].open)

        #         if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 6.054347826086946):
        #             if (signalCandleClose3 > signalCandleOpen3
        #                 and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange3
        #                 and endCandleRange3 < bigCandleRange3*0.5
        #                 and hisBars[2].high < hisBars[3].high
        #                 ):
        #                     res += 1
        #     k += 1

        # k = 1
        # maxUsedBar = 5
        # if(k<27/maxUsedBar):
        #     signalCandleClose4 = hisBars[k*3+1].close
        #     signalCandleOpen4 = hisBars[k*4].open
        #     bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
        #     smallCandleRange4 = hisBars[k*5].high - hisBars[k*5].low
        #     endCandleRange4 = abs(hisBars[1].close - hisBars[k].open)

        #     if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
        #         if (signalCandleClose4 > signalCandleOpen4
        #             and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange4
        #             # and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange4
        #             and endCandleRange4 < bigCandleRange4*0.5
        #             ):
        #                 res += 1
        #     k += 1

        # if res < 1: continue

        # # Inside day
        # if(
        #     hisBarsQQQ[1].close < hisBarsQQQ[1].open
        #     and hisBarsQQQ[0].open > hisBarsQQQ[1].low
        #     and hisBarsQQQ[0].open < hisBarsQQQ[1].high
        #     # and hisBarsQQQ[0].open 
        #     #     < hisBarsQQQ[1].low + (hisBarsQQQ[1].high
        #     #                                 -hisBarsQQQ[1].low) * 0.28
        # ): continue

        # # Relative strength
        # if(
        #     (hisBarsQQQ[1].close > hisBarsQQQ[1].open
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

        # plotLinesRes = plotLines(hisBarsD1)
        # if(plotLinesRes < 0):
        #     continue
        
        trade['status'] = ''
        for i in hisBarsM30:
            if i.high >= op:
                trade['status'] = i.date
                break

        trade['result'] = ''
        if trade['status'] != '':
            triggeredTime = trade['status']
            for i in hisBarsM30:
                if i.date >= triggeredTime:
                    if i.date == triggeredTime:
                        if i.high >= tp:
                            net = (tp-op)*vol - fee
                            singleTrade.append(
                                {
                                    'profit': net,
                                    'symbol': symbol,
                                    'time': triggeredTime
                                }
                            )
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
                            singleTrade.append(
                                {
                                    'profit': net,
                                    'symbol': symbol,
                                    'time': triggeredTime
                                }
                            )
                            trade['total'] = net
                            trade['result'] = 'loss'
                            totalNetLoss += net
                            loss += 1
                            total += net
                            break

                        if i.high >= tp:
                            net = (tp-op)*vol - fee
                            singleTrade.append(
                                {
                                    'profit': net,
                                    'symbol': symbol,
                                    'time': triggeredTime
                                }
                            )
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
    print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
    singleTrade = sorted(singleTrade, key=lambda x:x['profit'], reverse=True)
                    
    # df = pd.DataFrame(trades)
    # df.to_csv('./csv/result/trades_status.csv')

    # singleTradeDf = pd.DataFrame(singleTrade)
    # singleTradeDf.to_csv('./csv/result/single_trade.csv')
except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)