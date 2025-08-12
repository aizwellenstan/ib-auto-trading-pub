# from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
from datetime import datetime as dt, timedelta
import json
import pickle
import numpy as np
import gc
import sys
sys.path.append('../')
# from aizfinviz import get_insider
from modules.aiztradingview import GetProfit,GetPE,GetProfitWithADR,GetIndustry,GetSector
import requests
from scipy.signal import lfilter
from modules.riskOfRuin import calcRisk
from modules.trend import GetTrend
import talib

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

def GetClosestPrice(price, arr, isBuy, isSell):
    curr = arr[0]
    arrSize = len(arr)
    # if(isBuy): price += (Ask - Bid)*2
    # if(isSell): price -= (Ask - Bid)*2
    idx = 0
    while idx <= arrSize-1:
        if (isBuy):
            if (abs(price - arr[idx]) < abs(price - curr) and arr[idx]>price):
                curr = arr[idx]
        if (isSell):
            if (abs(price - arr[idx]) < abs(price - curr) and arr[idx]<price):
                curr = arr[idx]
        idx += 1

    return curr

def GetLevel(price, buy, sell):
    mult = 0.0
    prc = 0.0
    lv0 = 0.0
    # lv25 = 0.0
    lv50 = 0.0
    # lv75 = 0.0
    digits = 0
    prc = MathFix(price, digits)
    mult = MathFixCeil(0.00001, digits)
    if (buy):
        lv0 = normalizeFloat(prc+mult,price,price)
        # lv25 = normalizeFloat(prc+0.25*mult,price,price)
        lv50 = normalizeFloat(prc+0.5*mult,price,price)
        # lv75 = normalizeFloat(prc+0.75*mult,price,price)
    if (sell):
        lv0 = normalizeFloat(prc-mult,price,price)
        # lv25 = normalizeFloat(prc-0.25*mult,price,price)
        lv50 = normalizeFloat(prc-0.5*mult,price,price)
        # lv75 = normalizeFloat(prc-0.75*mult,price,price)
    # arr = [lv0,lv25,lv50,lv75]
    arr = [lv0, lv50]
    # if (lv0>0 and lv25>0 and lv50>0 and lv75>0):
    if (lv0 > 0 and lv50 > 0):
        if (buy):
            return GetClosestPrice(price,arr,True,False)
        
        if (sell):
            return GetClosestPrice(price,arr,False,True)
    
    return price

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

def MathSign(n):
    if (n > 0): return(1)
    elif (n < 0): return (-1)
    else: return(0)

def MathFix(n, d):
    return(round(n*math.pow(10,d)+0.000000000001*MathSign(n))/math.pow(10,d))

def MathFixCeil(n, d):
    return(math.ceil(n*math.pow(10,d)+0.000000000001*MathSign(n))/math.pow(10,d))

def GetClosestPrice(price, arr, isBuy, isSell):
    curr = arr[0]
    
    arrSize = len(arr)
    
    # if(isBuy): price += (Ask - Bid)*2
    # if(isSell): price -= (Ask - Bid)*2
    
    idx = 0
    while idx <= arrSize-1:
        if (isBuy):
            if (abs(price - arr[idx]) < abs(price - curr) and arr[idx]>price):
                curr = arr[idx]
                
        if (isSell):
            if (abs(price - arr[idx]) < abs(price - curr) and arr[idx]<price):
                curr = arr[idx]
        idx += 1
    return curr

def GetLevel(price, buy, sell):
    mult = 0.0
    prc = 0.0
    lv0 = 0.0
    lv50 = 0.0
    
    digits = 0
    
    prc = MathFix(price,digits)
    
    mult = MathFixCeil(0.00001,digits)
    
    if (buy):
        lv0 = normalizeFloat(prc+mult,price,price)
        lv50 = normalizeFloat(prc+0.5*mult,price,price)
    if (sell):
        lv0 = normalizeFloat(prc-mult,price,price)
        lv50 = normalizeFloat(prc-0.5*mult,price,price)
    
    arr = [lv0,lv50]
    
    if (lv0>0 and lv50>0):
        if (buy):
            return GetClosestPrice(price,arr,True,False)
        
        if (sell):
            return GetClosestPrice(price,arr,False,True)
    
        return price

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

