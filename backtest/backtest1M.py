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
from modules.riskOfRuin import calcRisk

ib = IB()

# # IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=11)

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

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

def checkHisBarsD1(hisBarsD1, hisBarsD1reverse, symbol):
    df = pd.DataFrame(hisBarsD1)
    hisBarsD1 = hisBarsD1reverse
    op = hisBarsD1[0].close
    print(symbol,op)

    if (hisBarsD1[0].open <= hisBarsD1[1].close): return False

    if hisBarsD1[0].open/hisBarsD1[1].close > 1.115132275: return False
    # if hisBarsD1[0].open/hisBarsD1[1].close < 1.003067754: return False

    if (
        hisBarsD1[1].close < hisBarsD1[240].close * 1.32
    ): return False

    df = df.assign(h3=df.high.shift(2))
    df = df.assign(h2=df.high.shift(1))

    df = df.assign(l2=df.low.shift(1))

    df = df.assign(c1h3=df.close/df.h3)
    df = df.assign(c1h2=df.close/df.h2)

    df = df.assign(c1l2=df.close/df.l2)

    df = df.assign(nextOpen=df.open.shift(-1))
    df = df.assign(nextClose=df.close.shift(-1))
    bearCandle = df['nextClose'] < df['nextOpen']

    avgC1H3 = int(df.loc[bearCandle, 'c1h3'].mean())
    avgC1H2 = int(df.loc[bearCandle, 'c1h2'].mean())

    avgC1L2 = int(df.loc[bearCandle, 'c1l2'].mean())

    C1H3 = int(hisBarsD1[1].close / hisBarsD1[3].high)
    C1H2 = int(hisBarsD1[1].close / hisBarsD1[2].high)

    C1L2 = int(hisBarsD1[1].close / hisBarsD1[2].low)

    if (
        C1L2 == avgC1L2
    ): return False

    if op > 50:
        hisBarsD1closeArr = []
        for d in hisBarsD1:
            hisBarsD1closeArr.append(d.close)

        sma25D1 = sma(hisBarsD1closeArr[1:26], 25)
        ema21D1 = ema(hisBarsD1closeArr[1:22], 21)

        if ema21D1 < sma25D1: return False

        if not (
            hisBarsD1[8].close > hisBarsD1[8].open
            and hisBarsD1[7].close > hisBarsD1[7].open
            and hisBarsD1[6].close > hisBarsD1[6].open
            and hisBarsD1[5].close > hisBarsD1[5].open
            and hisBarsD1[4].close > hisBarsD1[4].open
            and hisBarsD1[3].close > hisBarsD1[3].open
            and hisBarsD1[2].close < hisBarsD1[2].open
            and hisBarsD1[1].close < hisBarsD1[1].open
        ):
            if (
                C1H3 == avgC1H3
                and C1H2 == avgC1H2
            ): return False

    print(symbol,"passed")
    return True

def checkScanner(symbol):
    try:
        try:
            dataReader = web.get_quote_yahoo(symbol)
            marketCap = 0
            if('marketCap' in dataReader):
                marketCap = dataReader['marketCap'][0]
            if(marketCap < 47305439): return False
            volDf = web.DataReader(symbol, "yahoo", start, end)
            volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
            if(volavg < 569043): return False
        except:
            pass

        return True
    except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)

