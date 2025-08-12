# from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from datetime import datetime as dt, timedelta
import json
import pickle
import numpy as np
import gc
sys.path.append('../')
# from aizfinviz import get_insider
import requests
from scipy.signal import lfilter
from modules.riskOfRuin import calcRisk

# ib = IB()

# # IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
# ib.connect('127.0.0.1', 7497, clientId=12)

# cashDf = pd.DataFrame(ib.accountValues())
# # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
# #    print(cashDf)
# # cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
# cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
# cashDf = cashDf.loc[cashDf['currency'] == 'USD']
# cash = float(cashDf['value'])
# print(cash)
cash = 2061
risk = 0.00613800895 #0.06

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

def countSlopingCrosses(hisBars, fromBar, toBar, brk, rng, pk, body):
    t = 0
    x = 0
    lastCross = 0
    flag = False
    slope = 0
    val = 0
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

def plotLines(hisBars, brk = 2, body = False, tch = 4, level = 3, lineLife = 4):
    slopeUpper = 0
    slopeLower = 0
    pkArr = [1]
    trArr = [1]
    pk0A = 0
    pk0B = 0
    pk0C = 0
    pk1A = 0
    pk1B = 0
    pk1C = 0
    p = 0
    tr0A = 0
    tr0B = 0
    tr0C = 0
    tr1A = 0
    tr1B = 0
    tr1C = 0
    t = 0
    slope = 0.0
    i = 1
    hisBarsLen = len(hisBars)
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
        u = ""
        x = 0
        j = 0
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
    
        slope_val = 0
        if(slopeUpper > slope_val and slopeLower > slope_val):  return 1
        if(slopeUpper < -slope_val or slopeLower < -slope_val): return -1
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def talib_pattern(dur,time, df):
    try:
        morning_star = talib.CDLMORNINGSTAR(df['open'], df['high'], df['low'], df['close'])
        evening_star = talib.CDLEVENINGSTAR(df['open'], df['high'], df['low'], df['close'])
        engulfing = talib.CDLENGULFING(df['open'], df['high'], df['low'], df['close'])
        df['morning_star'] = morning_star
        df['evening_star'] = evening_star
        df['engulfing'] = engulfing
        signal_time = time-timedelta(minutes=dur)
        if signal_time.isoweekday()==7:
            signal_time = signal_time-timedelta(days = 2)
        if (dur >= 1440):    signal_time = signal_time.date()
        df_signal = df.loc[df['date'] == signal_time]
        morning_star_val = 0
        evening_star_val = 0
        engulfin_val = 0
        if(len(df_signal) > 0):
            morning_star_val = df_signal.iloc[0]['morning_star']
            evening_star_val = df_signal.iloc[0]['evening_star']
            engulfin_val = df_signal.iloc[0]['engulfing']
        return(morning_star_val, evening_star_val, engulfin_val)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0, 0, 0

def Check20BarRetracement(hisBars):
    if(
        hisBars[1].open - hisBars[1].low
        > (hisBars[1].high - hisBars[1].low) * 0.32
    ):  return True
    return False

