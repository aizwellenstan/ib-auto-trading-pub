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
mainFolder = '../'
sys.path.append(mainFolder)
from modules.movingAverage import Sma
from modules.normalizeFloat import NormalizeFloat
# from aizfinviz import get_insider
from modules.aiztradingview import GetProfit,GetPE,GetADR,GetIndustry,GetSector
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

def ema(x, period):
    dataArr = np.array([sum(x[0: period]) / period] + x[period:])
    alpha = 2/(period + 1.)
    wtArr = (1 - alpha)**np.arange(len(dataArr))
    xArr = (dataArr[1:] * alpha * wtArr[-2::-1]).cumsum() / wtArr[-2::-1]
    emaArr = dataArr[0] * wtArr +np.hstack((0, xArr))
    y = np.hstack((np.empty(period - 1) * np.nan, emaArr)).tolist()
    return y[-1]

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
df = pd.read_csv (r'./csv/trades_6M.csv', index_col=0)
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
        basicPoint = 0.01

        QQQD1arr = []
        output = open("./pickle/pro/compressed/QQQ6MD1arr.p", "rb")
        gc.disable()
        QQQD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load QQQD1arr finished")

        SPYD1arr = []
        output = open("./pickle/pro/compressed/SPY6MD1arr.p", "rb")
        gc.disable()
        SPYD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load SPYD1arr finished")

        VTID1arr = []
        output = open("./pickle/pro/compressed/VTI6MD1arr.p", "rb")
        gc.disable()
        VTID1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load VTID1arr finished")

        DIAD1arr = []
        output = open("./pickle/pro/compressed/DIA6MD1arr.p", "rb")
        gc.disable()
        DIAD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load DIAD1arr finished")

        IWMD1arr = []
        output = open("./pickle/pro/compressed/IWM6MD1arr.p", "rb")
        gc.disable()
        IWMD1arr = pickle.load(output)
        output.close()
        gc.enable()
        print("load IWMD1arr finished")

        hisBarsD1Dict = {}
        output = open("./pickle/pro/compressed/hisBarsStocks6MD1Dict.p", "rb")
        gc.disable()
        hisBarsD1Dict = pickle.load(output)
        output.close()
        gc.enable()
        print("load hisBarsD1Dict finished")

        hiBarsH1Dict = {}
        output = open("./pickle/pro/compressed/hisBarsStocks6MH1Dict.p", "rb")
        gc.disable()
        hiBarsH1Dict = pickle.load(output)
        output.close()
        gc.enable()
        print("load hiBarsH1Dict finished")

        profitSymList = GetProfit()
        adrDict = GetADR('USD')
        industryList = GetIndustry()
        sectorList = GetSector()

        adrValList = []
        for key in adrDict:
            adrValList.append(adrDict[key])
        adrValList.sort()

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
        minAdrVal = 0

        hisBarsD1arr = []

        oldLimit = 0.01
        idx = 0
        while idx <= len(adrValList):
            adrVal = adrValList[idx]
            if adrVal < oldLimit + 0.01: 
                idx += 1
                continue
            else: oldLimit = adrVal
            print(adrVal)
            total = 0
            net = 0
            win = 0
            loss = 0
            totalNetProfit = 0
            totalNetLoss = 0
            for trade in trades:
                industryLeaderBoard = {}
                symbol = trade['symbol']
                if symbol not in profitSymList: continue
                backtestTime = trade['time']
                op = trade['op']
                # if op < 7.18: continue
                sl = trade['sl']
                sl = op - 0.14

                adrRange = adrDict[symbol]
                if adrRange < adrVal: continue
                sl = NormalizeFloat(op - adrRange * 0.05, 0.01)
                if adrRange > 0.14:
                    sl = NormalizeFloat(op - adrRange * 0.35, 0.01)

                trade['sl'] = sl
                tp = op + adrRange * 5.57 #1.58
                tp = NormalizeFloat(tp, 0.01)

                if op - sl < 0.01: continue
                if op - sl < 0.02:
                    sl = NormalizeFloat(op - 0.02, basicPoint)
                vol = int((1000)/(op-sl))
                # vol = int((cash*risk)/(op-sl))
                trade['vol'] = vol
                trade['result'] = ''
                trade['total'] = 0
                if(vol<2): continue
                backtestTime = dt.strptime(backtestTime, '%Y-%m-%d')
                backtestTime = backtestTime + timedelta(hours = 22) +timedelta(minutes = 30)

                dataD1 = hisBarsD1Dict[symbol]

                if(len(dataD1) < 16):continue
                hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
                
                hisBarsD1 = hisBarsD1[::-1]
                if hisBarsD1[0].open < hisBarsD1[1].close * 1.003067754: 
                    continue
                if hisBarsD1[0].open < hisBarsD1[1].close * 1.02: 
                    continue

                # gapRange = hisBarsD1[0].open - hisBarsD1[1].close

                # if not (
                #     (
                #         hisBarsD1[2].close > hisBarsD1[2].open * 0.9917144678138942 and
                #         hisBarsD1[1].close > hisBarsD1[1].open * 0.9980928162746343
                #     ) or
                #     (
                #         hisBarsD1[1].low < hisBarsD1[2].low and
                #         hisBarsD1[1].high > hisBarsD1[2].high
                #     )
                # ):
                #     adr = (
                #         abs(hisBarsD1[1].close - hisBarsD1[3].open) +
                #         abs(hisBarsD1[4].close - hisBarsD1[6].open) +
                #         abs(hisBarsD1[7].close - hisBarsD1[9].open) +
                #         abs(hisBarsD1[10].close - hisBarsD1[12].open) +
                #         abs(hisBarsD1[13].close - hisBarsD1[15].open)
                #     ) / 5
                    
                #     if gapRange/adr > 2.82: continue

                # if not (
                #     (
                #         hisBarsD1[3].close < hisBarsD1[3].open and
                #         hisBarsD1[2].close < hisBarsD1[2].open and
                #         hisBarsD1[1].close > hisBarsD1[1].open
                #     ) or
                #     hisBarsD1[1].close < hisBarsD1[1].open or
                #     hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673
                # ):
                #     adr = (
                #         abs(hisBarsD1[1].close - hisBarsD1[10].open) +
                #         abs(hisBarsD1[11].close - hisBarsD1[20].open) +
                #         abs(hisBarsD1[21].close - hisBarsD1[30].open) +
                #         abs(hisBarsD1[31].close - hisBarsD1[40].open) +
                #         abs(hisBarsD1[41].close - hisBarsD1[50].open)
                #     ) / 5

                #     if gapRange/adr > 0.41: continue

                # if not (
                #     (
                #         hisBarsD1[2].close < hisBarsD1[2].open and
                #         hisBarsD1[1].close < hisBarsD1[1].open
                #     ) or
                #     hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673 or
                #     (
                #         hisBarsD1[3].close >= hisBarsD1[3].open and
                #         hisBarsD1[2].close > hisBarsD1[2].open and
                #         hisBarsD1[1].close > hisBarsD1[1].open * 0.993355481727574
                #     ) or
                #     (
                #         hisBarsD1[1].high / hisBarsD1[2].high > 0.99440037330844 and
                #         hisBarsD1[1].low < hisBarsD1[2].low
                #     )
                # ):
                #     adr = (
                #         abs(hisBarsD1[1].close - hisBarsD1[20].open) +
                #         abs(hisBarsD1[21].close - hisBarsD1[40].open) +
                #         abs(hisBarsD1[41].close - hisBarsD1[60].open) +
                #         abs(hisBarsD1[61].close - hisBarsD1[80].open) +
                #         abs(hisBarsD1[81].close - hisBarsD1[100].open)
                #     ) / 5

                #     if gapRange/adr > 0.34: continue

                # hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),QQQD1arr))
                # hisBarsSPYD1 = list(filter(lambda x:x.date <= backtestTime.date(),SPYD1arr))
                # hisBarsVTID1 = list(filter(lambda x:x.date <= backtestTime.date(),VTID1arr))
                # hisBarsDIAD1 = list(filter(lambda x:x.date <= backtestTime.date(),DIAD1arr))
                # hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))
                # # hisBarsXLFD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLFD1arr))
                # # hisBarsTLTD1 = list(filter(lambda x:x.date <= backtestTime.date(),TLTD1arr))
                # # hisBarsIEFD1 = list(filter(lambda x:x.date <= backtestTime.date(),IEFD1arr))

                # hisBarsQQQD1 = hisBarsQQQD1[::-1]
                # hisBarsSPYD1 = hisBarsSPYD1[::-1]
                # hisBarsVTID1 = hisBarsVTID1[::-1]
                # hisBarsDIAD1 = hisBarsDIAD1[::-1]
                # hisBarsIWMD1 = hisBarsIWMD1[::-1]
                # # hisBarsXLFD1 = hisBarsXLFD1[::-1]
                # # hisBarsTLTD1 = hisBarsTLTD1[::-1]
                # # hisBarsIEFD1 = hisBarsIEFD1[::-1]

                # buy = 0
                # opEndTime = ''

                # slByClose = 0
                # if (
                #     hisBarsD1[2].close > hisBarsD1[2].open and
                #     hisBarsD1[1].close > hisBarsD1[1].open
                # ):
                #     slByClose = hisBarsD1[1].close

                # if sl < slByClose: sl = slByClose

                # # if (
                # #     hisBarsD1[0].open > hisBarsD1[1].close * 1.115132275
                # # ): continue

                # # Warrior Trading
                # # if hisBarsD1[1].close > hisBarsD1[1].open: continue

                # # Red Bar improved
                # # if hisBarsD1[1].close-hisBarsD1[1].low > 0:
                # #     if not (
                # #         (hisBarsD1[1].high-hisBarsD1[1].close) /
                # #         (hisBarsD1[1].close-hisBarsD1[1].low) > 0.37
                # #     ): continue
                # maxHigh = hisBarsD1[1].high
                # for i in range(2,3):
                #     if hisBarsD1[i].high > maxHigh:
                #         maxHigh = hisBarsD1[i].high

                # minLow = hisBarsD1[1].low
                # for i in range(2,3):
                #     if hisBarsD1[i].low < minLow:
                #         minLow = hisBarsD1[i].low

                # if hisBarsD1[1].close-minLow > 0:
                #     if not (
                #         (maxHigh-hisBarsD1[1].close) /
                #         (hisBarsD1[1].close-minLow) > 0.03
                #     ): continue

                # hisBarsD1avgPriceArr = []
                # hisBarsD1closeArr = []
                # for d in hisBarsD1:
                #     avgPrice = (d.high+d.low) / 2
                #     hisBarsD1avgPriceArr.append(avgPrice)
                #     hisBarsD1closeArr.append(d.close)

                # if not hisBarsD1[1].close <= hisBarsD1[1].open:
                #     SmaD1 = Sma(hisBarsD1avgPriceArr[1:29], 28)
                #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     if bias < -0.17: continue

                # # Warrior Trading
                # # SmaD1 = Sma(hisBarsD1closeArr[1:21], 20)
                # # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                # # if bias < 0: continue

                # if (
                #     hisBarsD1[0].open < hisBarsD1[15].high and
                #     hisBarsD1[0].open > hisBarsD1[15].close and
                #     hisBarsD1[0].open < hisBarsD1[14].high and
                #     hisBarsD1[0].open > hisBarsD1[14].close and
                #     hisBarsD1[0].open < hisBarsD1[10].high and
                #     hisBarsD1[0].open > hisBarsD1[10].close and
                #     hisBarsD1[0].open < hisBarsD1[9].high and
                #     hisBarsD1[0].open > hisBarsD1[9].close
                # ): continue

                # # if (
                # #     hisBarsD1[1].low > hisBarsD1[5].low and
                # #     hisBarsD1[1].close < hisBarsD1[5].high and
                # #     hisBarsD1[1].low > hisBarsD1[4].low and
                # #     hisBarsD1[1].close < hisBarsD1[4].high and
                # #     hisBarsD1[1].low > hisBarsD1[2].low and
                # #     hisBarsD1[1].close < hisBarsD1[2].high
                # # ): continue

                # gapRange = hisBarsD1[0].open/hisBarsD1[1].high
                # qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].high
                # # spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].high
                # # vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].high
                # # diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].high
                # iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].high
                # # xlfGapRange = hisBarsXLFD1[0].open/hisBarsXLFD1[1].high
                # # tltGapRange = hisBarsTLTD1[0].open/hisBarsTLTD1[1].high
                # # iefGapRange = hisBarsIEFD1[0].open/hisBarsIEFD1[1].high
                
                # if (
                #     gapRange < qqqGapRange * 0.949 or
                #     gapRange < iwmGapRange * 0.949
                # ): continue

                # gapRange = hisBarsD1[0].open/hisBarsD1[1].close
                # qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].close
                # spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].close
                # vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].close
                # diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].close
                # iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].close
                # # xlfGapRange = hisBarsXLFD1[0].open/hisBarsXLFD1[1].close
                # # tltGapRange = hisBarsTLTD1[0].open/hisBarsTLTD1[1].high
                # # iefGapRange = hisBarsIEFD1[0].open/hisBarsIEFD1[1].high
                
                # if (
                #     gapRange < qqqGapRange * 1.013 or
                #     gapRange < spyGapRange * 1.013 or
                #     gapRange < vtiGapRange * 1.013 or
                #     gapRange < diaGapRange * 1.013 or
                #     gapRange < iwmGapRange * 1.013
                # ): continue

                # if  hisBarsD1[1].close / hisBarsD1[1].open > 0.926610644257703:
                #     if hisBarsD1[1].close / hisBarsD1[3].open > 1.06: continue

                # if not (
                #     (
                #         hisBarsD1[2].close < hisBarsD1[2].open and
                #         hisBarsD1[1].close > hisBarsD1[1].open
                #     ) or
                #     (
                #         hisBarsD1[4].close < hisBarsD1[4].open and
                #         hisBarsD1[3].close > hisBarsD1[3].open and
                #         hisBarsD1[2].close > hisBarsD1[2].open and
                #         hisBarsD1[1].close < hisBarsD1[1].open
                #     ) or
                #     hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673 or
                #     (
                #         hisBarsD1[2].close > hisBarsD1[2].open and
                #         hisBarsD1[1].close > hisBarsD1[1].open
                #     )
                # ):
                #     if hisBarsD1[1].close / hisBarsD1[5].open > 1.18: continue

                # if not hisBarsD1[1].close > hisBarsD1[1].open * 0.993355481727574:
                #     SmaD1 = Sma(hisBarsD1closeArr[1:51], 50)
                #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     # if bias > -0.05: continue
                #     if bias > 0.55: continue

                # if not (
                #     hisBarsD1[2].close > hisBarsD1[2].open and
                #     hisBarsD1[1].close < hisBarsD1[1].open
                # ):
                #     SmaD1 = Sma(hisBarsD1closeArr[1:9], 8)
                #     bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                #     if bias < -0.09: continue

                # SmaD1 = Sma(hisBarsD1closeArr[1:26], 25)
                # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                # if bias < -0.2: continue

                # SmaD1 = Sma(hisBarsD1closeArr[1:101], 100)
                # bias = (hisBarsD1[1].close-SmaD1)/SmaD1
                # if bias < -0.54: continue

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
                #                         for sym2hisBarsStockD1 in hisBarsD1Dict:
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
                    # df['Sma'] = df['close'].rolling(window=period).mean()
                    # df['bias'] = (df['close']-df['Sma'])/df['Sma']
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
                    # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                    # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                    # df['stddev'] = df['close'].rolling(window=period).std()
                    # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                    # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                    # def in_squeeze(df):
                    #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                    # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                    # squeeze = False
                    # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                    #     squeeze = True

                    # if squeeze: continue

                    # df['Sma'] = df['close'].rolling(window=20).mean()
                    # df['TR'] = abs(df['high'] - df['low'])
                    # df['ATR'] = df['TR'].rolling(window=20).mean()
                    # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                    # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                    # df['stddev'] = df['close'].rolling(window=20).std()
                    # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                    # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                    # def in_squeeze(df):
                    #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                    # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                    # squeeze = False
                    # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                    #     squeeze = True

                    # if squeeze: continue

                    # period = 15
                    # df['Sma'] = df['close'].rolling(window=period).mean()
                    # df['TR'] = abs(df['high'] - df['low'])
                    # df['ATR'] = df['TR'].rolling(window=period).mean()
                    # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                    # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                    # df['stddev'] = df['close'].rolling(window=period).std()
                    # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                    # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                    # def in_squeeze(df):
                    #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                    # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                    # squeeze = False
                    # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                    #     squeeze = True

                    # if squeeze: continue

                    # period = 14
                    # df['Sma'] = df['close'].rolling(window=period).mean()
                    # df['TR'] = abs(df['high'] - df['low'])
                    # df['ATR'] = df['TR'].rolling(window=period).mean()
                    # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                    # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                    # df['stddev'] = df['close'].rolling(window=period).std()
                    # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                    # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

                    # def in_squeeze(df):
                    #     return df['lower_band'] > df['lower_keltner'] and df['upper_band'] < df['upper_keltner']

                    # df['squeeze_on'] = df.apply(in_squeeze, axis=1)

                    # squeeze = False
                    # if df.iloc[-1]['squeeze_on'] and not df.iloc[-2]['squeeze_on']:
                    #     squeeze = True

                    # if squeeze: continue

                    # period = 4
                    # df['Sma'] = df['close'].rolling(window=period).mean()
                    # df['TR'] = abs(df['high'] - df['low'])
                    # df['ATR'] = df['TR'].rolling(window=period).mean()
                    # df['lower_keltner'] = df['Sma'] - (df['ATR'] * 1.5)
                    # df['upper_keltner'] = df['Sma'] + (df['ATR'] * 1.5)

                    # df['stddev'] = df['close'].rolling(window=period).std()
                    # df['lower_band'] = df['Sma'] - (2 * df['stddev'])
                    # df['upper_band'] = df['Sma'] + (2 * df['stddev'])

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
                
                dataH1 = hiBarsH1Dict[symbol]
                if(len(dataH1) < 6):
                    continue

                testhisBarsH1 = list(filter(lambda x:x.date >= backtestTime,dataH1))
                trade['status'] = ''
                
                cancelTime = backtestTime+timedelta(minutes=38)
                for i in testhisBarsH1:
                    if i.high >= op:
                        if i.date >= cancelTime: continue
                        trade['status'] = i.date
                        break

                trade['result'] = ''
                if trade['status'] != '':
                    triggeredTime = trade['status']
                    endTime = backtestTime+timedelta(minutes=155)
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
                                    if i.date >= endTime:
                                        # # print(symbol," close ",i.date)
                                        # if(i.open > (op-sl)*2 and sl < op):
                                        #     newSl = op + (op-sl)
                                        #     # newSl = op + 0.01
                                        #     if(i.open > newSl and newSl > sl):
                                        #         sl = newSl
                                        #     # newSl = NormalizeFloat((i.low + op) / 2,op,sl)
                                        #     # if newSl > sl:
                                        #     #     sl = newSl
                                        # print(i.date)
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
            if(total > maxProfit + 1): # and winrate>0.067
                print("total",total,"maxProfit",maxProfit)
                maxProfit = total
                maxTpVal = tpVal
                minAdrVal = '{0:.10f}'.format(adrVal)
            print('maxTpVal',str(maxTpVal),'maxProfit',str(maxProfit))
            riskOfRuin = calcRisk(tpVal,winrate,100)
            print("riskOfRuin",riskOfRuin)
            print("minAdrVal",minAdrVal)
            idx += 1

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