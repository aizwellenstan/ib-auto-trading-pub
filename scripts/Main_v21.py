from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from datetime import datetime as dt, timedelta
import pandas_datareader.data as web
import numpy as np
from scipy.signal import lfilter
import json
import requests
import talib
# from modules.aizfinviz import get_unusual_volume
from modules.aiztradingview import GetPerformance, GetProfit, GetPerformanceMore
from modules.trend import GetTrend
import math

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

def normalizeFloat(price, sample1):
    strFloat1 = str(sample1)
    dec = strFloat1[::-1].find('.')
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

cash = 0
total_cash = 0
def update_balance(*args):
    global cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    cash = float(cashDf['value'])
    print(cash)

def update_total_balance(*args):
    global total_cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'TotalCashBalance']
    # cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidation']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    print(total_cash)
    

risk = 0.00613800895 * 0.5548 * 0.675 * 0.46 #*0.4 #* 0.05 #0.79 #0.378 #0.06

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    opPrice = round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)
    print("getOP ",str(opPrice))
    return opPrice

class BracketOrderTwoTargets(NamedTuple):
    parent: Order
    takeProfit: Order
    stopLoss: Order

def bracketStopLimitOrderTwoTargets(c,
        action: str, quantity: float, stopPrice: float,
        limitPrice: float, takeProfitPrice1: float,
        stopLossPrice: float, **kwargs) -> BracketOrderTwoTargets:
    """
    Create a limit order that is bracketed by 2 take-profit orders and
    a stop-loss order. Submit the bracket like:

    Args:
        action: 'BUY' or 'SELL'.
        quantity: Size of order.
        stopPrice: Stop Price for stopLimit entry order
        limitPrice: Limit price of entry order.
        takeProfitPrice1: 1st Limit price of profit order.
        takeProfitPrice2: 2nd Limit price of profit order.
        stopLossPrice: Stop price of loss order.
        StopLimitOrder(action, totalQuantity, lmtPrice, stopPrice, **kwargs)
    """
    assert action in ('BUY', 'SELL')
    reverseAction = 'BUY' if action == 'SELL' else 'SELL'

    """
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')-1
    if action == 'SELL':
        limitPrice = round(limitPrice - ib.reqContractDetails(c)[0].minTick * 2,dps)
        stopPrice = round(stopPrice - ib.reqContractDetails(c)[0].minTick * 2,dps)
        stopLossPrice = round(stopLossPrice + ib.reqContractDetails(c)[0].minTick * 2,dps)
        takeProfitPrice1 = round(takeProfitPrice1 + ib.reqContractDetails(c)[0].minTick * 2,dps)
    elif action == 'BUY':
        limitPrice = round(limitPrice + ib.reqContractDetails(c)[0].minTick * 2,dps)
        stopPrice = round(stopPrice + ib.reqContractDetails(c)[0].minTick * 2,dps)
        stopLossPrice = round(stopLossPrice - ib.reqContractDetails(c)[0].minTick * 2,dps)
        takeProfitPrice1 = round(takeProfitPrice1 - ib.reqContractDetails(c)[0].minTick * 2,dps)
    """

    parent = StopLimitOrder(
        action, quantity, limitPrice, stopPrice,
        orderId=ib.client.getReqId(),
        transmit=False,
        outsideRth=False,
        tif="DAY",
        **kwargs)
    """
    parent = StopOrder(
        action, quantity, stopPrice,
        orderId=ib.client.getReqId(),
        transmit=False,
        outsideRth=True,
        **kwargs)
    """
    takeProfit1 = LimitOrder(
        action=reverseAction, totalQuantity=quantity, lmtPrice=takeProfitPrice1,
        orderId=ib.client.getReqId(),
        transmit=False,
        parentId=parent.orderId,
        outsideRth=False,
        tif="GTC",
        **kwargs)
    stopLoss = StopOrder(
        reverseAction, quantity, stopLossPrice,
        orderId=ib.client.getReqId(),
        transmit=True,
        parentId=parent.orderId,
        outsideRth = True,
        tif="GTC",
        **kwargs)
    return BracketOrderTwoTargets(parent, takeProfit1, stopLoss)

def handleBuyStop(contract, vol, op, sl, tp):
    limitPrice = normalizeFloat(op*1.003032140691, 0.01)
    high_bracket = bracketStopLimitOrderTwoTargets(
        contract,
        action='BUY', quantity=vol, stopPrice=op,
        limitPrice=limitPrice,
        takeProfitPrice1=tp,
        stopLossPrice=sl)
    for order in high_bracket:
        order_res = ib.placeOrder(contract=contract, order=order)
    print("Submitted "
            + contract.symbol
            + " BuyStop"
            + " vol " + str(vol)
            + " op " + str(op)
            + " sl " + str(sl)
            + " tp " + str(tp))

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

