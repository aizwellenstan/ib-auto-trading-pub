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
import math

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=4)

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

cash = 0
def update_balance(*args):
    global cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    cash = float(cashDf['value'])
    print(cash)

risk = 0.00613800895 * 0.18549364406 #0.79 #0.378 #0.06

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    opPrice = round(price + ib.reqContractDetails(c)[0].minTick * 2,dps)
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
    limitPrice = normalizeFloat(op*1.003032140691,sl,tp)
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

duplicate_list = ['SOXL','PLTR','SPCE','CSCO','SHIP','ABNB','FIVE','ALF','OPINL','SDHY']
all_symbol_list = []
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

def get_all():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        symbol = position.contract.symbol
        duplicate_list.append(symbol)

def remove_duplicate():
    global scanner
    # get_all()
    scanner = [stock for stock in scanner if stock not in duplicate_list]

def checkPreMarketTime():
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    if(hour < 13 or (hour == 13 and min < 30)): return True
    return False

def checkHisBarsD1(hisBarsD1, symbol):
    op = hisBarsD1[0].close
    print(symbol,op)
    if not check_op_limit(op): return False

    i = 0
    if checkPreMarketTime(): i = 1

    # 8b dwn
    if(
        hisBarsD1[9-i].close < hisBarsD1[9-i].open
        and hisBarsD1[8-i].close < hisBarsD1[8-i].open
        and hisBarsD1[7-i].close < hisBarsD1[7-i].open
        and hisBarsD1[6-i].close < hisBarsD1[6-i].open
        and hisBarsD1[5-i].close < hisBarsD1[5-i].open
        and hisBarsD1[4-i].close < hisBarsD1[4-i].open
        and hisBarsD1[3-i].close < hisBarsD1[3-i].open
        and hisBarsD1[2-i].close < hisBarsD1[2-i].open
    ):  return False

    # 5b dwn
    if(
        hisBarsD1[5-i].close < hisBarsD1[5-i].open
        and hisBarsD1[4-i].close < hisBarsD1[4-i].open
        and hisBarsD1[3-i].close < hisBarsD1[3-i].open
        and hisBarsD1[2-i].close < hisBarsD1[2-i].open
        and hisBarsD1[1-i].close < hisBarsD1[1-i].open
        and hisBarsD1[1-i].high > hisBarsD1[2-i].high
    ):  return False

    # Turn Arround
    if(
        hisBarsD1[8-i].close > hisBarsD1[8-i].open
        and hisBarsD1[7-i].close > hisBarsD1[7-i].open
        and hisBarsD1[6-i].close > hisBarsD1[6-i].open
        and hisBarsD1[5-i].close > hisBarsD1[5-i].open
        and hisBarsD1[4-i].close < hisBarsD1[4-i].open
        and hisBarsD1[3-i].close < hisBarsD1[3-i].open
        and hisBarsD1[2-i].close < hisBarsD1[2-i].open
        and hisBarsD1[1-i].close < hisBarsD1[1-i].open
    ):  return False

    # Topping Tails
    if(
        hisBarsD1[1-i].high - hisBarsD1[1-i].close
        > (hisBarsD1[1-i].high - hisBarsD1[1-i].low) * 0.51
        and hisBarsD1[2-i].high - hisBarsD1[2-i].close
            > (hisBarsD1[2-i].high - hisBarsD1[2-i].low) * 0.51
        and hisBarsD1[3-i].high - hisBarsD1[3-i].close
            > (hisBarsD1[3-i].high - hisBarsD1[3-i].low) * 0.51
        and hisBarsD1[4-i].high - hisBarsD1[4-i].close
            > (hisBarsD1[4-i].high - hisBarsD1[4-i].low) * 0.51
        and hisBarsD1[5-i].high - hisBarsD1[5-i].close
            > (hisBarsD1[5-i].high - hisBarsD1[5-i].low) * 0.51
        and hisBarsD1[6-i].high - hisBarsD1[6-i].close
            > (hisBarsD1[6-i].high - hisBarsD1[6-i].low) * 0.51
    ):  return False

    return True

