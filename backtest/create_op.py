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
import gc

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
# ib.connect('127.0.0.1', 7497, clientId=9)

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

df = pd.read_csv (r'./csv/symbolLst.csv', index_col=0)
df.drop
filter_symbols = json.loads(df.to_json(orient = 'records'))
filter_sym_list = []
for i in filter_symbols:
    filter_sym_list.append(i['symbol'])

def normalizeFloat(price, sample1):
    strFloat1 = str(sample1)
    dec = strFloat1[::-1].find('.')
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

try:
    fee = 1.001392062 * 2
    tpVal = 20.189
    maxProfit = 0 #41.07
    maxTpVal = 0
    maxMarCapLimit = 0
    maxVolavgLimit = 0
    hisBarsQQQD1arr = [] 
    hisBarsStocksD1arr = []

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
    #     pickle.dump(hisBarsQQQD1arr, open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsQQQD1arr = pickle.load(open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "rb"))

    # print(hisBarsQQQD1arr)

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

        pickle.dump(hisBarsStocksD1arr, open("./pickle/pro/compressed/hisBarsStocksD1arr.p", "wb"))
        print("pickle dump finished")
    else:
        hisBarsStocksD1Dict = pickle.load(open("./pickle/pro/compressed/hisBarsStocks8MD1Dict.p", "rb"))

    # hisBarsStocksM30arr = []
    # saveStocksM30arr = False
    # if(saveStocksM30arr):
    #     for symbol in symbolLst:
    #         contract = Stock(symbol, 'SMART', 'USD')
    #         hisBarsM30 = ib.reqHistoricalData(
    #             contract, endDateTime='', durationStr='90 D',
    #             barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

    #         maxTrys = 0
    #         while(len(hisBarsM30)<6 and maxTrys<=20):
    #             print("timeout")
    #             hisBarsM30 = ib.reqHistoricalData(
    #                 contract, endDateTime='', durationStr='90 D',
    #                 barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)
    #             maxTrys += 1
            
    #         hisBarsStocksM30arr.append(
    #             {
    #                 'symbol': symbol,
    #                 'data': hisBarsM30
    #             }
    #         )

    #     pickle.dump(hisBarsStocksM30arr, open("./pickle/pro/compressed/hisBarsStocksM30arr.p", "wb"))
    #     print("pickle dump finished")
    # else:
    #     hisBarsStocksM30arr = pickle.load(open("./pickle/pro/compressed/hisBarsStocksM30arr.p", "rb"))

    # hisBarsStocksM15arr = []
    # saveStocksM15arr = False
    # if(saveStocksM15arr):
    #     for symbol in filter_sym_list:
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
    #         hisBarsStocksM15arr.append({'s': symbol,'d': hisBarsM15})
    #     pickle.dump(hisBarsStocksM15arr, open("./pickle/pro/compressed/hisBarsStocksM15arr.p", "wb"),protocol=-1)
    #     print("pickle dump finished")
    # else:
    #     output = open("./pickle/pro/compressed/hisBarsStocksM15arr.p", "rb")
    #     gc.disable()
    #     hisBarsStocksM15arr = pickle.load(output)
    #     output.close()
    #     gc.enable()
    #     print("load hisBarsStocksM15arr finished")

    startTime = dt.strptime('2021-03-18', '%Y-%m-%d').date()
    fee = 1.001392062 * 2
    tpVal = 6.766666667 #20.189
    opArr = []

    totalTrades = 0
    total = 0
    for symbol in hisBarsStocksD1Dict:
        if symbol not in filter_sym_list: continue
        data = hisBarsStocksD1Dict[symbol]
        for i, date in enumerate(data):
            if i>0 and  data[i].date>=startTime:
                op = data[i].open
                close1 = data[i-1].close
                # if op > close1:
                if True:
                    time = data[i].date
                    res = 0
                    
                    hisBarsD1 = list(filter(lambda x:x.date <= time,data))
                    hisBarsD1 = hisBarsD1[::-1]
                    # sma25D1 = sum(map(lambda x: x.close, hisBarsD1[1:26]))/25

                    # vol = int(cash * risk / op)
                    vol = int(1000 / op)
                    # if(vol < 3): continue

                    # hisBarsQQQD1 = list(filter(lambda x:x.date <= time,hisBarsQQQD1arr))
                    # hisBarsQQQD1 = hisBarsQQQD1[::-1]

                    # # Inside day
                    # if(
                    #     hisBarsQQQD1[1].close < hisBarsQQQD1[1].open
                    #     and hisBarsQQQD1[0].open > hisBarsQQQD1[1].low
                    #     and hisBarsQQQD1[0].open < hisBarsQQQD1[1].high
                    #     and hisBarsQQQD1[0].open 
                    #         < hisBarsQQQD1[1].low + (hisBarsQQQD1[1].high
                    #                                     -hisBarsQQQD1[1].low) * 0.28
                    # ): continue

                    # # Relative strength
                    # if(
                    #     (hisBarsQQQD1[1].close > hisBarsQQQD1[1].open
                    #     and hisBarsD1[1].close < hisBarsD1[1].open)
                    # ): continue

                    # # Previous day inside bar
                    # if(
                    #     hisBarsD1[1].high < hisBarsD1[2].high
                    #     and hisBarsD1[1].low > hisBarsD1[2].low
                    # ): continue

                    # # Bias
                    # if(
                    #     hisBarsD1[0].open/sma25D1 > 1.176
                    # ): continue

                    # if(
                    #     hisBarsD1[0].open <= hisBarsD1[1].close
                    # ):  continue

                    # for hisBarsStockM30 in hisBarsStocksM30arr:
                    #     if symbol == hisBarsStockM30['symbol']:
                    #         dataM30arr = hisBarsStockM30['data']
                    #         for dataM30 in dataM30arr:
                    #             if (
                    #                 dataM30.date.date() == time
                    #                 and dataM30.date.hour == 22
                    #                 and dataM30.date.minute == 30
                    #             ):
                    #                 time = dataM30.date
                    #                 print(time)
                    #                 op = dataM30.open
                    #                 break
                    #         break

                    # dataM15 = []
                    # for hisBarsStockM15 in hisBarsStocksM15arr:
                    #     if symbol == hisBarsStockM15['s']:
                    #         dataM15 = hisBarsStockM15['d']
                    #         break
                    # if(len(dataM15) < 6):
                    #     print(symbol,'M15 no data')
                    #     continue

                    # for i in dataM15:
                    #     print(i.date.date())
                    #     if (
                    #         i.date.date() == time
                    #         and i.date.hour == 23
                    #         and i.date.minute == 00
                    #     ):
                    #         time = i.date
                    #         print(time)
                    #         op = i.open
                    #         break
                    op = hisBarsD1[0].open
                    # sl = op
                    # if(op > 100):
                    #     sl = op - 1.167
                    # elif(op >= 50 and op < 100):
                    #     sl = op - 0.577
                    # elif(op >= 10 and op<50):
                    #     sl = op - 0.347
                    # elif(op < 10):
                    #     sl = op - 0.145
                    # sl = normalizeFloat(sl,op,close1)
                    sl = normalizeFloat(op * 0.9930862018, 0.01)
                    if op > 100:
                        sl = normalizeFloat(op * 0.9977520318, 0.01)

                    tp = op+(op-sl)*tpVal
                    tp = normalizeFloat(tp,0.01)

                    # opendHisBarsD1 = list(filter(lambda x:x.date >= time,data))
                    # for bar in data:
                    #     if bar.date>=time:
                    #         if bar.date == time:
                    #             if bar.high >= tp:
                    #                 net = (tp-op)*vol - fee
                    #                 # if(net > 0):
                    #                 #     trade['result'] = 'profit'
                    #                 #     totalNetProfit += net
                    #                 #     win += 1
                    #                 # else:
                    #                 #     trade['result'] = 'loss'
                    #                 #     totalNetLoss += net
                    #                 #     loss += 1
                    #                 total += net
                    #                 totalTrades += 1
                    #                 break
                    #         else:
                    #             if bar.low <= sl:
                    #                 net = (sl-op)*vol - fee
                    #                 # trade['total'] = net
                    #                 # trade['result'] = 'loss'
                    #                 # totalNetLoss += net
                    #                 # loss += 1
                    #                 total += net
                    #                 totalTrades += 1
                    #                 break

                    #             if bar.high >= tp:
                    #                 net = (tp-op)*vol - fee
                    #                 # trade['total'] = net
                    #                 # if(net > 0):
                    #                 #     trade['result'] = 'profit'
                    #                 #     totalNetProfit += net
                    #                 #     win += 1
                    #                 # else:
                    #                 #     trade['result'] = 'loss'
                    #                 #     totalNetLoss += net
                    #                 #     loss += 1
                    #                 total += net
                    #                 totalTrades += 1
                    #                 break



                    # print(
                    #     symbol,
                    #     time,
                    #     vol,
                    #     op,
                    #     sl,
                    #     tp
                    # )
                    opArr.append({
                        'symbol': symbol,
                        'time': time,
                        'vol': vol,
                        'op': op,
                        'sl': sl,
                        'tp': tp
                    })
    print(str(len(opArr)))
    print(total)
    print(totalTrades)

    df = pd.DataFrame(opArr)
    df.to_csv('./csv/trades_8M.csv')

            

    # # saveData = False
    # # if(saveData):
    # #     for trade in trades:
    # #         symbol = trade['symbol']
    # #         backtestTime = trade['time']
    # #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    # #         opEndTime = ''
    # #         contract = Stock(symbol, 'SMART', 'USD')
    # #         hisBarsM5 = ib.reqHistoricalData(
    # #             contract, endDateTime=opEndTime, durationStr='90 D',
    # #             barSizeSetting='5 mins', whatToShow='BID', useRTH=True)

    # #         while(len(hisBarsM5)<6):
    # #             print("timeout")
    # #             hisBarsM5 = ib.reqHistoricalData(
    # #                 contract, endDateTime=opEndTime, durationStr='90 D',
    # #                 barSizeSetting='5 mins', whatToShow='BID', useRTH=True)

    # #         hisBarsM5 = [data for data in hisBarsM5 if data.date >= backtestTime]
    # #         tradeHisBarsM5arr.append(hisBarsM5)

    # #     pickle.dump(tradeHisBarsM5arr, open("./pickle/tradeHisBarsM5arr.p", "wb"))
    # #     print("pickle dump finished")
    # # else:
    # #     tradeHisBarsM5arr = pickle.load(open("./pickle/tradeHisBarsM5arr.p", "rb"))
    # #     print(tradeHisBarsM5arr[0][0].date)

    # # saveQQQ = False
    # # if(saveQQQ):
    # #     for trade in trades:
    # #         symbol = trade['symbol']
    # #         backtestTime = trade['time']
    # #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    # #         opEndTime = ''
    # #         contractQQQ = Stock("QQQ", 'SMART', 'USD')

    # #         hisBarsQQQ = ib.reqHistoricalData(
    # #             contractQQQ, endDateTime=backtestTime, durationStr='365 D',
    # #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    # #         while(len(hisBarsQQQ)<6):
    # #             print("timeout")
    # #             hisBarsQQQ = ib.reqHistoricalData(
    # #             contractQQQ, endDateTime=backtestTime, durationStr='365 D',
    # #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    # #         hisBarsQQQ = hisBarsQQQ[::-1]
    # #         print(backtestTime,hisBarsQQQ[0].date)
    # #         tradeHisBarsQQQarr.append(hisBarsQQQ)
    # #         print("data get")

    # #     pickle.dump(tradeHisBarsM5arr, open("./pickle/tradeHisBarsQQQarr.p", "wb"))
    # #     print("pickle dump finished")
    # # else:
    # #     tradeHisBarsQQQarr = pickle.load(open("./pickle/tradeHisBarsQQQarr.p", "rb"))
    # #     print(tradeHisBarsQQQarr[0][0].date)

    # # saveHisBarsD1 = False
    # # if(saveHisBarsD1):
    # #     for trade in trades:
    # #         symbol = trade['symbol']
    # #         backtestTime = trade['time']
    # #         backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')
    # #         opEndTime = ''
    # #         contract= Stock(symbol, 'SMART', 'USD')

    # #         hisBarsD1 = ib.reqHistoricalData(
    # #             contract, endDateTime=backtestTime, durationStr='365 D',
    # #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    # #         while(len(hisBarsD1)<6):
    # #             print("timeout")
    # #             hisBarsD1 = ib.reqHistoricalData(
    # #             contract, endDateTime=backtestTime, durationStr='365 D',
    # #             barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    # #         hisBarsD1 = hisBarsD1[::-1]
    # #         print(backtestTime,hisBarsD1[0].date)
    # #         hisBarsD1arr.append(hisBarsD1)
    # #         print("data get")

    # #     pickle.dump(hisBarsD1arr, open("./pickle/hisBarsD1arr.p", "wb"))
    # #     print("pickle dump finished")
    # # else:
    # #     hisBarsD1arr = pickle.load(open("./pickle/hisBarsD1arr.p", "rb"))
    # #     print(hisBarsD1arr[0][0].date)

    # end = dt.now()
    # start = end - timedelta(days=50)

    # tradeSymList = []

    # # drop duplicat sym for req data from yahoo
    # for trade in trades:
    #     symbol = trade['symbol']
    #     if symbol not in tradeSymList:
    #         tradeSymList.append(symbol)

    # tradableList = []
    # fetchTradableList = False
    # if(fetchTradableList):
    #     for symbol in tradeSymList:
    #         dataReader = web.get_quote_yahoo(symbol)
    #         marketCap = 0
    #         if('marketCap' in dataReader):
    #             marketCap = dataReader['marketCap'][0]
    #         # if(marketCap < 21744275): continue
    #         if(marketCap < 1): continue
    #         volDf = web.DataReader(symbol, "yahoo", start, end)
    #         volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
    #         # if(volavg < 1987664): continue
    #         if(volavg < 1): continue
    #         tradableList.append({
    #             'symbol': symbol,
    #             'marketCap': marketCap,
    #             'volavg': volavg
    #         })
    #     print(tradableList)
    # else:
    #     tradableList = [
    #         {
    #             "symbol":"DRIO",
    #             "marketCap":252887872,
    #             "volavg":227373.33333333334
    #         },
    #         {
    #             "symbol":"AFIB",
    #             "marketCap":457566112,
    #             "volavg":278543.3333333333
    #         },
    #         {
    #             "symbol":"BFLY",
    #             "marketCap":2247645696,
    #             "volavg":2610820.0
    #         },
    #         {
    #             "symbol":"SUMR",
    #             "marketCap":27497594,
    #             "volavg":67036.66666666667
    #         },
    #         {
    #             "symbol":"BCEL",
    #             "marketCap":332756832,
    #             "volavg":214113.33333333334
    #         },
    #         {
    #             "symbol":"HOL",
    #             "marketCap":378750016,
    #             "volavg":779256.6666666666
    #         },
    #         {
    #             "symbol":"DLPN",
    #             "marketCap":65102912,
    #             "volavg":1693600.0
    #         },
    #         {
    #             "symbol":"TUR",
    #             "marketCap":358854496,
    #             "volavg":278833.3333333333
    #         },
    #         {
    #             "symbol":"FNKO",
    #             "marketCap":1309415680,
    #             "volavg":1225486.6666666667
    #         },
    #         {
    #             "symbol":"PRTA",
    #             "marketCap":1283835904,
    #             "volavg":299430.0
    #         },
    #         {
    #             "symbol":"LUMO",
    #             "marketCap":87321344,
    #             "volavg":25276.666666666668
    #         },
    #         {
    #             "symbol":"CERT",
    #             "marketCap":4024877568,
    #             "volavg":501573.3333333333
    #         },
    #         {
    #             "symbol":"WAFU",
    #             "marketCap":30973882,
    #             "volavg":620250.0
    #         },
    #         {
    #             "symbol":"TLS",
    #             "marketCap":2192277248,
    #             "volavg":717316.6666666666
    #         },
    #         {
    #             "symbol":"X",
    #             "marketCap":6992309760,
    #             "volavg":24911243.333333332
    #         },
    #         {
    #             "symbol":"HGEN",
    #             "marketCap":1186625024,
    #             "volavg":1363226.6666666667
    #         },
    #         {
    #             "symbol":"GTH",
    #             "marketCap":1881413760,
    #             "volavg":282583.3333333333
    #         },
    #         {
    #             "symbol":"QURE",
    #             "marketCap":1594964864,
    #             "volavg":409193.3333333333
    #         },
    #         {
    #             "symbol":"IQ",
    #             "marketCap":11255203840,
    #             "volavg":14975030.0
    #         },
    #         {
    #             "symbol":"ORPH",
    #             "marketCap":202409200,
    #             "volavg":15406.666666666666
    #         },
    #         {
    #             "symbol":"ING",
    #             "marketCap":54260740096,
    #             "volavg":5301096.666666667
    #         },
    #         {
    #             "symbol":"GP",
    #             "marketCap":345776096,
    #             "volavg":159440.0
    #         },
    #         {
    #             "symbol":"CAN",
    #             "marketCap":1328443136,
    #             "volavg":8109560.0
    #         },
    #         {
    #             "symbol":"ABCL",
    #             "marketCap":7268944896,
    #             "volavg":882190.0
    #         },
    #         {
    #             "symbol":"TIGR",
    #             "marketCap":3239165696,
    #             "volavg":8075886.666666667
    #         },
    #         {
    #             "symbol":"VLDR",
    #             "marketCap":1830460160,
    #             "volavg":3364056.6666666665
    #         },
    #         {
    #             "symbol":"BOWX",
    #             "marketCap":741404992,
    #             "volavg":654310.0
    #         },
    #         {
    #             "symbol":"STLA",
    #             "marketCap":61141372928,
    #             "volavg":2691123.3333333335
    #         },
    #         {
    #             "symbol":"TME",
    #             "marketCap":26641051648,
    #             "volavg":19764970.0
    #         },
    #         {
    #             "symbol":"VIPS",
    #             "marketCap":15697612800,
    #             "volavg":13328890.0
    #         },
    #         {
    #             "symbol":"HYLN",
    #             "marketCap":1805019008,
    #             "volavg":4331443.333333333
    #         },
    #         {
    #             "symbol":"VERY",
    #             "marketCap":134767504,
    #             "volavg":22476.666666666668
    #         },
    #         {
    #             "symbol":"RICE",
    #             "marketCap":466829504,
    #             "volavg":237140.0
    #         },
    #         {
    #             "symbol":"FTCV",
    #             "marketCap":371609440,
    #             "volavg":614800.0
    #         },
    #         {
    #             "symbol":"ALLT",
    #             "marketCap":686815296,
    #             "volavg":169020.0
    #         },
    #         {
    #             "symbol":"KZIA",
    #             "marketCap":124400312,
    #             "volavg":58433.333333333336
    #         },
    #         {
    #             "symbol":"AGC",
    #             "marketCap":736875008,
    #             "volavg":1416390.0
    #         },
    #         {
    #             "symbol":"GROW",
    #             "marketCap":93708032,
    #             "volavg":341450.0
    #         },
    #         {
    #             "symbol":"MUDS",
    #             "marketCap":539600896,
    #             "volavg":3507273.3333333335
    #         },
    #         {
    #             "symbol":"EVLO",
    #             "marketCap":716277760,
    #             "volavg":157590.0
    #         },
    #         {
    #             "symbol":"AFMD",
    #             "marketCap":1055113088,
    #             "volavg":1992766.6666666667
    #         },
    #         {
    #             "symbol":"TIRX",
    #             "marketCap":80588496,
    #             "volavg":2574583.3333333335
    #         },
    #         {
    #             "symbol":"MFNC",
    #             "marketCap":228732672,
    #             "volavg":95316.66666666667
    #         },
    #         {
    #             "symbol":"INO",
    #             "marketCap":1572710400,
    #             "volavg":8469566.666666666
    #         },
    #         {
    #             "symbol":"GSK",
    #             "marketCap":95853395968,
    #             "volavg":3992153.3333333335
    #         },
    #         {
    #             "symbol":"INFY",
    #             "marketCap":81624276992,
    #             "volavg":5427043.333333333
    #         },
    #         {
    #             "symbol":"CRCT",
    #             "marketCap":7475529728,
    #             "volavg":882640.0
    #         },
    #         {
    #             "symbol":"HOG",
    #             "marketCap":7428076544,
    #             "volavg":2783890.0
    #         },
    #         {
    #             "symbol":"SBLK",
    #             "marketCap":1936166528,
    #             "volavg":2076710.0
    #         },
    #         {
    #             "symbol":"NNDM",
    #             "marketCap":1766636160,
    #             "volavg":19362800.0
    #         },
    #         {
    #             "symbol":"SLV",
    #             "marketCap":8843554816,
    #             "volavg":24782183.333333332
    #         },
    #         {
    #             "symbol":"SKLZ",
    #             "marketCap":6726391808,
    #             "volavg":27060533.333333332
    #         },
    #         {
    #             "symbol":"RHE",
    #             "marketCap":20343052,
    #             "volavg":9296726.666666666
    #         },
    #         {
    #             "symbol":"FSLY",
    #             "marketCap":5458231296,
    #             "volavg":5295556.666666667
    #         },
    #         {
    #             "symbol":"MVIS",
    #             "marketCap":2464051200,
    #             "volavg":41417633.333333336
    #         },
    #         {
    #             "symbol":"M",
    #             "marketCap":5698168832,
    #             "volavg":15768986.666666666
    #         },
    #         {
    #             "symbol":"CLF",
    #             "marketCap":10047968256,
    #             "volavg":24163103.333333332
    #         },
    #         {
    #             "symbol":"AA",
    #             "marketCap":7394844160,
    #             "volavg":6818473.333333333
    #         },
    #         {
    #             "symbol":"VALE",
    #             "marketCap":110414823424,
    #             "volavg":32629186.666666668
    #         },
    #         {
    #             "symbol":"CUE",
    #             "marketCap":437391520,
    #             "volavg":701630.0
    #         },
    #         {
    #             "symbol":"T",
    #             "marketCap":210130190336,
    #             "volavg":55475246.666666664
    #         },
    #         {
    #             "symbol":"PRTY",
    #             "marketCap":1027012800,
    #             "volavg":3339010.0
    #         },
    #         {
    #             "symbol":"GOLD",
    #             "marketCap":42869145600,
    #             "volavg":16722826.666666666
    #         },
    #         {
    #             "symbol":"ET",
    #             "marketCap":26764550144,
    #             "volavg":19754410.0
    #         },
    #         {
    #             "symbol":"GGB",
    #             "marketCap":9986937856,
    #             "volavg":23106310.0
    #         },
    #         {
    #             "symbol":"SLB",
    #             "marketCap":43809677312,
    #             "volavg":13460740.0
    #         },
    #         {
    #             "symbol":"DVN",
    #             "marketCap":17978064896,
    #             "volavg":10530423.333333334
    #         },
    #         {
    #             "symbol":"TLRY",
    #             "marketCap":5280972800,
    #             "volavg":24492350.0
    #         },
    #         {
    #             "symbol":"JMIA",
    #             "marketCap":2877917952,
    #             "volavg":7100496.666666667
    #         },
    #         {
    #             "symbol":"AMC",
    #             "marketCap":11761313792,
    #             "volavg":127067256.66666667
    #         },
    #         {
    #             "symbol":"WFC",
    #             "marketCap":193473134592,
    #             "volavg":26819176.666666668
    #         },
    #         {
    #             "symbol":"XLF",
    #             "marketCap":33562077184,
    #             "volavg":48929166.666666664
    #         },
    #         {
    #             "symbol":"BAC",
    #             "marketCap":363253465088,
    #             "volavg":40778586.666666664
    #         },
    #         {
    #             "symbol":"PLUG",
    #             "marketCap":18103298048,
    #             "volavg":39983003.333333336
    #         },
    #         {
    #             "symbol":"F",
    #             "marketCap":57998528512,
    #             "volavg":89647013.33333333
    #         },
    #         {
    #             "symbol":"UBER",
    #             "marketCap":94917910528,
    #             "volavg":23346823.333333332
    #         },
    #         {
    #             "symbol":"AAL",
    #             "marketCap":15547122688,
    #             "volavg":36053233.333333336
    #         },
    #         {
    #             "symbol":"FCEL",
    #             "marketCap":3166252544,
    #             "volavg":24049866.666666668
    #         },
    #         {
    #             "symbol":"FSR",
    #             "marketCap":3903836928,
    #             "volavg":19316080.0
    #         },
    #         {
    #             "symbol":"LEDS",
    #             "marketCap":56079072,
    #             "volavg":11962370.0
    #         },
    #         {
    #             "symbol":"FUBO",
    #             "marketCap":3336087296,
    #             "volavg":14403013.333333334
    #         },
    #         {
    #             "symbol":"NIO",
    #             "marketCap":63279644672,
    #             "volavg":74499686.66666667
    #         },
    #         {
    #             "symbol":"CLOV",
    #             "marketCap":3104246528,
    #             "volavg":25111526.666666668
    #         },
    #         {
    #             "symbol":"UWMC",
    #             "marketCap":14269962240,
    #             "volavg":5955783.333333333
    #         },
    #         {
    #             "symbol":"NVVE",
    #             "marketCap":199138576,
    #             "volavg":1034080.0
    #         },
    #         {
    #             "symbol":"FF",
    #             "marketCap":449242688,
    #             "volavg":431593.3333333333
    #         },
    #         {
    #             "symbol":"SM",
    #             "marketCap":2344180224,
    #             "volavg":3626293.3333333335
    #         },
    #         {
    #             "symbol":"MGM",
    #             "marketCap":21029277696,
    #             "volavg":8107836.666666667
    #         },
    #         {
    #             "symbol":"PDSB",
    #             "marketCap":271795264,
    #             "volavg":2121333.3333333335
    #         },
    #         {
    #             "symbol":"MOXC",
    #             "marketCap":205655904,
    #             "volavg":2247053.3333333335
    #         },
    #         {
    #             "symbol":"TAK",
    #             "marketCap":54037041152,
    #             "volavg":2147040.0
    #         },
    #         {
    #             "symbol":"REAL",
    #             "marketCap":1586045312,
    #             "volavg":3000426.6666666665
    #         },
    #         {
    #             "symbol":"PRVB",
    #             "marketCap":482281472,
    #             "volavg":3363710.0
    #         },
    #         {
    #             "symbol":"GTX",
    #             "marketCap":601210688,
    #             "volavg":497093.23333333334
    #         },
    #         {
    #             "symbol":"DOYU",
    #             "marketCap":2562838784,
    #             "volavg":2541040.0
    #         },
    #         {
    #             "symbol":"HRTX",
    #             "marketCap":1216521984,
    #             "volavg":2204240.0
    #         },
    #         {
    #             "symbol":"OCGN",
    #             "marketCap":1642697856,
    #             "volavg":103634946.66666667
    #         },
    #         {
    #             "symbol":"ZH",
    #             "marketCap":5227612160,
    #             "volavg":1531333.3333333333
    #         },
    #         {
    #             "symbol":"AMWL",
    #             "marketCap":2993353472,
    #             "volavg":3958663.3333333335
    #         },
    #         {
    #             "symbol":"BTBT",
    #             "marketCap":408311584,
    #             "volavg":1877383.3333333333
    #         },
    #         {
    #             "symbol":"KODK",
    #             "marketCap":558944960,
    #             "volavg":2294893.3333333335
    #         },
    #         {
    #             "symbol":"WKEY",
    #             "marketCap":161405216,
    #             "volavg":865383.3333333334
    #         },
    #         {
    #             "symbol":"WNW",
    #             "marketCap":178500000,
    #             "volavg":529630.0
    #         },
    #         {
    #             "symbol":"AEVA",
    #             "marketCap":2059779840,
    #             "volavg":1397393.3333333333
    #         },
    #         {
    #             "symbol":"CLVS",
    #             "marketCap":536418464,
    #             "volavg":3986180.0
    #         },
    #         {
    #             "symbol":"BPTH",
    #             "marketCap":39603084,
    #             "volavg":185020.0
    #         },
    #         {
    #             "symbol":"AMR",
    #             "marketCap":365207552,
    #             "volavg":190040.0
    #         }
    #         ]
    # # df = pd.read_csv (r'./fillter.csv')
    # df = pd.read_csv (r'./fillter_all.csv')
    # df.drop
    # fillters = json.loads(df.to_json(orient = 'records'))

    # marketCapLimitArr = []
    # volavgLimitArr = []
    # for fillter in fillters:
    #     if(fillter['marketCap'] != None and fillter['marketCap'] > 0):
    #         marketCapLimitArr.append(
    #             int(fillter['marketCap'])
    #             ) 
    #     if(fillter['volavg'] != None and fillter['volavg']>0):
    #         volavgLimitArr.append(int(fillter['volavg']))

    # marketCapLimitArr.reverse()
    # volavgLimitArr.reverse()

    # total = 0
    # net = 0
    # win = 0
    # loss = 0
    # totalNetProfit = 0
    # totalNetLoss = 0
    # a = 0
    # for trade in trades:
    #     a += 1
    #     symbol = trade['symbol']
    #     if not list(filter(lambda x:x["symbol"]== symbol,tradableList)): continue
    #     marketCap = 0
    #     volavg = 0
    #     for sym in tradableList:
    #         if(symbol == sym['symbol']):
    #             marketCap = float(sym['marketCap'])
    #             volavg = float(sym['volavg'])
    #             # tpVal = volavg/175751849.851#1563121.35747
    #             # tpVal = marketCap/175751849.851
    #             tpVal = marketCap/188785133.098#175751849.851
    #             if(tpVal<20.189): tpVal=20.189

    #     # if(symbol == 'AMC'): continue
        
    #     marketCapLimit = 178499997
    #     volavgLimit = 922216
    #     if(marketCap < marketCapLimit): continue
    #     if(volavg < volavgLimit): continue

    #     backtestTime = trade['time']
    #     op = trade['op']
    #     if(op>13.60 and op < 50): continue
    #     sl = trade['sl']
    #     # tp = trade['tp']
    #     tp = op+(op-sl)*tpVal
    #     trade['tp'] = tp
    #     vol = trade['vol']
    #     trade['result'] = ''
    #     trade['total'] = 0
    #     if(vol<3): continue
    #     backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

    #     opEndTime = ''

    #     hisBarsQQQ = tradeHisBarsQQQarr[a-1]
    #     hisBarsD1 = hisBarsD1arr[a-1]

    #     sma25QQQ = sum(map(lambda x: x.close, hisBarsQQQ[2:27]))/25
    #     sma25D1 = sum(map(lambda x: x.close, hisBarsD1[2:27]))/25

    #     if(hisBarsQQQ[1].close/sma25QQQ > 1.021):
    #         continue
        
    #     # Inside day
    #     if(
    #         hisBarsQQQ[1].close < hisBarsQQQ[1].open
    #         and hisBarsQQQ[0].open > hisBarsQQQ[1].low
    #         and hisBarsQQQ[0].open < hisBarsQQQ[1].high
    #         and hisBarsQQQ[0].open 
    #             < hisBarsQQQ[1].low + (hisBarsQQQ[1].high
    #                                         -hisBarsQQQ[1].low) * 0.88
    #     ): continue


    #     if(hisBarsQQQ[0].open > hisBarsQQQ[1].close * 1.014):
    #         continue

    #     # Relative strength
    #     if(
    #         (hisBarsQQQ[1].close > hisBarsQQQ[1].open
    #         and hisBarsD1[1].close < hisBarsD1[1].open)
    #         or
    #         (hisBarsQQQ[1].close > hisBarsQQQ[3].open
    #         and hisBarsD1[1].close < hisBarsD1[3].open)
    #     ): continue

    #     # Previous day inside bar
    #     if(
    #         (hisBarsD1[1].high < hisBarsD1[2].high
    #         and hisBarsD1[1].low > hisBarsD1[2].low)
    #     ): continue

    #     plotLinesRes = plotLines(hisBarsQQQ)
    #     if(plotLinesRes < 0):
    #         continue
    #     plotLinesRes = plotLines(hisBarsD1)
    #     if(plotLinesRes < 0):
    #         continue

    #     hisBarsM5 = tradeHisBarsM5arr[a-1]

    #     opendHisBarsM5 = hisBarsM5

    #     endTime = hisBarsM5[-1].date
        
    #     trade['status'] = ''
    #     for i in opendHisBarsM5:
    #         if i.high >= op:
    #             trade['status'] = i.date
    #             break

    #     trade['result'] = ''
    #     if trade['status'] != '':
    #         triggeredTime = trade['status']
    #         for i in hisBarsM5:
    #             if i.date >= triggeredTime:
    #                 if i.date == triggeredTime:
    #                     if i.high >= tp:
    #                         net = (tp-op)*vol - fee
    #                         trade['total'] = net
    #                         if(net > 0):
    #                             trade['result'] = 'profit'
    #                             totalNetProfit += net
    #                             win += 1
    #                         else:
    #                             trade['result'] = 'loss'
    #                             totalNetLoss += net
    #                             loss += 1
    #                         total += net
    #                         break
    #                 else:
    #                     if i.low <= sl:
    #                         net = (sl-op)*vol - fee
    #                         trade['total'] = net
    #                         trade['result'] = 'loss'
    #                         totalNetLoss += net
    #                         loss += 1
    #                         total += net
    #                         break

    #                     if i.high >= tp:
    #                         net = (tp-op)*vol - fee
    #                         trade['total'] = net
    #                         if(net > 0):
    #                             trade['result'] = 'profit'
    #                             totalNetProfit += net
    #                             win += 1
    #                         else:
    #                             trade['result'] = 'loss'
    #                             totalNetLoss += net
    #                             loss += 1
    #                         total += net
    #                         break
                        
    #                     # if i.date >= endTime:
    #                     #     print(symbol," closeAtPre ",i.date)
    #                     #     if(i.open > op):
    #                     #         net = (i.open-op)*vol - 2
    #                     #         trade['total'] = net
    #                     #         if(net > 0):
    #                     #             trade['result'] = 'profit closeAtPre'
    #                     #             totalNetProfit += net
    #                     #             win += 1
    #                     #         else:
    #                     #             trade['result'] = 'loss closeAtPre'
    #                     #             totalNetLoss += net
    #                     #             loss += 1
    #                     #         total += net
    #                     #     else:
    #                     #         net = (i.open-op)*vol - 2
    #                     #         trade['total'] = net
    #                     #         trade['result'] = 'loss closeAtPre'
    #                     #         totalNetLoss += net
    #                     #         loss += 1
    #                     #         total += net
    #                     #     break
    # winrate = 0
    # if(win+loss>0):
    #     winrate = win/(win+loss)
    # profitfactor =0
    # if(abs(totalNetLoss)>0):
    #     profitfactor = totalNetProfit/abs(totalNetLoss)
    # elif(totalNetProfit>0):
    #     profitfactor = 99.99
    # print("total",str(total),
    #         "wr",winrate*100,"%",
    #         "profitfactor",str(profitfactor))
    # if(total > maxProfit): # and winrate>0.067
    #     maxProfit = total
    #     maxTpVal = tpVal
    #     maxMarCapLimit = marketCapLimit
    #     maxVolavgLimit = volavgLimit
    # print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
    # print('maxMarCapLimit',str(maxMarCapLimit),'maxVolavgLimit',str(maxVolavgLimit))
                    
    # df = pd.DataFrame(trades)
    # df.to_csv('./trades_status.csv')
except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)