def isLetter(input):
    return ''.join(c for c in input if c.isalpha())

def plotLines(hisBarsD1, brk :int = 2, body :bool = False, tch :int = 4, level :int = 3, lineLife :int = 4):
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
    hisBarsLen :int = len(hisBarsD1)
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
        j :int
        a = len(pkArr)
        if (a > 1):
            pkArr.sort(reverse = True)
            i = 0
            while(i < a):
                j = i + 1
                while(j < a):
                    u = countSlopingCrosses(hisBarsD1, pkArr[i], pkArr[j], brk, 0, True, body)
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
                    u = countSlopingCrosses(hisBarsD1, trArr[i], trArr[j], brk, 0, False, body)
                    t = int([x.strip() for x in u.split(',')][0])
                    x = int([x.strip() for x in u.split(',')][1])
                    if( t > tch and x <= lineLife ):
                        slope = (hisBarsD1[trArr[i]].low - hisBarsD1[trArr[j]].low) / (trArr[i] - trArr[j])
                        slopeLower = slope
                    j += 1
                i += 1
    
        if(slopeUpper > 0 or slopeLower > 0):   return 1
        if(slopeUpper < 0 or slopeLower < 0):   return -1
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

def countSlopingCrosses(hisBarsD1, fromBar :int, toBar :int, brk :int, rng :float, pk :bool, body: bool):
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

# Yahoo query duration
end = dt.now()
start = end - timedelta(days=50)

duplicate_list = ['SOXL','PLTR','SPCE','CSCO','SHIP','ABNB','FIVE','ALF',
'OPINL','SDHY','PSTH','AEI','TUEM','VOLT','ALF','MCFE','PEB PRG','CRBU',
'NGTF','ISPI','MATW','KEYS','CAT','GPRO','SEM','BPOP','ACCD','TREX']
all_symbol_list = []
performanceSymList = []
profitSymList = []
gain_sym_list = []
vol_sym_list = []
active_sym_list = []
scanner = []
gap_list = []

inside_day = False

# ---List section---
stock_list = [] # List for open
# Tp List
stock_list_bias = []
stock_list_M30_turn_arround = []
stock_list_bp3_d1 = []

bias_over8_list = []
bias_over10_list = []

fillterPassedList = [] # List for M30 open check
talib_passed_list = []
talib_passed_list_d1_w1 = []
# ---end list section---

timeD = dt.strptime(str(ib.reqCurrentTime().date()), '%Y-%m-%d')
marketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)

IsTesting = False

def get_all():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        symbol = position.contract.symbol
        duplicate_list.append(symbol)

def remove_duplicate():
    global scanner
    get_all()
    scanner = [stock for stock in scanner if stock not in duplicate_list]

def checkPreMarketTime():
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    if(hour < 13 or (hour == 13 and min < 30)): return True
    return False