def checkScanner(symbol):
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
        try:
            dataReader = web.get_quote_yahoo(symbol)
            marketCap = 0
            if('marketCap' in dataReader):
                marketCap = dataReader['marketCap'][0]
            # if(marketCap < 239829535): return False
            if(marketCap < 19430771126): return False
            volDf = web.DataReader(symbol, "yahoo", start, end)
            volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
            # if(volavg < 149604): return False
            if(volavg < 32282961): return False
        except:
            pass

        # Pre check bars before marketopen
        if checkPreMarketTime():
            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            hisBarsD1 = hisBarsD1[::-1]
            if not checkHisBarsD1(hisBarsD1,symbol): return False
        return True
    except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)

def get_all_symbol_list():
    global all_symbol_list
    symbol_df = pd.read_csv (r'./backtest/csv/livetradersSym.csv')
    symbol_df.drop
    sym_list = json.loads(symbol_df.to_json(orient = 'records'))
    for sym in sym_list:
        s = sym['symbol']
        if(checkScanner(s)):
            all_symbol_list.append(s)
        
# Scanner
def get_scanner():
    global scanner, gain_sym_list, vol_sym_list, active_sym_list
    gain_sym_list = []
    vol_sym_list = []
    active_sym_list = []
    hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='TOP_PERC_GAIN',
                                        # belowPrice=cash/5,
                                        abovePrice=18.97, #'0.97',
                                        aboveVolume=500000,#500000 #139303 #621428 #316859 #6664151  # <1407
                                        stockTypeFilter='CORP'
                                        )
    # hot_stk_by_volume = ScannerSubscription(instrument='STK',
    #                                         locationCode='STK.US.MAJOR',
    #                                         scanCode='HOT_BY_VOLUME', #'HOT_BY_VOLUME',
    #                                         # belowPrice=cash/5,
    #                                         abovePrice=18.97, #'0.97',
    #                                         aboveVolume=56208, #316859 #6664151  # <1407
    #                                         stockTypeFilter='CORP'
    #                                         )
    hot_stk_by_active = ScannerSubscription(instrument='STK',
                                            locationCode='STK.US.MAJOR',
                                            scanCode='MOST_ACTIVE', #'HOT_BY_VOLUME',
                                            # belowPrice=cash/5,
                                            abovePrice=18.97, #'0.97',
                                            aboveVolume=500000,#500000 #139303 #621428 #316859 #6664151  # <1407
                                            stockTypeFilter='CORP'
                                            )
    gain_list = ib.reqScannerData(hot_stk_by_gain, [])
    # vol_list = ib.reqScannerData(hot_stk_by_volume, [])
    active_list = ib.reqScannerData(hot_stk_by_active, [])
    for stock in gain_list:
        symbol = stock.contractDetails.contract.symbol
        gain_sym_list.append(symbol)
    # for stock in vol_list:
    #     symbol = stock.contractDetails.contract.symbol
    #     vol_sym_list.append(symbol)
    for stock in active_list:
        symbol = stock.contractDetails.contract.symbol
        active_sym_list.append(symbol)
    scanner = all_symbol_list
    for sym in gain_sym_list:
        if sym not in scanner:
            scanner.append(sym)
    # for sym in vol_sym_list:
    #     if sym not in scanner:
    #         scanner.append(sym)
    for sym in active_sym_list:
        if sym not in scanner:
            scanner.append(sym)
    remove_duplicate()
    print('gain',gain_sym_list)
    print('vol',vol_sym_list)
    print('active',active_sym_list)
    print('scanner',scanner)