df = pd.read_csv (r'./csv/trades_rf3.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))

fillterDf = pd.read_csv (r'./csv/symbolLst.csv', index_col=0)
fillterDf.drop
filter_symbols = json.loads(fillterDf.to_json(orient = 'records'))
filter_sym_list = []
for i in filter_symbols:
    filter_sym_list.append(i['symbol'])

vix_df = pd.read_csv (r'./csv/VIX_History.csv')
vix_df.drop
vix_list = json.loads(vix_df.to_json(orient = 'records'))

# arkfund_df = pd.read_csv (r'./csv/ark-fund.csv', index_col=0)
# arkfund_df.drop
# arkfund_list = json.loads(arkfund_df.to_json(orient = 'records'))

# sectorDf = pd.read_csv (r'./csv/sector.csv', index_col=0)
# sectorDf.drop
# secLst = json.loads(sectorDf.to_json(orient = 'records'))
# sectorLst = sectorDf.groupby('sector')['symbol'].apply(list)

def main():
    try:
        # hisBarsQQQD1arr = [] 
        # output = open("./pickle/pro/compressed/hisBarsQQQD1arr.p", "rb")
        # gc.disable()
        # hisBarsQQQD1arr = pickle.load(output)
        # output.close()
        # gc.enable()
        # print("load hisBarsQQQD1arr finished")

        hisBarsStocksD1arr = []
        output = open("./pickle/pro/compressed/hisBarsStocksRFD1arr.p", "rb")
        gc.disable()
        hisBarsStocksD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksD1arr finished")

        hisBarsStocksM30arr = []
        output = open("./pickle/pro/compressed/hisBarsStocksRFM30arr.p", "rb")
        gc.disable()
        hisBarsStocksM30arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksM30arr finished")

        fee = 1.001392062 * 2
        tpVal = 2 #5 #2 #3.19148936 #2 #15.42857143 #5.7#5.7#35.2#23.5 #25.8
        maxProfit = 0
        maxTpVal = 0
        maxSlVal = 0
        maxMarCapLimit = 0
        maxVolavgLimit = 0

        tradeHisBarsM5arr = []
        # tradeHisBarsQQQarr = []
        hisBarsD1arr = []

        total = 0
        net = 0
        win = 0
        loss = 0
        totalNetProfit = 0
        totalNetLoss = 0
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in filter_sym_list: continue
            backtestTime = trade['time']
            op = trade['op']
            # if(op>13.60 and op < 50): continue
            if op<16.5: continue
            sl = trade['sl']
            sl = normalizeFloat(op * 0.9937888199, op, sl)
            if op > 18.97:
                sl = normalizeFloat(op * 0.9947503029, op, sl)
            if (op > 100):
                sl = normalizeFloat(op * 0.998584196, op, sl)
            trade['sl'] = sl
            # tp = normalizeFloat(op+(op-sl)*tpVal,op,sl)
            tp = normalizeFloat(op * 1.062712388,op,sl)
            if op < 100:
                tp = normalizeFloat(op * 1.057407407,op,sl)
            if op < 55:
                tp = normalizeFloat(op * 1.0299,op,sl)

            tp = normalizeFloat(op+(op-sl)*tpVal,op,sl)

            # vol = trade['vol']
            vol = int((1000)/(op-sl))
            # vol = int((cash*risk)/(op-sl))
            trade['vol'] = vol
            trade['result'] = ''
            trade['total'] = 0
            if(vol<2): continue
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d')
            backtestTime = backtestTime + timedelta(hours = 22) +timedelta(minutes = 30)

            dataD1 = []
            for hisBarsStockD1 in hisBarsStocksD1arr:
                if symbol == hisBarsStockD1['s']:
                    dataD1 = hisBarsStockD1['d']
                    break

            if(len(dataD1) < 330):continue
            hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
            # hisBarsD1[-1].close = hisBarsD1[-1].open
            df = pd.DataFrame(hisBarsD1)
            momentumDf = df
            hisBarsD1 = hisBarsD1[::-1]

            buy = 0
            opEndTime = ''

            # if (
            #     hisBarsD1[0].open <= hisBarsD1[1].close
            # ): continue

            # buy = 0
            # for i in range(1, 98):
            #     if hisBarsD1[0].open > hisBarsD1[i].high:
            #         buy += 1

            if True:
                if (
                    hisBarsD1[0].open > hisBarsD1[1].close * 1.115132275
                ): continue

                # 8b dwn
                # if(
                #     hisBarsD1[9].close < hisBarsD1[9].open
                #     and hisBarsD1[8].close < hisBarsD1[8].open
                #     and hisBarsD1[7].close < hisBarsD1[7].open
                #     and hisBarsD1[6].close < hisBarsD1[6].open
                #     and hisBarsD1[5].close < hisBarsD1[5].open
                #     and hisBarsD1[4].close < hisBarsD1[4].open
                #     and hisBarsD1[3].close < hisBarsD1[3].open
                #     and hisBarsD1[2].close < hisBarsD1[2].open
                # ):  continue

                # if (
                #     hisBarsD1[3].close > hisBarsD1[3].open
                #     and hisBarsD1[2].close < hisBarsD1[2].open
                #     and hisBarsD1[1].close > hisBarsD1[1].open
                #     and hisBarsD1[2].high > hisBarsD1[3].high
                #     and hisBarsD1[1].high < hisBarsD1[2].high
                #     and hisBarsD1[1].close < hisBarsD1[2].close
                # ): continue

                # Topping Tails
                ohlcDf = df[:-1]
                ohlcDf = ohlcDf.assign(
                    hchl = (
                                (ohlcDf.high - ohlcDf.close)/
                                (ohlcDf.high - ohlcDf.low)
                    )
                )
                ohlcDf = ohlcDf.assign(o2=ohlcDf.open.shift(1))
                ohlcDf = ohlcDf.assign(h2=ohlcDf.high.shift(1))
                ohlcDf = ohlcDf.assign(l2=ohlcDf.low.shift(1))
                ohlcDf = ohlcDf.assign(c2=ohlcDf.close.shift(1))

                ohlcDf = ohlcDf.assign(
                    hchl2 = (
                                (ohlcDf.h2 - ohlcDf.c2)/
                                (ohlcDf.h2 - ohlcDf.l2)
                    )
                )

                ohlcDf = ohlcDf.assign(nextOpen=ohlcDf.open.shift(-1))
                ohlcDf = ohlcDf.assign(nextClose=ohlcDf.close.shift(-1))
                bearCandle = ohlcDf['nextClose'] < ohlcDf['nextOpen']
                avgHCHL = ohlcDf.loc[bearCandle, 'hchl'].mean()
                avgHCHL2 = ohlcDf.loc[bearCandle, 'hchl2'].mean()

                HCHL = (
                            (hisBarsD1[1].high - hisBarsD1[1].close)
                            / (hisBarsD1[1].high - hisBarsD1[1].low)
                )
                HCHL2 = (
                            (hisBarsD1[2].high - hisBarsD1[2].close)
                            / (hisBarsD1[2].high - hisBarsD1[2].low)
                )

                if (
                    HCHL > avgHCHL * 0.69
                ): continue 
                if (
                    HCHL2 > avgHCHL2 * 0.69
                ): continue 

                period = 11
                df['sma'] = df['close'].rolling(window=period).mean()
                df['bias'] = (df['close']-df['sma'])/df['sma']
                bearBias = df['bias'] < 0
                avgBearBias = df.loc[bearBias, 'bias'].mean()

                if (
                    df.iloc[-2]['bias'] > avgBearBias
                ): continue

                momentumPeriod = 30
                momentumDf = momentumDf.assign(c30=momentumDf.close.shift(momentumPeriod))
                momentumDf = momentumDf.assign(momentum=momentumDf.close/momentumDf.c30)
                momentumDf = momentumDf.assign(nextOpen=momentumDf.open.shift(-1))
                momentumDf = momentumDf.assign(nextClose=momentumDf.close.shift(-1))

                bullCandle = momentumDf['nextClose'] > momentumDf['nextOpen']

                avgMomentum= momentumDf.loc[bullCandle, 'momentum'].mean()

                momentumDf = momentumDf.iloc[momentumPeriod:, :]

                if (
                    hisBarsD1[1].close/hisBarsD1[momentumPeriod].close > avgMomentum
                ): continue

                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # df['sma'] = df['close'].rolling(window=20).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=20).mean()
                # df['lower_keltner'] = df['sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=20).std()
                # df['lower_band'] = df['sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # period = 15
                # df['sma'] = df['close'].rolling(window=period).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # period = 14
                # df['sma'] = df['close'].rolling(window=period).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue

                # period = 4
                # df['sma'] = df['close'].rolling(window=period).mean()
                # df['TR'] = abs(df['high'] - df['low'])
                # df['ATR'] = df['TR'].rolling(window=period).mean()
                # df['lower_keltner'] = df['sma'] - (df['ATR'] * 1.5)
                # df['upper_keltner'] = df['sma'] + (df['ATR'] * 1.5)

                # df['stddev'] = df['close'].rolling(window=period).std()
                # df['lower_band'] = df['sma'] - (2 * df['stddev'])
                # df['upper_band'] = df['sma'] + (2 * df['stddev'])

                # def in_squeeze(df):
                #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                # squeeze = False
                # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                #     squeeze = True

                # if squeeze: continue
            
                # Ark-fund
                # ark_fund = False
                # ark_fund_sell = False

                # TRADE_STATUS_URL = "http://127.0.0.1:8000/api/v1/stock/trades?symbol="+symbol
                # res = requests.get(TRADE_STATUS_URL, timeout=10)
                # html = res.text
                # if res.status_code == 200 and "no trades listed" not in html:
                #     r = res.json()['trades']
                #     for i in r:
                #         date = dt.strptime(i['date'], '%Y-%m-%d')
                #         date_end = date + timedelta(days=1)
                #         if date_end.isoweekday()==5:
                #             date_end += timedelta(days=3)
                #         direction = i['direction']
                #         if date >= backtestTime and backtestTime <= date_end:
                #             if direction == 'Sell':
                #                 ark_fund_sell = True
            
                # if ark_fund_sell:   continue

                # hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),hisBarsQQQD1arr))
                # hisBarsQQQD1 = hisBarsQQQD1[::-1]

                # hisBarsQQQD1closeArr = []
                # for d in hisBarsQQQD1:
                #     hisBarsQQQD1closeArr.append(d.close)

            eod = True
            
            dataM30 = []
            for hisBarsStockM30 in hisBarsStocksM30arr:
                if symbol == hisBarsStockM30['s']:
                    dataM30 = hisBarsStockM30['d']
                    break
            if(len(dataM30) < 6):
                continue

            testhisBarsM30 = list(filter(lambda x:x.date >= backtestTime,dataM30))
            trade['status'] = ''
            
            for i in testhisBarsM30:
                if i.high >= op:
                    trade['status'] = i.date
                    break

            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                endTime = triggeredTime+timedelta(minutes=90)
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

                            if eod:
                                if i.date == endTime:
                                    # # print(symbol," close ",i.date)
                                    # if(i.open > (op-sl)*2 and sl < op):
                                    #     newSl = op + (op-sl)
                                    #     # newSl = op + 0.01
                                    #     if(i.open > newSl and newSl > sl):
                                    #         sl = newSl
                                    #     # newSl = normalizeFloat((i.low + op) / 2,op,sl)
                                    #     # if newSl > sl:
                                    #     #     sl = newSl
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
        riskOfRuin = calcRisk(tpVal,winrate,100)
        print("riskOfRuin",riskOfRuin)
              
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

if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()','output.dat')

    # import pstats
    # from pstats import SortKey

    # with open("output_time.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("time").print_stats()
    
    # with open("output_calls.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("calls").print_stats()