def checkHisBarsD1(contract, shift, hisBarsD1, hisBarsD1reverse, symbol):
    df = pd.DataFrame(hisBarsD1)
    hisBarsD1 = hisBarsD1reverse
    op = hisBarsD1[0].close
    print(symbol,op)
    if not checkOPLimit(op): return False

    # if symbol in jared: return True

    hisBarsM1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1 D',
        barSizeSetting='1 min', whatToShow='BID', useRTH=False)
    
    count = 0
    while len(hisBarsM1) < 1 and count < 10:
        ib.sleep(1)
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='1 D',
            barSizeSetting='1 min', whatToShow='BID', useRTH=False)
        count += 1

    hisBarsM1 = hisBarsM1[::-1]

    if not IsTesting:
        if not (
            hisBarsM1[0].close > hisBarsD1[1-shift].close
        ): return False

    # if hisBarsM1[0].close > cash/2/14: return False

    if (
        hisBarsD1[1-shift].close < hisBarsD1[180-shift].close * 0.92
    ): return False

    hisBarsD1closeArr = []
    for d in hisBarsD1:
        hisBarsD1closeArr.append(d.close)
    trend = GetTrend(hisBarsD1closeArr[1-shift:226-shift])

    if (
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ):
        highBreak = False
        if (
            hisBarsM1[0].close > hisBarsD1[1-shift].high and
            hisBarsM1[0].close > hisBarsD1[2-shift].high and
            hisBarsM1[0].close > hisBarsD1[50-shift].high
        ): highBreak = True

        if symbol not in jared and symbol not in gain_sym_list:
            if not highBreak:
                if (
                    hisBarsM1[1-shift].close < hisBarsD1[180].close * 1.48 and
                    trend < 0
                ): return False

    if (
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close > hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open and
        hisBarsD1[2-shift].open < hisBarsD1[3-shift].open
    ): return False

    if (
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        hisBarsD1[5-shift].close > hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        trend < 0
    ): return False

    if (
        hisBarsD1[5-shift].close > hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close > hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].open > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].high < hisBarsD1[2-shift].close and
        trend < 0
    ): return False

    if (
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open and
        trend < 0
    ): return False

    if (
        hisBarsD1[5-shift].close > hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close > hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        trend < 0
    ): return False

    if (
        hisBarsD1[10-shift].close > hisBarsD1[10-shift].open and
        hisBarsD1[9-shift].close > hisBarsD1[9-shift].open and
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        trend < 0
    ): return False

    if (
        hisBarsD1[9-shift].close > hisBarsD1[9-shift].open and
        hisBarsD1[8-shift].close < hisBarsD1[8-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[9-shift].close > hisBarsD1[9-shift].open and
        hisBarsD1[8-shift].close > hisBarsD1[8-shift].open and
        hisBarsD1[7-shift].close > hisBarsD1[7-shift].open and
        hisBarsD1[4-shift].close > hisBarsD1[4-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open
    ): return False

    if (
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        hisBarsD1[4-shift].open > hisBarsD1[5-shift].high and
        hisBarsD1[4-shift].close < hisBarsD1[5-shift].low and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[1-shift].low > hisBarsD1[2-shift].high and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[10-shift].close < hisBarsD1[10-shift].open and
        hisBarsD1[5-shift].close > hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close > hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[9-shift].close > hisBarsD1[9-shift].open and
        hisBarsD1[8-shift].close > hisBarsD1[8-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[8-shift].close > hisBarsD1[8-shift].open and
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open
    ): return False

    if (
        hisBarsD1[15-shift].close > hisBarsD1[15-shift].open and
        hisBarsD1[14-shift].close < hisBarsD1[14-shift].open and
        hisBarsD1[11-shift].close > hisBarsD1[11-shift].open and
        hisBarsD1[10-shift].close < hisBarsD1[10-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open
    ): return False

    if (
        hisBarsD1[10-shift].close > hisBarsD1[10-shift].open and
        hisBarsD1[7-shift].close > hisBarsD1[7-shift].open and
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[15-shift].close < hisBarsD1[15-shift].open and
        hisBarsD1[12-shift].close > hisBarsD1[12-shift].open and
        hisBarsD1[7-shift].close > hisBarsD1[7-shift].open and
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[20-shift].close > hisBarsD1[20-shift].open and
        hisBarsD1[19-shift].close > hisBarsD1[19-shift].open and
        hisBarsD1[7-shift].close > hisBarsD1[7-shift].open and
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[26-shift].close > hisBarsD1[26-shift].open and
        hisBarsD1[22-shift].close < hisBarsD1[22-shift].open and
        hisBarsD1[20-shift].close > hisBarsD1[20-shift].open and
        hisBarsD1[7-shift].close > hisBarsD1[7-shift].open and
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[12-shift].close < hisBarsD1[12-shift].open and
        hisBarsD1[11-shift].close < hisBarsD1[11-shift].open and
        hisBarsD1[9-shift].close < hisBarsD1[9-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    if (
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
    ): return False

    # doji
    if (
        hisBarsD1[12-shift].close > hisBarsD1[12-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        (
            (hisBarsD1[12-shift].high - hisBarsD1[12-shift].close) /
            (hisBarsD1[12-shift].high - hisBarsD1[12-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[20-shift].close > hisBarsD1[20-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        (
            (hisBarsD1[20-shift].high - hisBarsD1[20-shift].close) /
            (hisBarsD1[20-shift].high - hisBarsD1[20-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[21-shift].close > hisBarsD1[21-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        (
            (hisBarsD1[21-shift].high - hisBarsD1[21-shift].close) /
            (hisBarsD1[21-shift].high - hisBarsD1[21-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[26-shift].close > hisBarsD1[26-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        (
            (hisBarsD1[26-shift].high - hisBarsD1[26-shift].close) /
            (hisBarsD1[26-shift].high - hisBarsD1[26-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[71-shift].close > hisBarsD1[71-shift].open and
        hisBarsD1[1-shift].close < hisBarsD1[1-shift].open and
        (
            (hisBarsD1[71-shift].high - hisBarsD1[71-shift].close) /
            (hisBarsD1[71-shift].high - hisBarsD1[71-shift].low)
        ) > 0.55
    ): return False
    
    if (
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[6-shift].high - hisBarsD1[6-shift].close) /
            (hisBarsD1[6-shift].high - hisBarsD1[6-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[9-shift].close > hisBarsD1[9-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[9-shift].high - hisBarsD1[9-shift].close) /
            (hisBarsD1[9-shift].high - hisBarsD1[9-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[12-shift].close > hisBarsD1[12-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[12-shift].high - hisBarsD1[12-shift].close) /
            (hisBarsD1[12-shift].high - hisBarsD1[12-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[16-shift].close > hisBarsD1[16-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[16-shift].high - hisBarsD1[16-shift].close) /
            (hisBarsD1[16-shift].high - hisBarsD1[16-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[22-shift].close > hisBarsD1[22-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[22-shift].high - hisBarsD1[22-shift].close) /
            (hisBarsD1[22-shift].high - hisBarsD1[22-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[31-shift].close > hisBarsD1[31-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[31-shift].high - hisBarsD1[31-shift].close) /
            (hisBarsD1[31-shift].high - hisBarsD1[31-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[43-shift].close > hisBarsD1[43-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[43-shift].high - hisBarsD1[43-shift].close) /
            (hisBarsD1[43-shift].high - hisBarsD1[43-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[52-shift].close > hisBarsD1[52-shift].open and
        hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
        (
            (hisBarsD1[52-shift].high - hisBarsD1[52-shift].close) /
            (hisBarsD1[52-shift].high - hisBarsD1[52-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[38-shift].close > hisBarsD1[38-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        (
            (hisBarsD1[38-shift].high - hisBarsD1[38-shift].close) /
            (hisBarsD1[38-shift].high - hisBarsD1[38-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[47-shift].close > hisBarsD1[47-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        (
            (hisBarsD1[47-shift].high - hisBarsD1[47-shift].close) /
            (hisBarsD1[47-shift].high - hisBarsD1[47-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[54-shift].close > hisBarsD1[54-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        (
            (hisBarsD1[54-shift].high - hisBarsD1[54-shift].close) /
            (hisBarsD1[54-shift].high - hisBarsD1[54-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[68-shift].close > hisBarsD1[68-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        (
            (hisBarsD1[68-shift].high - hisBarsD1[68-shift].close) /
            (hisBarsD1[68-shift].high - hisBarsD1[68-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[73-shift].close > hisBarsD1[73-shift].open and
        hisBarsD1[3-shift].close < hisBarsD1[3-shift].open and
        (
            (hisBarsD1[73-shift].high - hisBarsD1[73-shift].close) /
            (hisBarsD1[73-shift].high - hisBarsD1[73-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[19-shift].close > hisBarsD1[19-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        (
            (hisBarsD1[19-shift].high - hisBarsD1[19-shift].close) /
            (hisBarsD1[19-shift].high - hisBarsD1[19-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[31-shift].close > hisBarsD1[31-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        (
            (hisBarsD1[31-shift].high - hisBarsD1[31-shift].close) /
            (hisBarsD1[31-shift].high - hisBarsD1[31-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[55-shift].close > hisBarsD1[55-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        (
            (hisBarsD1[55-shift].high - hisBarsD1[55-shift].close) /
            (hisBarsD1[55-shift].high - hisBarsD1[55-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[56-shift].close > hisBarsD1[56-shift].open and
        hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
        (
            (hisBarsD1[56-shift].high - hisBarsD1[56-shift].close) /
            (hisBarsD1[56-shift].high - hisBarsD1[56-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[16-shift].close > hisBarsD1[16-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        (
            (hisBarsD1[16-shift].high - hisBarsD1[16-shift].close) /
            (hisBarsD1[16-shift].high - hisBarsD1[16-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[31-shift].close > hisBarsD1[31-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        (
            (hisBarsD1[31-shift].high - hisBarsD1[31-shift].close) /
            (hisBarsD1[31-shift].high - hisBarsD1[31-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[41-shift].close > hisBarsD1[41-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        (
            (hisBarsD1[41-shift].high - hisBarsD1[41-shift].close) /
            (hisBarsD1[41-shift].high - hisBarsD1[41-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[52-shift].close > hisBarsD1[52-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        (
            (hisBarsD1[52-shift].high - hisBarsD1[52-shift].close) /
            (hisBarsD1[52-shift].high - hisBarsD1[52-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[123-shift].close > hisBarsD1[123-shift].open and
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        (
            (hisBarsD1[123-shift].high - hisBarsD1[123-shift].close) /
            (hisBarsD1[123-shift].high - hisBarsD1[123-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[130-shift].close > hisBarsD1[130-shift].open and
        hisBarsD1[6-shift].close < hisBarsD1[6-shift].open and
        (
            (hisBarsD1[130-shift].high - hisBarsD1[130-shift].close) /
            (hisBarsD1[130-shift].high - hisBarsD1[130-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        (
            (hisBarsD1[3-shift].high - hisBarsD1[3-shift].close) /
            (hisBarsD1[3-shift].high - hisBarsD1[3-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[46-shift].close > hisBarsD1[46-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        (
            (hisBarsD1[46-shift].high - hisBarsD1[46-shift].close) /
            (hisBarsD1[46-shift].high - hisBarsD1[46-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[164-shift].close > hisBarsD1[164-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        (
            (hisBarsD1[164-shift].high - hisBarsD1[164-shift].close) /
            (hisBarsD1[164-shift].high - hisBarsD1[164-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[209-shift].close > hisBarsD1[209-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        (
            (hisBarsD1[209-shift].high - hisBarsD1[209-shift].close) /
            (hisBarsD1[209-shift].high - hisBarsD1[209-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[14-shift].close > hisBarsD1[14-shift].open and
        hisBarsD1[9-shift].close < hisBarsD1[9-shift].open and
        (
            (hisBarsD1[14-shift].high - hisBarsD1[14-shift].close) /
            (hisBarsD1[14-shift].high - hisBarsD1[14-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[6-shift].close > hisBarsD1[6-shift].open and
        hisBarsD1[11-shift].close < hisBarsD1[11-shift].open and
        (
            (hisBarsD1[6-shift].high - hisBarsD1[6-shift].close) /
            (hisBarsD1[6-shift].high - hisBarsD1[6-shift].low)
        ) > 0.55
    ): return False

    if (
        hisBarsD1[85-shift].close > hisBarsD1[85-shift].open and
        hisBarsD1[11-shift].close < hisBarsD1[11-shift].open and
        (
            (hisBarsD1[85-shift].high - hisBarsD1[85-shift].close) /
            (hisBarsD1[85-shift].high - hisBarsD1[85-shift].low)
        ) > 0.55
    ): return False

    rangeHigh = max(hisBarsD1closeArr[1-shift:18-shift])
    rangeLow = min(hisBarsD1closeArr[1-shift:18-shift])

    if (
        (rangeHigh - rangeLow) / hisBarsD1[1-shift].close < 0.053
    ): return False

    if (
        hisBarsD1[7-shift].close > hisBarsD1[7-shift].open and
        hisBarsD1[5-shift].close < hisBarsD1[5-shift].open and
        hisBarsD1[6-shift].open < hisBarsD1[7-shift].low and
        (
            hisBarsD1[6-shift].open - hisBarsD1[6-shift].close
            > hisBarsD1[1-shift].close * 0.05
        )
    ): return False

    if (
        hisBarsD1[9-shift].close < hisBarsD1[9-shift].open and
        hisBarsD1[7-shift].close < hisBarsD1[7-shift].open and
        hisBarsD1[7-shift].open < hisBarsD1[8-shift].close * 0.95
    ): return False

    if (
        hisBarsD1[20-shift].close > hisBarsD1[20-shift].open and
        hisBarsD1[19-shift].close > hisBarsD1[19-shift].open and
        hisBarsD1[17-shift].close < hisBarsD1[17-shift].open and
        hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
        hisBarsD1[2-shift].close > hisBarsD1[2-shift].open
    ): return False
    

    if hisBarsM1[0].close > 100:
        df = df.assign(h1l1=df.high/df.low)
        df = df.assign(nextOpen=df.open.shift(-1))
        df = df.assign(nextClose=df.close.shift(-1))
        bearCandle = df['nextClose'] < df['nextOpen']
        avgH1L1 = df.loc[bearCandle, 'h1l1'].mean()
        H1L1 = hisBarsD1[1-shift].high / hisBarsD1[1-shift].low
        if (
            H1L1 > avgH1L1
        ): return False
    
    print(symbol,"passed")
    return True

def checkScanner(shift,symbol):
    try:
        # today = ib.reqCurrentTime().today()
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
        #         if date >= today and today <= date_end:
        #             if direction == 'Sell': return False
        #         else:   break
        # try:
        #     dataReader = web.get_quote_yahoo(symbol)
        #     marketCap = 0
        #     if('marketCap' in dataReader):
        #         marketCap = dataReader['marketCap'][0]
        #     # if(marketCap < 239829535): return False
        #     # if(marketCap < 19430771126): return False
        #     if(marketCap < 47305439): return False
        #     volDf = web.DataReader(symbol, "yahoo", start, end)
        #     volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
        #     # if(volavg < 149604): return False
        #     # if(volavg < 32282961): return False
        #     if(volavg < 153889): return False
        # except:
        #     pass

        # Pre check bars before marketopen
        contract = Stock(symbol, 'SMART', 'USD')
        hisBarsD1 = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='360 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        count = 0
        while len(hisBarsD1) < 1 and count < 10:
            ib.sleep(1)
            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            count += 1

        if len(hisBarsD1) < 181: return False
        hisBarsD1reverse = hisBarsD1[::-1]

        if IsTesting: shift = 0
        if not checkHisBarsD1(contract,shift,hisBarsD1,hisBarsD1reverse,symbol):
            return False
        elif symbol not in stock_list:
            stock_list.append(
                {
                    's':symbol,
                    'close1':hisBarsD1reverse[1-shift].close
                }
            )
        return True
    except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)

def get_all_symbol_list():
    global all_symbol_list
    symbol_df = pd.read_csv (r'./backtest/csv/livetradersSym.csv')
    symbol_df.drop
    sym_list = json.loads(symbol_df.to_json(orient = 'records'))
    shift = 0
    if checkPreMarketTime(): shift = 1
    for sym in sym_list:
        s = sym['symbol']
        if(checkScanner(shift,s)):
            all_symbol_list.append(s)

def getPerformanceSymList():
    global performanceSymList
    performanceSymList = GetPerformance(-8)

def getPerformanceMoreSymList():
    global performanceSymList
    performanceSymList = GetPerformanceMore(-8)

def getProfitSymList():
    global profitSymList
    profitSymList = GetProfit()
        
# Scanner
def get_scanner():
    global scanner, gain_sym_list, vol_sym_list, active_sym_list
    gain_sym_list = []
    vol_sym_list = []
    active_sym_list = []
    hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='HIGH_OPEN_GAP',
                                        belowPrice=total_cash/2*0.83657741748*0.21,
                                        abovePrice=3, #18.97 #'0.97',
                                        aboveVolume=56208,#500000 #139303 #621428 #316859 #6664151  # <1407
                                        stockTypeFilter='CORP'
                                        )
    hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                            locationCode='STK.US.MAJOR',
                                            scanCode='HOT_BY_VOLUME', #'HOT_BY_VOLUME',
                                            belowPrice=cash/2/12,
                                            abovePrice=3, #18.97 #'0.97',
                                            aboveVolume=56208, #316859 #6664151  # <1407
                                            stockTypeFilter='CORP'
                                            )
    hot_stk_by_active = ScannerSubscription(instrument='STK',
                                            locationCode='STK.US.MAJOR',
                                            scanCode='MOST_ACTIVE', #'HOT_BY_VOLUME',
                                            belowPrice=cash/2/12,
                                            abovePrice=3, #18.97 #'0.97',
                                            aboveVolume=56208,#500000 #139303 #621428 #316859 #6664151  # <1407
                                            stockTypeFilter='CORP'
                                            )
    gain_list = ib.reqScannerData(hot_stk_by_gain, [])
    vol_list = ib.reqScannerData(hot_stk_by_volume, [])
    active_list = ib.reqScannerData(hot_stk_by_active, [])
    for stock in gain_list:
        symbol = stock.contractDetails.contract.symbol
        gain_sym_list.append(symbol)
    for stock in vol_list:
        symbol = stock.contractDetails.contract.symbol
        vol_sym_list.append(symbol)
    for stock in active_list:
        symbol = stock.contractDetails.contract.symbol
        active_sym_list.append(symbol)

    for sym in all_symbol_list:
        scanner.append(sym)

    for sym in performanceSymList:
        if sym not in scanner:
            scanner.append(sym)

    # for sym in gain_sym_list:
    #     if isLetter(sym):
    #         if sym not in scanner and sym in profitSymList:
    #             scanner.append(sym)
    # for sym in vol_sym_list:
    #     if isLetter(sym):
    #         if sym not in scanner:
    #             scanner.append(sym)
    # for sym in active_sym_list:
    #     if isLetter(sym):
    #         if sym not in scanner and sym in profitSymList:
    #             scanner.append(sym)
    remove_duplicate()
    print('gain',gain_sym_list,len(gain_sym_list))
    print('vol',vol_sym_list,len(vol_sym_list))
    print('active',active_sym_list,len(active_sym_list))
    print('scanner',scanner)

def checkOPLimit(op):
    sl = op - 0.14
    if op > 16.5:
        sl = op * 0.9930862018
    if op > 100:
        sl = op * 0.9977520318
    if abs(op - sl) < 0.01: return False
    vol = int(total_cash * risk / (op - sl))
    volLimit = 7
    if op >= 14: volLimit = 4
    if(
        (op >= 3)
        and op < total_cash*0.83657741748/volLimit
        and vol >= volLimit
    ): return True

    return False

def check_for_pre_open():
    try:
        shift = 0
        if checkPreMarketTime(): shift = 1
        for sym in scanner:
            if sym not in all_symbol_list:
                checkScanner(shift,sym)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
    print("スキャンは終わりました！,GTHF")

jared = []
def check_for_jared():
    try:
        shift = 0
        if checkPreMarketTime(): shift = 1
        for sym in jared:
            if sym not in scanner:
                checkScanner(shift,sym)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
    print("スキャンは終わりました！,GTHF")

def getPreMarketRange(contract):
    hisBarsM1 = ib.reqHistoricalData(
        contract, endDateTime=marketOpenTime, durationStr='5400 S',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)

    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=4):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=marketOpenTime, durationStr='5400 S',
            barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
        maxTrys += 1

    preMaxHigh = 0
    preMinLow = 9999

    for i in hisBarsM1:
        if i.high > preMaxHigh:
            preMaxHigh = i.high
        if i.low < preMinLow:
            preMinLow = i.low
    return preMaxHigh, preMinLow

oppened_list = []
def check_for_open():
    cost = 0
    # stock_list = [{'s': 'VTNR', 'close1': 8.6}, {'s': 'HDSN', 'close1': 3.84}, {'s': 'AMC', 'close1': 40.27}, {'s': 'NURO', 'close1': 18.12}, {'s': 'FISV', 'close1': 111.38}]
    for stock in stock_list:
        try:
            symbol = stock['s']
            if symbol in oppened_list: continue
            contract = Stock(symbol, 'SMART', 'USD')

            spread = 0.0
            ticker=ib.reqMktData(contract, '', False, False)
            ib.sleep(2)
            ask = ticker.ask
            bid = ticker.bid
            retryCount = 0

            if not IsTesting:
                while (math.isnan(bid) or bid < 0) and retryCount < 8:
                    print("retry")
                    ticker=ib.reqMktData(contract, '', False, False)
                    ib.sleep(3)
                    ask = ticker.ask
                    bid = ticker.bid
                    retryCount += 1
            # if ticker.volume*100 < 56208 or math.isnan(ticker.volume): continue
            # if math.isnan(ticker.volume): continue
            spread = ask-bid

            if IsTesting:
                hisBarsD1Ask = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

                hisBarsD1Bid = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 day', whatToShow='BID', useRTH=True)

                ask = hisBarsD1Ask[-1].open
                bid = hisBarsD1Bid[-1].open

                spread = ask-bid
                print(ask,bid,spread)

            opM30 = normalizeFloat(getOP(contract, bid), 0.01)
            print(symbol,opM30)
            if opM30 < stock['close1']: continue
            if symbol not in jared:
                if opM30 > stock['close1'] * 1.115132275: continue
            if opM30 < stock['close1'] * 1.003067754: continue

            preMaxHigh, preMinLow = getPreMarketRange(contract)
            if preMaxHigh - preMinLow < 0.01: continue

            print("preMaxHigh",preMaxHigh,"preMinLow",preMinLow)
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            if(ask>0 and bid>0):
                op = normalizeFloat(preMaxHigh + 0.01 * 7, 0.01)
                sl = preMinLow
                if op > 16.5:
                    sl = normalizeFloat(op * 0.9930862018, 0.01)
                if op > 100:
                    sl = normalizeFloat(op * 0.9977520318, 0.01)
                vol = int(total_cash*risk/(op-sl))
                volLimit = 7
                if op >= 14: volLimit = 4
                if(vol >= volLimit):
                    tpVal = 2.42 #3.06 #3.69 #3.02 #3.444444444 #2.08 #1.15137614678 #4.4
                    tp = op + (op-sl) * tpVal
                    tp = normalizeFloat(tp, 0.01)
                    spread = 0
                    spread = ask-bid
                    spreadPercent = 0.32
                    spreadFixed = 2.1
                    print(symbol,"spreadPercent",spread/(op - sl))
                    if (spread < (op - sl) * spreadPercent and spread < spreadFixed):
                        log("BuyStop " + symbol
                                + " vol " + str(vol)
                                + " op " + str(op)
                                + " sl " + str(sl)
                                + " tp " + str(tp))
                        cost += op*vol
                        diff = 0.00063717746183
                        if(abs((op-sl)/sl)<diff or abs(op-sl)<=0.01):
                            print("sl too close")
                        else:
                            if not IsTesting:
                                handleBuyStop(contract,vol,op,sl,tp)
            else:
                print("ask/bid err ",ask," ",bid)
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("cost",cost)
    print("Open終わりました！,GTHF")

def cancelUntriggered():
    oos = list(ib.openOrders())
    ib.client.reqAllOpenOrders()  # issue reqAllOpenOrders() directly to IB API, this is a non blocking call
    dummy = ib.reqOpenOrders()    # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
    aoos = list(ib.openOrders())  # the orders received from issuing reqAllOpenOrders() are correctly captured
    for oo in aoos:
        print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
        if oo.orderType == "STP LMT":
            ib.cancelOrder(oo)

keepOpenList = []
def close_all():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        contract = position.contract
        if(contract.symbol not in keepOpenList): continue
        if position.position > 0: # Number of active Long positions
            action = 'Sell' # to offset the long positions
        elif position.position < 0: # Number of active Short positions
            action = 'Buy' # to offset the short positions
        else:
            assert False
        totalQuantity = abs(position.position)
        order = MarketOrder(action=action, totalQuantity=totalQuantity)
        trade = ib.placeOrder(contract, order)
        print(f'Flatten Position: {action} {totalQuantity} {contract.localSymbol}')
        assert trade in ib.trades(), 'trade not listed in ib.trades'

def close_all_limit():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        print(position)
        contract = position.contract
        if(contract.symbol in keepOpenList): continue
        ticker=ib.reqMktData(contract, '', False, False)
        ib.sleep(2)
        ask = ticker.ask
        bid = ticker.bid
        retryCount = 0
        while (math.isnan(bid) or bid < 0) and retryCount < 10:
            print("retry")
            ticker=ib.reqMktData(contract, '', False, False)
            ib.sleep(3)
            ask = ticker.ask
            bid = ticker.bid
            retryCount += 1
        print("symbol ",contract.symbol," bid " +str(bid)," ask ",str(ask))
        if position.position > 0: # Number of active Long positions
            action = 'Sell' # to offset the long positions
        elif position.position < 0: # Number of active Short positions
            action = 'Buy' # to offset the short positions
        else:
            assert False
        if not  (math.isnan(bid) or bid < 0):
            totalQuantity = abs(position.position)
            limitPrice = normalizeFloat(bid * (2-1.003032140691), 0.01)
            order = StopLimitOrder(
                action=action, totalQuantity=totalQuantity, 
                lmtPrice=limitPrice, stopPrice = bid,
                outsideRth=False,
                tif="DAY")
            trade = ib.placeOrder(contract, order)
            print(f'Flatten Position: {action} {totalQuantity} {contract.localSymbol}')
            assert trade in ib.trades(), 'trade not listed in ib.trades'

def main():
    global IsTesting
    IsTesting = False
    update_total_balance()
    update_balance()
    # getPerformanceMoreSymList()
    # getProfitSymList()
    # get_scanner()
    # remove_duplicate()
    # print(scanner)
    # check_for_pre_open()
    # check_for_jared()
    # print(stock_list)

    # check_for_open()

    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        min = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second

        if(hour == 12 and min == 56 and sec == 0):
            update_total_balance()
            update_balance()
            # getPerformanceSymList()
            getPerformanceMoreSymList()
            getProfitSymList()
            get_scanner()
            remove_duplicate()
            print(scanner)
            check_for_pre_open()
            check_for_jared()
            print(stock_list)

        if(hour == 13 and min == 30 and sec == 10):
            check_for_open()

        # EOD Cancel
        if(hour == 14 and min == 25 and sec == 0):
            cancelUntriggered()

        # EOD Limit
        if(hour == 14 and min == 55 and sec == 0):
            close_all_limit()
            
        # EOD
        if(hour == 14 and min == 56 and sec == 0):
            close_all()

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