def check_op_limit(op):
    sl = op * 0.9937888199
    if op > 18.97:
        sl = op * 0.9947503029
    if (op > 100):
        sl = op * 0.998584196
    if abs(op - sl) < 0.01: return False
    vol = int(cash*risk/(op-sl))

    volLimit = 5
    if op>=100: volLimit=2
    elif op>=50: volLimit=3
    else: volLimit=5
    if(
        (op>=16.5)
        and op < cash*0.83657741748/5
        and vol >= volLimit
    ): return True
    return False

def check_for_pre_open():
    for symbol in scanner:
        try:
            # try:
            #     if not get_unusual_volume(symbol):  continue
            #     else: print("Unusual Volume",symbol)
            # except: pass
            if symbol not in all_symbol_list:
                if not checkScanner(symbol): continue

            contract = Stock(symbol, 'SMART', 'USD')

            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """

            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            if(len(hisBarsD1) < 330): continue
            df = pd.DataFrame(hisBarsD1)
            hisBarsD1 = hisBarsD1[::-1]

            op = hisBarsD1[0].open
            if not check_op_limit(op): continue

            # 8b dwn
            if(
                hisBarsD1[9].close < hisBarsD1[9].open
                and hisBarsD1[8].close < hisBarsD1[8].open
                and hisBarsD1[7].close < hisBarsD1[7].open
                and hisBarsD1[6].close < hisBarsD1[6].open
                and hisBarsD1[5].close < hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
            ): continue

            # 5b dwn
            if(
                hisBarsD1[5].close < hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
                and hisBarsD1[1].high > hisBarsD1[2].high
            ): continue

            # Turn Arround
            if(
                hisBarsD1[8].close > hisBarsD1[8].open
                and hisBarsD1[7].close > hisBarsD1[7].open
                and hisBarsD1[6].close > hisBarsD1[6].open
                and hisBarsD1[5].close > hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
            ): continue

            # Topping Tails
            if(
                hisBarsD1[1].high - hisBarsD1[1].close
                > (hisBarsD1[1].high - hisBarsD1[1].low) * 0.51
                and hisBarsD1[2].high - hisBarsD1[2].close
                    > (hisBarsD1[2].high - hisBarsD1[2].low) * 0.51
                and hisBarsD1[3].high - hisBarsD1[3].close
                    > (hisBarsD1[3].high - hisBarsD1[3].low) * 0.51
                and hisBarsD1[4].high - hisBarsD1[4].close
                    > (hisBarsD1[4].high - hisBarsD1[4].low) * 0.51
                and hisBarsD1[5].high - hisBarsD1[5].close
                    > (hisBarsD1[5].high - hisBarsD1[5].low) * 0.51
                and hisBarsD1[6].high - hisBarsD1[6].close
                    > (hisBarsD1[6].high - hisBarsD1[6].low) * 0.51
            ): continue

            hisBarsD1closeArr = []
            for d in hisBarsD1:
                hisBarsD1closeArr.append(d.close)
            
            sma25D1 = sma(hisBarsD1closeArr[1:26], 25)

            if not (
                hisBarsD1[0].open <= hisBarsD1[1].close * 0.91821988114
                and hisBarsD1[0].open < sma25D1
            ):
                if(
                    hisBarsD1[0].open <= hisBarsD1[1].close
                    or hisBarsD1[0].open > hisBarsD1[1].close * 1.14
                ):  continue

            if symbol not in stock_list:
                stock_list.append(symbol)

        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("スキャンは終わりました！,GTHF")

def check_for_open():
    cost = 0
    for stock in stock_list:
        try:
            symbol = stock
            contract = Stock(symbol, 'SMART', 'USD')

            spread = 0.0

            ticker=ib.reqMktData(contract, '', False, False)
            ib.sleep(2)
            ask = ticker.ask
            bid = ticker.bid
            retryCount = 0
            while (math.isnan(bid) or bid < 0) and retryCount < 1:
                print("retry")
                ticker=ib.reqMktData(contract, '', False, False)
                ib.sleep(3)
                ask = ticker.ask
                bid = ticker.bid
                retryCount += 1
            # if ticker.volume < 139303: 
            if ticker.volume < 56208: continue
            ask = ticker.ask
            bid = ticker.bid
            spread = ask-bid

            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            if(ask>0 and bid>0):
                hisBarsD1 = ib.reqHistoricalData(
                    contract, endDateTime='', durationStr='5 D',
                    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                hisBarsD1 = hisBarsD1[::-1]

                open = hisBarsD1[0].open

                op = normalizeFloat(getOP(contract, bid), ask, bid)
                if not check_op_limit(op): continue
                sl = normalizeFloat(op * 0.9937888199, ask, bid)
                if op > 18.97:
                    sl = normalizeFloat(op * 0.9947503029, ask, bid)
                if (op > 100):
                    sl = normalizeFloat(op * 0.998584196, ask, bid)
                # if(op > 100):
                #     slMin = op - 1.167
                # elif(op >= 50 and op < 100):
                #     slMin = op - 0.577
                # elif(op >= 10 and op<50):
                #     slMin = op - 0.347
                # elif(op < 10):
                #     slMin = op - 0.145
                # sl = max(slMin, sl)
                # sl = normalizeFloat(sl, ask, bid)
                if(sl != 0 and op != sl):
                    tpVal = 5.7
                    if symbol in bias_over8_list:    tpVal = 3.5
                    if symbol in bias_over10_list:    tpVal = 10.4
                    # tp = op + (op-sl) * tpVal #2.8 #4.496913030998851894374282433984 #2.79
                    tp = normalizeFloat(open * 1.062712388,op,sl)
                    if op < 100:
                        tp = normalizeFloat(open * 1.057407407,op,sl)
                    if op < 55:
                        tp = normalizeFloat(open * 1.0299,op,sl)
                    # tp = normalizeFloat(tp, ask, bid)
                    if abs(tp-op)/abs(op-sl) < 1.022222222: continue
                    # volMax = int(cash*risk/op)
                    vol = int(cash*risk/(op-sl))
                    # if(vol>volMax): vol=volMax
                    volLimit = 5
                    if op>=100: volLimit=2
                    elif op>=50: volLimit=3
                    else: volLimit=5
                    if(vol>=volLimit):
                        spread = 0
                        spread = ask-bid
                        if (spread < (op - sl) * 0.27):
                            log("BuyStop " + symbol
                                    + " vol " + str(vol)
                                    + " op " + str(op)
                                    + " sl " + str(sl)
                                    + " tp " + str(tp)
                                    + " tickerVol " + str(ticker.volume))
                            cost += op*vol
                            diff = 0.00063717746183
                            if(abs((op-sl)/sl)<diff or abs(op-sl)<=0.01):
                                print("sl too close")
                            else:
                                handleBuyStop(contract,vol,op,sl,tp)
            else:
                print("ask/bid err ",ask," ",bid)
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("cost",cost)
    print("Open終わりました！,GTHF")

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
        while (math.isnan(bid) or bid < 0) and retryCount < 1:
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
            limitPrice = normalizeFloat(bid * (2-1.003032140691),ask,bid)
            order = StopLimitOrder(
                action=action, totalQuantity=totalQuantity, 
                lmtPrice=limitPrice, stopPrice = bid,
                outsideRth=False,
                tif="DAY")
            trade = ib.placeOrder(contract, order)
            print(f'Flatten Position: {action} {totalQuantity} {contract.localSymbol}')
            assert trade in ib.trades(), 'trade not listed in ib.trades'

def main():
    update_balance()
    get_all_symbol_list()

    afterOppen = False
    if afterOppen:
        get_scanner()
        print(scanner)
        check_for_pre_open()
        print(stock_list)
        check_for_open()

    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        min = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second

        if(hour == 13 and min == 29 and sec == 0):
            update_balance()
            get_scanner()
            remove_duplicate()
            print(scanner)

        if(hour == 13 and min == 30 and sec == 0):
            check_for_pre_open()
            print(stock_list)
            check_for_open()

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