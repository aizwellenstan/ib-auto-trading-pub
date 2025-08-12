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
from modules.harmonic.harmonic_functions import *
import requests
import talib

ib = IB()

# # IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
# ib.connect('127.0.0.1', 7497, clientId=11)

# cashDf = pd.DataFrame(ib.accountValues())
# # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
# #    print(cashDf)
# # cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
# cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
# cashDf = cashDf.loc[cashDf['currency'] == 'USD']
# cash = float(cashDf['value'])
# print(cash)

# risk = 0.06

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

df = pd.read_csv (r'./csv/trades_2315.csv', index_col=0)
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

        """timeframes
        1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
        """

        # hisBarsStocksW1arr = []
        # saveStocksW1arr = False
        # if(saveStocksW1arr):
        #     for symbol in filter_sym_list:
        #         contract = Stock(symbol, 'SMART', 'USD')
        #         hisBarsW1 = ib.reqHistoricalData(
        #             contract, endDateTime='', durationStr='52 W',
        #             barSizeSetting='1W', whatToShow='ASK', useRTH=True)
        #         maxTrys = 0
        #         while(len(hisBarsW1)<6 and maxTrys<=20):
        #             print("timeout")
        #             hisBarsW1 = ib.reqHistoricalData(
        #                 contract, endDateTime='', durationStr='52 W',
        #                 barSizeSetting='1W', whatToShow='ASK', useRTH=True)
        #             maxTrys += 1
        #         hisBarsStocksW1arr.append({'s': symbol,'d': hisBarsW1})
        #     pickle.dump(hisBarsStocksW1arr, open("./pickle/pro/compressed/hisBarsStocksW1arr.p", "wb"),protocol=-1)
        #     print("pickle dump finished")
        # else:
        #     output = open("./pickle/pro/compressed/hisBarsStocksW1arr.p", "rb")
        #     gc.disable()
        #     hisBarsStocksW1arr = pickle.load(output)
        #     output.close()
        #     gc.enable()
        #     print("load hisBarsStocksW1arr finished")

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
        #     for symbol in filter_sym_list:
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
        #     for symbol in filter_sym_list:
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
        #     for symbol in filter_sym_list:
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
        #     for symbol in filter_sym_list:
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
        #     for symbol in filter_sym_list:
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

        #     pickle.dump(hisBarsStocksM30arr, open("./pickle/pro/compressed/hisBarsStocksM30arr.p", "wb"),protocol=-1)
        #     print("pickle dump finished")
        # else:
        #     output = open("./pickle/pro/compressed/hisBarsStocksM30arr.p", "rb")
        #     gc.disable()
        #     hisBarsStocksM30arr = pickle.load(output)
        #     output.close()
        #     gc.enable()
        #     print("load hisBarsStocksM30arr finished")

        hisBarsStocksM15arr = []
        saveStocksM15arr = False
        if(saveStocksM15arr):
            for symbol in filter_sym_list:
                contract = Stock(symbol, 'SMART', 'USD')
                hisBarsM15 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='90 D',
                    barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)
                maxTrys = 0
                while(len(hisBarsM15)<6 and maxTrys<=20):
                    print("timeout")
                    hisBarsM15 = ib.reqHistoricalData(
                        contract, endDateTime='', durationStr='90 D',
                        barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)
                    maxTrys += 1
                hisBarsStocksM15arr.append({'s': symbol,'d': hisBarsM15})
            pickle.dump(hisBarsStocksM15arr, open("./pickle/pro/compressed/hisBarsStocksM15arr.p", "wb"),protocol=-1)
            print("pickle dump finished")
        else:
            output = open("./pickle/pro/compressed/hisBarsStocksM15arr.p", "rb")
            gc.disable()
            hisBarsStocksM15arr = pickle.load(output)
            output.close()
            gc.enable()
            print("load hisBarsStocksM15arr finished")

        # hisBarsStocksM10arr = []
        # saveStocksM10arr = False
        # if(saveStocksM10arr):
        #     for symbol in filter_sym_list:
        #         contract = Stock(symbol, 'SMART', 'USD')
        #         hisBarsM10 = ib.reqHistoricalData(
        #             contract, endDateTime='', durationStr='90 D',
        #             barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)
        #         maxTrys = 0
        #         while(len(hisBarsM10)<6 and maxTrys<=20):
        #             print("timeout")
        #             hisBarsM10 = ib.reqHistoricalData(
        #                 contract, endDateTime='', durationStr='90 D',
        #                 barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)
        #             maxTrys += 1
        #         hisBarsStocksM10arr.append({'s': symbol,'d': hisBarsM10})
        #     pickle.dump(hisBarsStocksM10arr, open("./pickle/pro/compressed/hisBarsStocksM10arr.p", "wb"),protocol=-1)
        #     print("pickle dump finished")
        # else:
        #     output = open("./pickle/pro/compressed/hisBarsStocksM10arr.p", "rb")
        #     gc.disable()
        #     hisBarsStocksM10arr = pickle.load(output)
        #     output.close()
        #     gc.enable()
        #     print("load hisBarsStocksM10arr finished")

        # hisBarsStocksM5arr = []
        # saveStocksM5arr = False
        # if(saveStocksM5arr):
        #     for symbol in filter_sym_list:
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
        #         hisBarsStocksM5arr.append({'s': symbol,'d': hisBarsM5})
        #     pickle.dump(hisBarsStocksM5arr, open("./pickle/pro/compressed/hisBarsStocksM5arr.p", "wb"),protocol=-1)
        #     print("pickle dump finished")
        # else:
        #     output = open("./pickle/pro/compressed/hisBarsStocksM5arr.p", "rb")
        #     gc.disable()
        #     hisBarsStocksM5arr = pickle.load(output)
        #     output.close()
        #     gc.enable()
        #     print("load hisBarsStocksM5arr finished")

        # hisBarsStocksM3arr = []
        # saveStocksM3arr = False
        # if(saveStocksM3arr):
        #     for symbol in filter_sym_list:
        #         contract = Stock(symbol, 'SMART', 'USD')
        #         hisBarsM3 = ib.reqHistoricalData(
        #             contract, endDateTime='', durationStr='90 D',
        #             barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)
        #         maxTrys = 0
        #         while(len(hisBarsM3)<6 and maxTrys<=20):
        #             print("timeout")
        #             hisBarsM3 = ib.reqHistoricalData(
        #                 contract, endDateTime='', durationStr='90 D',
        #                 barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)
        #             maxTrys += 1
        #         hisBarsStocksM3arr.append({'s': symbol,'d': hisBarsM3})
        #     pickle.dump(hisBarsStocksM3arr, open("./pickle/pro/compressed/hisBarsStocksM3arr.p", "wb"),protocol=-1)
        #     print("pickle dump finished")
        # else:
        #     output = open("./pickle/pro/compressed/hisBarsStocksM3arr.p", "rb")
        #     gc.disable()
        #     hisBarsStocksM3arr = pickle.load(output)
        #     output.close()
        #     gc.enable()
        #     print("load hisBarsStocksM3arr finished")

        fee = 1.001392062 * 2
        tpVal = 25.8
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
        for trade in trades:
            symbol = trade['symbol']
            if symbol not in filter_sym_list: continue
            backtestTime = trade['time']
            op = trade['op']
            # if(op>13.60 and op < 50): continue
            # if(op<0.97): continue
            # if(op>1.94 and op<10.96):continue
            sl = trade['sl']
            tp = normalizeFloat(op+(op-sl)*tpVal,op,sl)
            vol = trade['vol']
            trade['result'] = ''
            trade['total'] = 0
            if(vol<2): continue
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

            dataD1 = []
            for hisBarsStockD1 in hisBarsStocksD1arr:
                if symbol == hisBarsStockD1['symbol']:
                    dataD1 = hisBarsStockD1['data']
                    break

            if(len(dataD1) < 330):continue
            hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
            df_d1 = pd.DataFrame(hisBarsD1)
            hisBarsD1 = hisBarsD1[::-1]

            buy = 0
            opEndTime = ''

            # dataW1 = []
            # for hisBarsStockW1 in hisBarsStocksW1arr:
            #     if symbol == hisBarsStockW1['s']:
            #         dataW1 = hisBarsStockW1['d']
            #         break
            # if(len(dataW1) < 6):
            #     print(symbol,'W1 no data')
            #     continue
            # hisBarsW1 = list(filter(lambda x:x.date <= backtestTime.date(),dataW1))
            # df_w1 = pd.DataFrame(hisBarsW1)
            # hisBarsW1 = hisBarsW1[::-1]

            # dataH8 = []
            # for hisBarsStockH8 in hisBarsStocksH8arr:
            #     if symbol == hisBarsStockH8['s']:
            #         dataH8 = hisBarsStockH8['d']
            #         break
            # if(len(dataH8) < 6):
            #     print(symbol,'H8 no data')
            #     continue
            # hisBarsH8 = list(filter(lambda x:x.date <= backtestTime,dataH8))
            # hisBarsH8 = hisBarsH8[::-1]

            # dataH1 = []
            # for hisBarsStockH1 in hisBarsStocksH1arr:
            #     if symbol == hisBarsStockH1['s']:
            #         dataH1 = hisBarsStockH1['d']
            #         break
            # if(len(dataH1) < 6):
            #     print(symbol,'H1 no data')
            #     continue
            # hisBarsH1 = list(filter(lambda x:x.date <= backtestTime,dataH1))
            # df_h1 = pd.DataFrame(hisBarsH1)
            # hisBarsH1 = hisBarsH1[::-1]

            
            # hisBarsM15 = list(filter(lambda x:x.date <= backtestTime,dataM15))
            # hisBarsM15 = hisBarsM15[::-1]

            # dataM10 = []
            # for hisBarsStockM10 in hisBarsStocksM10arr:
            #     if symbol == hisBarsStockM10['s']:
            #         dataM10 = hisBarsStockM10['d']
            #         break
            # if(len(dataM10) < 6):
            #     print(symbol,'M10 no data')
            #     continue
            # hisBarsM10 = list(filter(lambda x:x.date <= backtestTime,dataM10))
            # hisBarsM10 = hisBarsM10[::-1]

            # hisBarsD1closeArr = []
            # for d in hisBarsD1:
            #     hisBarsD1closeArr.append(d.close)

            # sma25D1 = sma(hisBarsD1closeArr[1:26], 25)
            
            # bias = (hisBarsD1[1].close-sma25D1)/sma25D1
            # bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

            # biasSignal = False
            # biasval = 0.0482831585
            # if (
            #     bias < -biasval 
            #     and bias2 < -biasval
            # ):
            #     buy += 1
            #     biasSignal = True

            # # # 3 bar play
            # # if(
            # #     hisBarsW1[2].close > hisBarsW1[2].open
            # #     and hisBarsW1[2].close - hisBarsW1[2].open
            # #         > hisBarsW1[3].high - hisBarsW1[3].low
            # #     and hisBarsW1[1].high - hisBarsW1[1].low
            # #         < hisBarsW1[2].high - hisBarsW1[2].low
            # # ):
            # #     buy += 1

            # bp3_d1 = False
            # k = 1
            # while(k < 5):
            #     maxUsedBar = 4
            #     if(k<27/maxUsedBar):
            #         signalCandleClose3 = hisBarsD1[k*2+1].close
            #         signalCandleOpen3 = hisBarsD1[k*3].open
            #         bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
            #         smallCandleRange3 = hisBarsD1[k*4].high - hisBarsD1[k*4].low
            #         endCandleRange3 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

            #         if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 6.054347826086946):
            #             if (signalCandleClose3 > signalCandleOpen3
            #                 and abs(hisBarsD1[k+1].close - hisBarsD1[k*2].open) < bigCandleRange3
            #                 and endCandleRange3 < bigCandleRange3*0.5
            #                 and hisBarsD1[2].high < hisBarsD1[3].high
            #                 ):
            #                     buy += 1
            #                     bp3_d1 = True
            #     k += 1

            # turnArround = False
            # # if(
            # #     hisBarsM30[2].close > hisBarsM30[2].open
            # #     and hisBarsM30[1].close < hisBarsM30[1].open
            # # ):
            # #     buy += 1

            # k = 1
            # maxUsedBar = 5
            # while(k<=1):
            #     if(k<27/maxUsedBar):
            #         signalCandleClose4 = hisBarsD1[k*3+1].close
            #         signalCandleOpen4 = hisBarsD1[k*4].open
            #         bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
            #         smallCandleRange4 = hisBarsD1[k*5].high - hisBarsD1[k*5].low
            #         endCandleRange4 = abs(hisBarsD1[1].close - hisBarsD1[k].open)

            #         if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
            #             if (signalCandleClose4 > signalCandleOpen4
            #                 and abs(hisBarsD1[k*2+1].close - hisBarsD1[k*3].open) < bigCandleRange4
            #                 and endCandleRange4 < bigCandleRange4*0.5
            #                 ):
            #                     buy += 1
            #     k += 1

            # # M15 Turn arround
            # if(
            #     hisBarsM15[3].close < hisBarsM15[3].open
            #     and hisBarsM15[2].close > hisBarsM15[2].open
            # ):
            #     buy += 1

            # # M15 range break
            # if(
            #     hisBarsM15[2].high > hisBarsM15[3].high
            #     and hisBarsM15[2].low > hisBarsM15[3].open
            # ):
            #     buy += 1


            if(
                hisBarsD1[0].open < hisBarsD1[1].close * 1.01
            ):
                continue

            if(
                hisBarsD1[1].close < hisBarsD1[120].close
            ):  continue

            buy_setup = False
            if (
                hisBarsD1[4].close > hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
                and hisBarsD1[2].close - hisBarsD1[2].low
                    > (hisBarsD1[2].high - hisBarsD1[2].low) * 0.65
            ): buy_setup = True

            # Previous day inside bar
            if not buy_setup:
                if(
                    hisBarsD1[1].high < hisBarsD1[2].high
                    and hisBarsD1[1].low > hisBarsD1[2].low
                    and hisBarsD1[2].low < hisBarsD1[3].high
                    and hisBarsD1[3].close > hisBarsD1[2].open
                ): continue

            if(
                hisBarsD1[9].close < hisBarsD1[9].open
                and hisBarsD1[8].close < hisBarsD1[8].open
                and hisBarsD1[7].close < hisBarsD1[7].open
                and hisBarsD1[6].close < hisBarsD1[6].open
                and hisBarsD1[5].close < hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
            ):  continue

            if(
                hisBarsD1[1].close < hisBarsD1[12].low
                and hisBarsD1[1].close < hisBarsD1[11].low
                and hisBarsD1[1].close < hisBarsD1[10].low
                and hisBarsD1[1].close < hisBarsD1[9].low
                and hisBarsD1[1].close < hisBarsD1[8].low
                and hisBarsD1[1].close < hisBarsD1[7].low
                and hisBarsD1[1].close < hisBarsD1[6].low
                and hisBarsD1[1].close < hisBarsD1[5].low
                and hisBarsD1[1].close < hisBarsD1[4].low
                and hisBarsD1[1].close < hisBarsD1[3].low
                and hisBarsD1[1].close < hisBarsD1[2].low
            ):  continue

            # if(
            #     hisBarsD1[0].open < hisBarsD1[1].close * 1.01
            #     or hisBarsD1[0].open <= hisBarsH8[1].high
            # ):
            #     continue
        
            # if buy < 1: continue
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
        
            if ark_fund_sell:   continue

            hisBarsD1closeArr = []
            for d in hisBarsD1:
                hisBarsD1closeArr.append(d.close)
            sma25D1 = sma(hisBarsD1closeArr[1:26], 25)
            
            bias = (hisBarsD1[1].close-sma25D1)/sma25D1
            bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

            if not buy_setup:
                if (
                    bias > 0.15
                    and bias2 > 0.15
                ):  continue

            price = df_d1['close'][:-225]
            current_idx,current_pat,start,end = peak_detect(price.values)
            ### Harmonic Patterns
            XA = current_pat[1]-current_pat[0]
            AB = current_pat[2]-current_pat[1]
            BC = current_pat[3]-current_pat[2]
            CD = current_pat[4]-current_pat[3]

            moves = [XA,AB,BC,CD]

            err_allowed = 4.0/100
            gart = is_gartley(moves,err_allowed)
            butt = is_butterfly(moves,err_allowed)
            bat = is_bat(moves,err_allowed)
            crab = is_crab(moves,err_allowed)

            harmonics = np.array([gart,butt,bat,crab])

            labels = ['Gartely','Butterfly','Bat','Crab']

            if np.any(harmonics == 1) or np.any(harmonics == -1):
                
                for j in range(0,len(harmonics)):
                    
                    if harmonics[j] == 1 or harmonics[j] == -1:
                        
                        sense = 'Bearish' if harmonics[j] == -1 else 'Bullish'
                        label = sense + labels[j] + ' Found'




            if not (
                (
                    (hisBarsD1[1].high-hisBarsD1[1].low)
                    / (hisBarsD1[2].high-hisBarsD1[2].low) >= 2.91
                    and hisBarsD1[1].close < hisBarsD1[2].low
                )
                or buy_setup
            ):
                if(hisBarsD1[2].close / hisBarsD1[3].close < 1.35):
                    plotLinesRes = plotLines(hisBarsD1)
                    if(plotLinesRes < 0):   continue

            d1_morning_star_val, d1_evening_star_val, d1_engulfin_val = talib_pattern(
                1440, backtestTime, df_d1)
            if(d1_evening_star_val < 0):
                continue

            # if biasSignal and buy == 1:
            #     tp = normalizeFloat(op+(op-sl)*20.5,op,sl)
            # if turnArround and buy == 1:
            #     tp = normalizeFloat(op+(op-sl)*22.5,op,sl)
            # if bp3_d1 and buy == 1:
            #     tp = normalizeFloat(op+(op-sl)*25.9,op,sl)
            # if ark_fund and buy == 1:
            #     tp = normalizeFloat(op+(op-sl)*25.2,op,sl)

            eod = False

            dataM15 = []
            for hisBarsStockM15 in hisBarsStocksM15arr:
                if symbol == hisBarsStockM15['s']:
                    dataM15 = hisBarsStockM15['d']
                    break
            if(len(dataM15) < 6):
                print(symbol,'M15 no data')
                continue

            testhisBarsM15 = list(filter(lambda x:x.date >= backtestTime,dataM15))
            trade['status'] = ''
            for i in testhisBarsM15:
                if i.high >= op:
                    trade['status'] = i.date
                    break

            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                endTime = triggeredTime+timedelta(minutes=60)
                for i in testhisBarsM15:
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
                                    print(symbol," close ",i.date)
                                    if(i.open > op):
                                        sl = op
                                    # if(i.open > op):
                                    #     net = (i.open-op)*vol - fee
                                    #     trade['total'] = net
                                    #     if(net > 0):
                                    #         trade['result'] = 'profit close'
                                    #         totalNetProfit += net
                                    #         win += 1
                                    #     else:
                                    #         trade['result'] = 'loss close'
                                    #         totalNetLoss += net
                                    #         loss += 1
                                    #     total += net
                                    # else:
                                    #     net = (i.open-op)*vol - fee
                                    #     trade['total'] = net
                                    #     trade['result'] = 'loss close'
                                    #     totalNetLoss += net
                                    #     loss += 1
                                    #     total += net
                                    # break
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