downloadData = False
def main():

    all_symbol_list = []
    symbol_df = pd.read_csv (r'./csv/livetradersSym.csv')
    symbol_df.drop
    sym_list = json.loads(symbol_df.to_json(orient = 'records'))

    stocks = []

    for sym in sym_list:
        stocks.append(sym['symbol'])

    # stocks = ['MHO', 'MRVL', 'EHTH', 'PCRX', 'KEX', 'GIS']
    # stocks = ['AXP','PINS','BA']

    ignoreList = []

    hisBarsStocksD1arr = []
    saveStocksD1arr = downloadData
    if(saveStocksD1arr):
        for stock in stocks:
            symbol = stock
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            maxTrys = 0
            while(len(hisBarsD1)<6 and maxTrys<=4):
                print("timeout")
                hisBarsD1 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='365 D',
                    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                maxTrys += 1
            if (len(hisBarsD1) > 0):
                hisBarsStocksD1arr.append(
                    {
                        's': symbol,
                        'd': hisBarsD1
                    }
                )
            else:
                ignoreList.append(symbol)

        # pickle.dump(hisBarsStocksD1arr, open("./pickle/pro/compressed/trades/0724D1arr.p", "wb"),protocol=-1)
        print("pickle dump finished")
        print(ignoreList)
        df = pd.DataFrame(ignoreList)
        df.to_csv('./csv/ignoreD1.csv')
    else:
        output = open("./pickle/pro/compressed/trades/0724D1arr.p", "rb")
        gc.disable()
        hisBarsStocksD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksD1arr finished")

    hisBarsStocksM1arr = []
    saveStocksM1arr = downloadData
    if(saveStocksM1arr):
        for stock in stocks:
            symbol = stock
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='2 D',
                barSizeSetting='1 min', whatToShow='ASK', useRTH=False)

            maxTrys = 0
            while(len(hisBarsM1)<6 and maxTrys<=4):
                print("timeout")
                hisBarsM1 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='2 D',
                    barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
                maxTrys += 1
            if (len(hisBarsM1) > 0):
                hisBarsStocksM1arr.append(
                    {
                        's': symbol,
                        'd': hisBarsM1
                    }
                )
            else:
                ignoreList.append(symbol)

        # pickle.dump(hisBarsStocksM1arr, open("./pickle/pro/compressed/trades/0724M1arr.p", "wb"),protocol=-1)
        print("pickle dump finished")
        print(ignoreList)
        df = pd.DataFrame(ignoreList)
        df.to_csv('./csv/ignoreM1.csv')
    else:
        output = open("./pickle/pro/compressed/trades/0724M1arr.p", "rb")
        gc.disable()
        hisBarsStocksM1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksM1arr finished")

    backtestTimeD = '2021-07-23'
    backtestTimeD = dt.strptime(backtestTimeD, '%Y-%m-%d')
    preMarketTime = backtestTimeD + timedelta(hours = 21)
    # preMarketTime = backtestTimeD + timedelta(hours = 22)

    preMarketEndTime = backtestTimeD + timedelta(hours = 22) + timedelta(minutes = 29)
    backtestTime = backtestTimeD + timedelta(hours = 22) + timedelta(minutes = 30)
    endOpenTime = backtestTimeD + timedelta(hours = 23) + timedelta(minutes = 26)

    endTime = backtestTime+timedelta(minutes=85)

    cash = 1656.72
    risk = 0.00613800895 * 0.05

    fee = 1.001392062 * 2
    tpVal = 2 #2

    maxProfit = 0
    maxTpVal = 0

    cost = 0
    total = 0
    net = 0
    win = 0
    loss = 0
    totalNetProfit = 0
    totalNetLoss = 0

    eod = True

    trades = []

    for stock in stocks:
        symbol = stock

        dataM1 = []
        for hisBarsStockD1 in hisBarsStocksD1arr:
            if symbol == hisBarsStockD1['s']:
                dataD1 = hisBarsStockD1['d']
                break

        hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))

        if len(hisBarsD1)<240: continue

        hisBarsD1reverse = hisBarsD1[::-1]

        dataM1 = []
        for hisBarsStockM1 in hisBarsStocksM1arr:
            if symbol == hisBarsStockM1['s']:
                dataM1 = hisBarsStockM1['d']
                break

        preHisBarsM1 = list(filter(lambda x:(x.date >= preMarketTime and x.date < preMarketEndTime),dataM1))

        hisBarsM1 = list(filter(lambda x:x.date >= backtestTime,dataM1))

        limitedHisBarsM1 = list(filter(lambda x:x.date <= endOpenTime,hisBarsM1))

        if len(hisBarsM1)<2: continue

        M1High = hisBarsM1[0].high

        preMaxHigh = 0
        preMinLow = 9999

        for i in preHisBarsM1:
            if i.high > preMaxHigh:
                preMaxHigh = i.high
            if i.low < preMinLow:
                preMinLow = i.low

        if preMaxHigh-preMinLow<0.01: continue

        # buy = 0
        # for i in limitedHisBarsM1:
        #     if i.high > preMaxHigh and preMaxHigh-preMinLow>0.01:
        #         print(symbol,i.date,i.high-preMaxHigh)
        #         buy += 1
        #         break

        # if buy < 1: continue

        # buy = 0
        # for i in limitedHisBarsM1:
        #     if preMaxHigh-preMinLow>0.01:
        #         print(symbol,i.date)
        #         buy += 1
        #         break

        # if buy < 1: continue

        # buy = 0
        # for i in limitedHisBarsM1:
        #     if i.high > M1High:
        #         print(symbol,i.date)
        #         buy += 1
        #         break

        # if buy < 1: continue

        # if not checkHisBarsD1(hisBarsD1,hisBarsD1reverse,symbol): continue

        op = hisBarsM1[0].open

        if op > cash/2/14 : continue

        if op<3: continue
        sl =  normalizeFloat(op - 0.14, op, op-0.01)
        if op > 16.5:
            sl = normalizeFloat(op * 0.9930862018, op, sl)
        if (op > 100):
            sl = normalizeFloat(op * 0.9977520318, op, sl)

        # buy = 0
        # for i in limitedHisBarsM1:
        #     if i.high > M1High:
        #         print(symbol,i.date)
        #         buy += 1
        #         break

        # if buy < 1: continue

        op = preMaxHigh
        sl = preMinLow 

        print(op,sl)

        tp = normalizeFloat(op+(op-sl)*tpVal,op,sl)
        tp = normalizeFloat(op+(op-sl)*4.4,op,sl)

        diff = 0.00063717746183
        if abs((op-sl)/sl) < diff: continue

        # vol = int((1000)/(op-sl))
        vol = int((cash*risk)/(op-sl))

        volLimit = 7
        if op>=100: volLimit=2
        elif op>=50: volLimit=3
        else: volLimit=7
        if vol < volLimit: continue

        trade = {
            "symbol": symbol,
            "vol": vol,
            "op": op,
            "sl": sl,
            "tp": tp
        }
        

        print(trade)

        for i in hisBarsM1:
            if i.high >= op:
                triggeredTime = i.date
                if i.date >= triggeredTime:
                    if i.date == triggeredTime:
                        if i.high >= tp:
                            net = (tp-op)*vol - fee
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

                        if eod:
                            if i.date == endTime:
                                if(i.open > op):
                                    net = (i.open-op)*vol - fee
                                    trade['total'] = net
                                    if(net > 0):
                                        trade['result'] = 'profit close'
                                        totalNetProfit += net
                                        win += 1
                                    else:
                                        trade['result'] = 'loss close'
                                        totalNetLoss += net
                                        loss += 1
                                    total += net
                                else:
                                    net = (i.open-op)*vol - fee
                                    trade['total'] = net
                                    trade['result'] = 'loss close'
                                    totalNetLoss += net
                                    loss += 1
                                    total += net
                                break
        trade['gap%'] = hisBarsD1[0].open/hisBarsD1[1].close
        trades.append(trade)
        cost += vol*op
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
    print("cost",cost)
            # if(total > maxProfit): # and winrate>0.067
            #     maxProfit = total
            #     maxTpVal = tpVal
            # print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
    # riskOfRuin = calcRisk(tpVal,winrate,100)
    # print("riskOfRuin",riskOfRuin)
    df = pd.DataFrame(trades)
    df.to_csv('./csv/2021-07-23_trades_status.csv')

if __name__ == '__main__':
    main()
    