# df = pd.read_csv (r'./csv/trades_rf3.csv', index_col=0)
df = pd.read_csv (r'./csv/trades_5-5M.csv', index_col=0)
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

        QQQD1arr = []
        output = open("./pickle/pro/compressed/QQQ5MD1arr.p", "rb")
        gc.disable()
        QQQD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load QQQD1arr finished")

        SPYD1arr = []
        output = open("./pickle/pro/compressed/SPY5MD1arr.p", "rb")
        gc.disable()
        SPYD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load SPYD1arr finished")

        VTID1arr = []
        output = open("./pickle/pro/compressed/VTI5MD1arr.p", "rb")
        gc.disable()
        VTID1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load VTID1arr finished")

        DIAD1arr = []
        output = open("./pickle/pro/compressed/DIA5MD1arr.p", "rb")
        gc.disable()
        DIAD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load DIAD1arr finished")

        IWMD1arr = []
        output = open("./pickle/pro/compressed/IWM5MD1arr.p", "rb")
        gc.disable()
        IWMD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load IWMD1arr finished")

        XLFD1arr = []
        output = open("./pickle/pro/compressed/XLF5MD1arr.p", "rb")
        gc.disable()
        XLFD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load XLFD1arr finished")

        # TLTD1arr = []
        # output = open("./pickle/pro/compressed/TLT5MD1arr.p", "rb")
        # gc.disable()
        # TLTD1arr = pickle.load(output)
        # output.close()
        # gc.enable()
        # print("load TLTD1arr finished")

        # IEFD1arr = []
        # output = open("./pickle/pro/compressed/IEF5MD1arr.p", "rb")
        # gc.disable()
        # IEFD1arr = pickle.load(output)
        # output.close()
        # gc.enable()
        # print("load IEFD1arr finished")

        hisBarsStocksD1arr = []
        # output = open("./pickle/pro/compressed/hisBarsStocksRFD1arr.p", "rb")
        output = open("./pickle/pro/compressed/hisBarsStocks5-5MD1arr.p", "rb")
        gc.disable()
        hisBarsStocksD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksD1arr finished")

        hisBarsStocksH1arr = []
        output = open("./pickle/pro/compressed/hisBarsStocks5-5MH1arr.p", "rb")
        gc.disable()
        hisBarsStocksH1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsStocksH1arr finished")

        # hisBarsStocksM30arr = []
        # output = open("./pickle/pro/compressed/hisBarsStocks5MM30arr.p", "rb")
        # gc.disable()
        # hisBarsStocksM30arr = pickle.load(output)
        # output.close()
        # gc.enable()
        # print("load hisBarsStocksM30arr finished")

        profitSymLst = GetProfit()
        adrList = GetProfitWithADR()
        industryList = GetIndustry()
        sectorList = GetSector()

        # payload=pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
        # first_table = payload[0]
        # second_table = payload[1]
        # df = first_table
        # sp500symbols = df['Symbol'].values.tolist()

        industryListGroup = {}
        for item in industryList:
            industryListGroup.setdefault(item['industry'], []).append(item['s'])

        sectorListGroup = {}
        for item in sectorList:
            sectorListGroup.setdefault(item['sector'], []).append(item['s'])

        fee = 1.001392062 * 2
        tpVal = 1.15137614678 #3.69 #2 #5 #2 #3.19148936 #2 #15.42857143 #5.7#5.7#35.2#23.5 #25.8
        maxProfit = 0
        maxTpVal = 6.766666667
        maxSlVal = 0
        maxMarCapLimit = 0
        maxVolavgLimit = 0
        maxGapVal = 0

        tradeHisBarsM5arr = []
        # tradeHisBarsQQQarr = []
        hisBarsD1arr = []

        gapVal = 0
        while gapVal <= 2:
            total = 0
            net = 0
            win = 0
            loss = 0
            totalNetProfit = 0
            totalNetLoss = 0
            for trade in trades:
                industryLeaderBoard = {}
                symbol = trade['symbol']
                if symbol not in profitSymLst: continue
                # if symbol not in peSymLst: continue
                backtestTime = trade['time']
                op = trade['op']
                # if op < 7.18: continue
                sl = trade['sl']

                adrRange = 0.01
                for s in adrList:
                    if s['s'] == symbol:
                        adrRange = s['adr']
                        break


                sl = op - 0.14
                # if op > 16.5:
                #     sl = normalizeFloat(op * 0.9930862018, op, sl)
                # if (op > 100):
                #     sl = normalizeFloat(op * 0.9977520318, op, sl)

                sl = normalizeFloat(op - adrRange * 0.05, 0.01, 0.01)
                if adrRange > 0.14:
                    sl = normalizeFloat(op - adrRange * 0.35, 0.01,0.01)

                trade['sl'] = sl

                # tp = normalizeFloat(op+(op-sl)*tpVal,op,sl)
                tp = op + adrRange * 4.47 #1.58
                # tp = op * 1.02 + adrRange
                tp = normalizeFloat(tp, 0.01, 0.01)

                # vol = trade['vol']
                if op - sl < 0.01: continue
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

                if(len(dataD1) < 181):continue
                hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
                
                hisBarsD1 = hisBarsD1[::-1]

                if (
                    hisBarsD1[0].open < hisBarsD1[1].close * 1.003067754
                ): continue

                gapRange = hisBarsD1[0].open - hisBarsD1[1].close
                if gapRange/adrRange < gapVal: continue

                hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),QQQD1arr))
                hisBarsSPYD1 = list(filter(lambda x:x.date <= backtestTime.date(),SPYD1arr))
                hisBarsVTID1 = list(filter(lambda x:x.date <= backtestTime.date(),VTID1arr))
                hisBarsDIAD1 = list(filter(lambda x:x.date <= backtestTime.date(),DIAD1arr))
                hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))
                hisBarsXLFD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLFD1arr))
                # hisBarsTLTD1 = list(filter(lambda x:x.date <= backtestTime.date(),TLTD1arr))
                # hisBarsIEFD1 = list(filter(lambda x:x.date <= backtestTime.date(),IEFD1arr))

                hisBarsQQQD1 = hisBarsQQQD1[::-1]
                hisBarsSPYD1 = hisBarsSPYD1[::-1]
                hisBarsVTID1 = hisBarsVTID1[::-1]
                hisBarsDIAD1 = hisBarsDIAD1[::-1]
                hisBarsIWMD1 = hisBarsIWMD1[::-1]
                hisBarsXLFD1 = hisBarsXLFD1[::-1]
                # hisBarsTLTD1 = hisBarsTLTD1[::-1]
                # hisBarsIEFD1 = hisBarsIEFD1[::-1]
                
                buy = 0
                opEndTime = ''

                slByClose = 0
                if (
                    hisBarsD1[2].close > hisBarsD1[2].open and
                    hisBarsD1[1].close > hisBarsD1[1].open
                ):
                    slByClose = hisBarsD1[1].close

                if sl < slByClose: sl = slByClose

                # if (
                #     hisBarsD1[0].open > hisBarsD1[1].close * 1.115132275
                # ): continue

                # Warrior Trading
                # if hisBarsD1[1].close > hisBarsD1[1].open: continue

                # Red Bar improved
                # if hisBarsD1[1].close-hisBarsD1[1].low > 0:
                #     if not (
                #         (hisBarsD1[1].high-hisBarsD1[1].close) /
                #         (hisBarsD1[1].close-hisBarsD1[1].low) > 0.37
                #     ): continue
                maxHigh = hisBarsD1[1].high
                for i in range(2,3):
                    if hisBarsD1[i].high > maxHigh:
                        maxHigh = hisBarsD1[i].high

                minLow = hisBarsD1[1].low
                for i in range(2,3):
                    if hisBarsD1[i].low < minLow:
                        minLow = hisBarsD1[i].low

                if hisBarsD1[1].close-minLow > 0:
                    if not (
                        (maxHigh-hisBarsD1[1].close) /
                        (hisBarsD1[1].close-minLow) > 0.03
                    ): continue

                maxHigh = hisBarsD1[1].high
                for i in range(2,51):
                    if hisBarsD1[i].high > maxHigh:
                        maxHigh = hisBarsD1[i].high

                if not hisBarsD1[0].open < maxHigh * 1.01:
                    continue

                hisBarsD1closeArr = []
                for d in hisBarsD1:
                    hisBarsD1closeArr.append(d.close)

                # Warrior Trading
                # smaD1 = sma(hisBarsD1closeArr[1:21], 20)
                # bias = (hisBarsD1[1].close-smaD1)/smaD1
                # if bias < 0: continue

                # sma5D1i = sma(hisBarsD1closeArr[1:6], 5)
                # sma5D1ii = sma(hisBarsD1closeArr[2:7], 5)
                # sma5D1iii = sma(hisBarsD1closeArr[3:8], 5)
                # sma5D1iv = sma(hisBarsD1closeArr[4:9], 5)
                # sma5D1v = sma(hisBarsD1closeArr[5:10], 5)
                # sma5D1vi = sma(hisBarsD1closeArr[6:11], 5)
                # sma5D1vii = sma(hisBarsD1closeArr[7:12], 5)
                # sma5D1viii = sma(hisBarsD1closeArr[8:13], 5)

                # gapVal = 0.89
                # if not (
                #     hisBarsD1[7].close > sma5D1vii*gapVal and
                #     hisBarsD1[6].close > sma5D1vi*gapVal and
                #     hisBarsD1[5].close > sma5D1v*gapVal and
                #     hisBarsD1[4].close > sma5D1iv*gapVal and
                #     hisBarsD1[3].close > sma5D1iii*gapVal and
                #     hisBarsD1[2].close > sma5D1ii*gapVal
                # ): continue

                lv = GetLevel(hisBarsD1[1].close, True, False)
                if hisBarsD1[0].open < lv * 0.92: continue

                # maxHigh = max(hisBarsD1[1].high, hisBarsD1[2].high, hisBarsD1[3].high, hisBarsD1[4].high)
                # lv = GetLevel(maxHigh, True, False)
                # if hisBarsD1[0].open > lv: continue

                # minLow = min(hisBarsD1[1].low, hisBarsD1[2].low)
                # if hisBarsD1[1].close < minLow: continue

                if (
                    hisBarsD1[0].open < hisBarsD1[15].high and
                    hisBarsD1[0].open > hisBarsD1[15].close and
                    hisBarsD1[0].open < hisBarsD1[14].high and
                    hisBarsD1[0].open > hisBarsD1[14].close and
                    hisBarsD1[0].open < hisBarsD1[10].high and
                    hisBarsD1[0].open > hisBarsD1[10].close and
                    hisBarsD1[0].open < hisBarsD1[9].high and
                    hisBarsD1[0].open > hisBarsD1[9].close
                ): continue

                if (
                    hisBarsD1[1].low > hisBarsD1[5].low and
                    hisBarsD1[1].close < hisBarsD1[5].high and
                    hisBarsD1[1].low > hisBarsD1[4].low and
                    hisBarsD1[1].close < hisBarsD1[4].high and
                    hisBarsD1[1].low > hisBarsD1[2].low and
                    hisBarsD1[1].close < hisBarsD1[2].high
                ): continue

                gapRange = hisBarsD1[0].open/hisBarsD1[1].high
                qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].high
                spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].high
                vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].high
                diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].high
                iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].high
                xlfGapRange = hisBarsXLFD1[0].open/hisBarsXLFD1[1].high
                # tltGapRange = hisBarsTLTD1[0].open/hisBarsTLTD1[1].high
                # iefGapRange = hisBarsIEFD1[0].open/hisBarsIEFD1[1].high
                
                if (
                    gapRange < qqqGapRange * 0.983 or
                    gapRange < spyGapRange * 0.983 or
                    gapRange < vtiGapRange * 0.983 or
                    gapRange < diaGapRange * 0.983 or
                    gapRange < iwmGapRange * 0.983
                ): continue

                gapRange = hisBarsD1[0].open/hisBarsD1[1].close
                qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].close
                spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].close
                vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].close
                diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].close
                iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].close
                xlfGapRange = hisBarsXLFD1[0].open/hisBarsXLFD1[1].close
                # tltGapRange = hisBarsTLTD1[0].open/hisBarsTLTD1[1].high
                # iefGapRange = hisBarsIEFD1[0].open/hisBarsIEFD1[1].high
                
                if (
                    gapRange < qqqGapRange * 1.014 or
                    gapRange < spyGapRange * 1.014 or
                    gapRange < vtiGapRange * 1.014 or
                    gapRange < diaGapRange * 1.014 or
                    gapRange < iwmGapRange * 1.014
                ): continue

                gapRange = hisBarsD1[1].close/hisBarsD1[1].low
                qqqGapRange = hisBarsQQQD1[1].close/hisBarsQQQD1[1].low
                spyGapRange = hisBarsSPYD1[1].close/hisBarsSPYD1[1].low
                vtiGapRange = hisBarsVTID1[1].close/hisBarsVTID1[1].low
                diaGapRange = hisBarsDIAD1[1].close/hisBarsDIAD1[1].low
                iwmGapRange = hisBarsIWMD1[1].close/hisBarsIWMD1[1].low

                if (
                    gapRange < qqqGapRange and
                    gapRange < spyGapRange and
                    gapRange < vtiGapRange and
                    gapRange < diaGapRange
                ): continue

                if hisBarsD1[1].close / hisBarsD1[1].open > 1.06:
                    continue

                if not hisBarsD1[1].close > hisBarsD1[1].open:
                    if hisBarsD1[1].close / hisBarsD1[3].open > 1.06:
                        continue

                if hisBarsD1[1].close / hisBarsD1[4].open > 1.07:
                    continue

                if not (
                    hisBarsD1[2].close < hisBarsD1[2].open and
                    hisBarsD1[1].close > hisBarsD1[1].open
                ):
                    if hisBarsD1[1].close / hisBarsD1[5].open > 1.08:
                        continue

                if hisBarsD1[1].close < hisBarsD1[1].open:
                    if hisBarsD1[1].close / hisBarsD1[6].open > 1.1:
                        continue

                if hisBarsD1[1].close / hisBarsD1[8].open > 1.14:
                    continue

                if hisBarsD1[1].close / hisBarsD1[9].open > 1.23:
                    continue

                if hisBarsD1[1].close / hisBarsD1[14].open > 1.2:
                    continue

                # if not (
                #     hisBarsD1[0].open > hisBarsD1[1].high and
                #     hisBarsD1[0].open > hisBarsD1[2].high
                # ):
                #     if (
                #         hisBarsD1[1].close < hisBarsD1[180].close * 0.92
                #     ): continue

                

                # if (
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ):
                #     highBreak = False
                #     if (
                #         hisBarsD1[0].open > hisBarsD1[1].high and
                #         hisBarsD1[0].open > hisBarsD1[2].high and
                #         hisBarsD1[0].open > hisBarsD1[50].high
                #     ): highBreak = True

                #     if not highBreak:
                #         if (
                #             hisBarsD1[1].close < hisBarsD1[180].close * 1.48 and
                #             trend < 0
                #         ): continue

                # smaD1 = sma(hisBarsD1closeArr[1:3], 2)
                # bias = (hisBarsD1[1].close-smaD1)/smaD1
                # if bias > 0.03: continue

                if not (
                    hisBarsD1[1].open > hisBarsD1[2].close * 1.04
                ):
                    smaD1 = sma(hisBarsD1closeArr[1:4], 3)
                    bias = (hisBarsD1[1].close-smaD1)/smaD1
                    if bias > 0.03: continue

                smaD1 = sma(hisBarsD1closeArr[1:51], 50)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                # if bias > -0.05: continue
                if bias > 0.1: continue

                if not (
                    hisBarsD1[1].high < hisBarsD1[2].high and
                    hisBarsD1[1].low > hisBarsD1[2].low
                ):
                    smaD1 = sma(hisBarsD1closeArr[1:3], 2)
                    bias = (hisBarsD1[1].close-smaD1)/smaD1
                    if bias < - 0.02: continue

                smaD1 = sma(hisBarsD1closeArr[1:4], 3)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < - 0.03: continue

                smaD1 = sma(hisBarsD1closeArr[1:5], 4)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < - 0.04: continue

                smaD1 = sma(hisBarsD1closeArr[1:7], 6)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < - 0.06: continue

                smaD1 = sma(hisBarsD1closeArr[1:9], 8)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < - 0.07: continue

                # smaD1 = sma(hisBarsD1closeArr[1:17], 16)
                # bias = (hisBarsD1[1].close-smaD1)/smaD1
                # if bias < - 0.13: continue

                smaD1 = sma(hisBarsD1closeArr[1:26], 25)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < -0.2: continue

                # if not hisBarsD1[1].close / hisBarsD1[1].open < 0.97:
                #     smaD1 = sma(hisBarsD1closeArr[1:6], 5)
                #     bias = (hisBarsD1[1].close-smaD1)/smaD1
                #     if (
                #         bias > 0.04
                #     ): continue

                #     smaD1 = sma(hisBarsD1closeArr[1:9], 8)
                #     bias = (hisBarsD1[1].close-smaD1)/smaD1
                #     if (
                #         bias > 0.05
                #     ): continue

                #     smaD1 = sma(hisBarsD1closeArr[1:10], 9)
                #     bias = (hisBarsD1[1].close-smaD1)/smaD1
                #     if (
                #         bias > 0.06
                #     ): continue

                #     smaD1 = sma(hisBarsD1closeArr[1:16], 15)
                #     bias = (hisBarsD1[1].close-smaD1)/smaD1
                #     if (
                #         bias > 0.12
                #     ): continue

                #     smaD1 = sma(hisBarsD1closeArr[1:22], 21)
                #     bias = (hisBarsD1[1].close-smaD1)/smaD1
                #     if (
                #         bias > 0.09
                #     ): continue

                # Industry
                # industryCheck = False
                # industryCheckPeriod = 4
                # industryLeader = hisBarsD1[1].close / hisBarsD1[industryCheckPeriod].open
                # for s in industryList:
                #     if s['s'] == symbol:
                #         industry = s['industry']
                #         groupList = industryListGroup[industry]
                #         if len(groupList) > 1:
                #             if industry in industryLeaderBoard:
                #                 industryLeader = industryLeaderBoard[industry]
                #             else:
                #                 for sym2 in groupList:
                #                     if sym2 == symbol: continue
                #                     else:
                #                         sym2hisBarsD1 = []
                #                         for sym2hisBarsStockD1 in hisBarsStocksD1arr:
                #                             if sym2 == sym2hisBarsStockD1['s']:
                #                                 sym2dataD1 = sym2hisBarsStockD1['d']
                #                                 break

                #                         if(len(sym2dataD1) < 181):continue
                #                         sym2hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),sym2dataD1))
                #                         sym2hisBarsD1 = sym2hisBarsD1[::-1]
                #                     industryGain = sym2hisBarsD1[1].close / sym2hisBarsD1[industryCheckPeriod].open
                #                     if industryGain > industryLeader:
                #                         industryLeader = industryGain
                #                 industryLeaderBoard[industry] = industryLeader
                #         else:
                #             industryCheck = True
                            
                # if hisBarsD1[1].close / hisBarsD1[industryCheckPeriod].open < industryLeader:
                #     industryCheck = True
                # if not industryCheck: continue

                # if (
                #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     hisBarsD1[4].close < hisBarsD1[4].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ): continue

                # if (
                #     hisBarsD1[9].close > hisBarsD1[9].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ): continue

                # if (
                #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     hisBarsD1[6].close < hisBarsD1[6].open and
                #     hisBarsD1[2].close > hisBarsD1[2].open
                # ): continue

                # if (
                #     hisBarsD1[9].close > hisBarsD1[9].open and
                #     hisBarsD1[3].close < hisBarsD1[3].open
                # ): continue

                # if (
                #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     hisBarsD1[3].close > hisBarsD1[3].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ): continue

                # if (
                #     hisBarsD1[8].close < hisBarsD1[8+5].open and
                #     hisBarsD1[6].close > hisBarsD1[6+5].open and
                #     hisBarsD1[1].close > hisBarsD1[1+5].open
                # ): continue

                # if(
                #     hisBarsD1[5].close < hisBarsD1[5].open and
                #     hisBarsD1[4].close > hisBarsD1[4].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open
                # ):  continue

                # if (
                #     hisBarsD1[6].close > hisBarsD1[6].open and
                #     hisBarsD1[4].close > hisBarsD1[4].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ):  continue

                # if(
                #     hisBarsD1[8].close > hisBarsD1[8].open and
                #     hisBarsD1[1].close < hisBarsD1[1].open
                # ):  continue

                # if(
                #     hisBarsD1[4].close > hisBarsD1[4].open and
                #     hisBarsD1[1].close < hisBarsD1[1].open
                # ):  continue

                # if (
                #     hisBarsD1[4].close < hisBarsD1[4].open and
                #     hisBarsD1[2].close > hisBarsD1[2].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ): continue

                # #high wr
                # if (
                #     hisBarsD1[6].close < hisBarsD1[6].open and
                #     hisBarsD1[3].close > hisBarsD1[3].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ): continue

                # # no diff
                # # if (
                # #     hisBarsD1[10].close > hisBarsD1[10].open and
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # #     hisBarsD1[2].close > hisBarsD1[2].open and
                # #     hisBarsD1[1].close < hisBarsD1[1].open and
                # #     trend < 0
                # # ): continue

                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[8].close < hisBarsD1[8].open and
                # #     hisBarsD1[7].close < hisBarsD1[7].open and
                # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # #     hisBarsD1[3].close < hisBarsD1[3].open and
                # #     hisBarsD1[1].close > hisBarsD1[1].open
                # # ): continue

                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[8].close > hisBarsD1[8].open and
                # #     hisBarsD1[7].close > hisBarsD1[7].open and
                # #     hisBarsD1[4].close > hisBarsD1[4].open and
                # #     hisBarsD1[2].close < hisBarsD1[2].open
                # # ): continue

                # # if (
                # #     hisBarsD1[1].low > hisBarsD1[2].high and
                # #     hisBarsD1[2].close > hisBarsD1[2].open and
                # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # ): continue

                # if (
                #     hisBarsD1[10].close < hisBarsD1[10].open and
                #     hisBarsD1[5].close > hisBarsD1[5].open and
                #     hisBarsD1[4].close > hisBarsD1[4].open and
                #     hisBarsD1[3].close > hisBarsD1[3].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ): continue

                # # # if (
                # # #     hisBarsD1[8].close > hisBarsD1[8].open and
                # # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # # #     hisBarsD1[2].close > hisBarsD1[2].open
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[15].close > hisBarsD1[15].open and
                # # #     hisBarsD1[14].close < hisBarsD1[14].open and
                # # #     hisBarsD1[11].close > hisBarsD1[11].open and
                # # #     hisBarsD1[10].close < hisBarsD1[10].open and
                # # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # # #     hisBarsD1[2].close > hisBarsD1[2].open
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[15].close < hisBarsD1[15].open and
                # # #     hisBarsD1[12].close > hisBarsD1[12].open and
                # # #     hisBarsD1[7].close > hisBarsD1[7].open and
                # # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # # #     hisBarsD1[1].close > hisBarsD1[1].open and
                # # #     trend < 0
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[12].close < hisBarsD1[12].open and
                # # #     hisBarsD1[11].close < hisBarsD1[11].open and
                # # #     hisBarsD1[9].close < hisBarsD1[9].open and
                # # #     hisBarsD1[7].close < hisBarsD1[7].open and
                # # #     hisBarsD1[4].close < hisBarsD1[4].open and
                # # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # # #     hisBarsD1[1].close < hisBarsD1[1].open and
                # # #     trend < 0
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[4].close > hisBarsD1[4].open and
                # # #     hisBarsD1[3].close < hisBarsD1[3].open and
                # # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[8].close > hisBarsD1[8].open and
                # # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # # #     hisBarsD1[5].close > hisBarsD1[5].open and
                # # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # # #     trend < 0
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[4].close > hisBarsD1[4].open and
                # # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # # #     hisBarsD1[1].close > hisBarsD1[1].open
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[7].close > hisBarsD1[7].open and
                # # #     hisBarsD1[5].close > hisBarsD1[5].open and
                # # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # # ): continue
                
                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[7].close < hisBarsD1[7].open and
                # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # #     hisBarsD1[5].close > hisBarsD1[5].open and
                # #     hisBarsD1[4].close < hisBarsD1[4].open and
                # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # #     hisBarsD1[2].close > hisBarsD1[2].open and
                # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # ): continue

                # # # if (
                # # #     hisBarsD1[7].close > hisBarsD1[7].open and
                # # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # # #     hisBarsD1[2].close > hisBarsD1[2].open and
                # # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # # ): continue

                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[4].close < hisBarsD1[4].open and
                # #     hisBarsD1[2].close > hisBarsD1[2].open
                # # ): continue

                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[6].close < hisBarsD1[6].open and
                # #     hisBarsD1[5].close < hisBarsD1[5].open
                # # ): continue

                # # if (
                # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # #     hisBarsD1[4].close < hisBarsD1[4].open and
                # #     hisBarsD1[2].close > hisBarsD1[2].open
                # # ): continue

                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[6].close > hisBarsD1[6].open and
                # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # #     hisBarsD1[2].close < hisBarsD1[2].open
                # # ): continue

                # # if (
                # #     hisBarsD1[5].close > hisBarsD1[5].open and
                # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # ):  continue

                # # if (
                # #     hisBarsD1[9].close < hisBarsD1[9].open and
                # #     hisBarsD1[7].close < hisBarsD1[7].open and 
                # #     hisBarsD1[7].open < hisBarsD1[8].close * 0.95
                # # ): continue
                # # if not (
                # #     hisBarsD1[1].high < hisBarsD1[2].high and
                # #     hisBarsD1[1].low > hisBarsD1[2].low
                # # ):
                # #     if (
                # #         hisBarsD1[20].close > hisBarsD1[20].open and
                # #         hisBarsD1[19].close > hisBarsD1[19].open and
                # #         hisBarsD1[17].close < hisBarsD1[17].open and
                # #         hisBarsD1[3].close > hisBarsD1[3].open and
                # #         hisBarsD1[2].close > hisBarsD1[2].open
                # #     ): continue

                # # # if (
                # # #     hisBarsD1[4].close < hisBarsD1[4].open and
                # # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # # #     hisBarsD1[2].close > hisBarsD1[2].open and
                # # #     hisBarsD1[1].close > hisBarsD1[1].open and
                # # #     hisBarsD1[2].open < hisBarsD1[3].open
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[6].close < hisBarsD1[6].open and
                # # #     hisBarsD1[4].open > hisBarsD1[5].high and
                # # #     hisBarsD1[4].close < hisBarsD1[5].low and
                # # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # # ): continue

                # # # if (
                # # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # # #     hisBarsD1[8].close > hisBarsD1[8].open and
                # # #     hisBarsD1[7].close < hisBarsD1[7].open and
                # # #     hisBarsD1[6].close < hisBarsD1[6].open and
                # # #     hisBarsD1[3].close < hisBarsD1[3].open and
                # # #     hisBarsD1[2].close > hisBarsD1[2].open and
                # # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # # ): continue
                # if not (
                #     hisBarsD1[2].low > hisBarsD1[3].low and
                #     hisBarsD1[1].low > hisBarsD1[2].low
                # ):
                #     # if (
                #     #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     #     hisBarsD1[3].close < hisBarsD1[3].open and
                #     #     hisBarsD1[1].close < hisBarsD1[1].open
                #     # ): continue

                #     if (
                #         hisBarsD1[6].close < hisBarsD1[6].open and
                #         hisBarsD1[5].close < hisBarsD1[5].open and
                #         hisBarsD1[4].close < hisBarsD1[4].open and
                #         hisBarsD1[2].close > hisBarsD1[2].open and
                #         hisBarsD1[1].close < hisBarsD1[1].open
                #     ): continue

                # # if (
                # #     hisBarsD1[9].close > hisBarsD1[9].open and
                # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # #     hisBarsD1[1].close > hisBarsD1[1].open
                # # ):  continue

                # if (
                #     hisBarsD1[6].close < hisBarsD1[6].open and
                #     hisBarsD1[3].close < hisBarsD1[3].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open and
                #     hisBarsD1[1].close < hisBarsD1[1].open
                # ):  continue

                # # if (
                # #     hisBarsD1[5].close < hisBarsD1[5].open and
                # #     hisBarsD1[4].close > hisBarsD1[4].open and
                # #     hisBarsD1[2].close < hisBarsD1[2].open and
                # #     hisBarsD1[1].close < hisBarsD1[1].open
                # # ):  continue

                # if (
                #     hisBarsD1[7].close > hisBarsD1[7].open and
                #     hisBarsD1[6].close < hisBarsD1[6].open and
                #     hisBarsD1[4].close < hisBarsD1[4].open and
                #     hisBarsD1[3].close > hisBarsD1[3].open
                # ):  continue

                # # if (
                # #     hisBarsD1[6].close < hisBarsD1[6].open and
                # #     hisBarsD1[4].close < hisBarsD1[4].open and
                # #     hisBarsD1[3].close > hisBarsD1[3].open and
                # #     hisBarsD1[1].close > hisBarsD1[1].open
                # # ):  continue

                # #high wr
                # if (
                #     hisBarsD1[4].close > hisBarsD1[4].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open and
                #     hisBarsD1[1].close < hisBarsD1[1].open
                # ):  continue

                # if (
                #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     hisBarsD1[4].close < hisBarsD1[4].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ):  continue

                # # high wr
                # if (
                #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     hisBarsD1[6].close > hisBarsD1[6].open and
                #     hisBarsD1[2].close > hisBarsD1[2].open
                # ):  continue

                # if (
                #     hisBarsD1[6].close > hisBarsD1[6].open and
                #     hisBarsD1[5].close < hisBarsD1[5].open and
                #     hisBarsD1[4].close > hisBarsD1[4].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open
                # ):  continue

                # if (
                #     hisBarsD1[8].close > hisBarsD1[8].open and
                #     hisBarsD1[3].close > hisBarsD1[3].open
                # ):  continue

                # if (
                #     hisBarsD1[9].close < hisBarsD1[9].open and
                #     hisBarsD1[8].close < hisBarsD1[8].open and
                #     hisBarsD1[7].close < hisBarsD1[7].open and
                #     hisBarsD1[6].close < hisBarsD1[6].open and
                #     hisBarsD1[5].close < hisBarsD1[5].open and
                #     hisBarsD1[4].close < hisBarsD1[4].open and
                #     hisBarsD1[3].close < hisBarsD1[3].open and
                #     hisBarsD1[2].close < hisBarsD1[2].open and
                #     hisBarsD1[1].close < hisBarsD1[1].open
                # ):  continue

                # trend = GetTrend(hisBarsD1closeArr[1:226])

                # if (
                #     hisBarsD1[26].close > hisBarsD1[26].open and
                #     hisBarsD1[22].close < hisBarsD1[22].open and
                #     hisBarsD1[20].close > hisBarsD1[20].open and
                #     hisBarsD1[7].close > hisBarsD1[7].open and
                #     hisBarsD1[6].close > hisBarsD1[6].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open and
                #     trend < 0
                # ): continue

                # df = df.assign(nextOpen=df.open.shift(-1))
                # df = df.assign(nextClose=df.close.shift(-1))
                # bearCandle = df['nextClose'] < df['nextOpen']

                # if op > 100:
                #     df = df.assign(h1l1=df.high/df.low)
                #     avgH1L1 = df.loc[bearCandle, 'h1l1'].mean()

                #     H1L1 = hisBarsD1[1].high / hisBarsD1[1].low
                #     if (
                #         H1L1 > avgH1L1
                #     ): continue

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
                    # ohlcDf = df[:-1]
                    # ohlcDf = ohlcDf.assign(
                    #     hchl = (
                    #                 (ohlcDf.high - ohlcDf.close)/
                    #                 (ohlcDf.high - ohlcDf.low)
                    #     )
                    # )
                    # ohlcDf = ohlcDf.assign(nextOpen=ohlcDf.open.shift(-1))
                    # ohlcDf = ohlcDf.assign(nextClose=ohlcDf.close.shift(-1))
                    # bearCandle = ohlcDf['nextClose'] < ohlcDf['nextOpen']
                    # avgHCHL = ohlcDf.loc[bearCandle, 'hchl'].mean()
                    # HCHL = (
                    #             (hisBarsD1[1].high - hisBarsD1[1].close)
                    #             / (hisBarsD1[1].high - hisBarsD1[1].low)
                    # )

                    # if (
                    #     HCHL > avgHCHL * 0.84
                    # ): continue 

                    # period = 11
                    # df['sma'] = df['close'].rolling(window=period).mean()
                    # df['bias'] = (df['close']-df['sma'])/df['sma']
                    # bearBias = df['bias'] < 0
                    # avgBearBias = df.loc[bearBias, 'bias'].mean()

                    # if (
                    #     df.iloc[-2]['bias'] > avgBearBias
                    # ): continue

                    # momentumPeriod = 62
                    # momentumDf = momentumDf.assign(c30=momentumDf.close.shift(momentumPeriod))
                    # momentumDf = momentumDf.assign(momentum=momentumDf.close/momentumDf.c30)
                    # momentumDf = momentumDf.assign(nextOpen=momentumDf.open.shift(-1))
                    # momentumDf = momentumDf.assign(nextClose=momentumDf.close.shift(-1))

                    # bullCandle = momentumDf['nextClose'] > momentumDf['nextOpen']

                    # avgMomentum= momentumDf.loc[bullCandle, 'momentum'].mean()

                    # momentumDf = momentumDf.iloc[momentumPeriod:, :]

                    # if (
                    #     hisBarsD1[1].close/hisBarsD1[momentumPeriod].close > avgMomentum
                    # ): continue

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
                
                dataH1 = []
                for hisBarsStockH1 in hisBarsStocksH1arr:
                    if symbol == hisBarsStockH1['s']:
                        dataH1 = hisBarsStockH1['d']
                        break
                if(len(dataH1) < 6):
                    continue

                testhisBarsH1 = list(filter(lambda x:x.date >= backtestTime,dataH1))
                trade['status'] = ''
                
                for i in testhisBarsH1:
                    if i.high >= op:
                        trade['status'] = i.date
                        break

                trade['result'] = ''
                if trade['status'] != '':
                    triggeredTime = trade['status']
                    endTime = triggeredTime+timedelta(minutes=315)
                    for i in testhisBarsH1:
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
                maxGapVal = gapVal
            print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
            riskOfRuin = calcRisk(tpVal,winrate,100)
            print("riskOfRuin",riskOfRuin)
            print("maxGapVal",'{0:.10f}'.format(maxGapVal))
            gapVal += 0.01
              
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