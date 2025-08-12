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

risk = 0.06

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
        outsideRth=True,
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
    high_bracket = bracketStopLimitOrderTwoTargets(
        contract,
        action='BUY', quantity=vol, stopPrice=op,
        limitPrice=op,
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

duplicate_list = ['SQQQ', 'PLTR', 'SPCE', 'CSCO', 'SHIP']
all_symbol_list = []
gain_sym_list = []
vol_sym_list = []
active_sym_list = []
hisBarsQQQD1 = []
scanner = []
gap_list = []

inside_day = False

# ---List section---
stock_list = [] # List for open
# Tp List
stock_list_bias = []
stock_list_M30_turn_arround = []
stock_list_bp3_d1 = []
stock_list_marcap = []

bias_over8_list = []
bias_over10_list = []

fillterPassedList = [] # List for M30 open check
talib_passed_list = []
talib_passed_list_d1_w1 = []
# ---end list section---
contractQQQ = Stock('QQQ', 'SMART', 'USD')

def get_all():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        symbol = position.contract.symbol
        duplicate_list.append(symbol)

def remove_duplicate():
    global scanner
    # get_all()
    scanner = [stock for stock in scanner if stock not in duplicate_list]

def check_inside_day():
    global inside_day
    hisBarsQQQD1 = ib.reqHistoricalData(
        contractQQQ, endDateTime='', durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    hisBarsQQQD1 = hisBarsQQQD1[::-1]

    if(
        hisBarsQQQD1[1].close < hisBarsQQQD1[1].open
        and hisBarsQQQD1[0].open > hisBarsQQQD1[1].low
        and hisBarsQQQD1[0].open < hisBarsQQQD1[1].high
    ):  inside_day = True

def get_all_symbol_list():
    global all_symbol_list
    symbol_df = pd.read_csv (r'./backtest/csv/symbolLst.csv', index_col=0)
    symbol_df.drop
    sym_list = json.loads(symbol_df.to_json(orient = 'records'))
    for sym in sym_list:
        all_symbol_list.append(sym['symbol'])
# Scanner
def get_scanner():
    global scanner, gain_sym_list, vol_sym_list, active_sym_list
    gain_sym_list = []
    vol_sym_list = []
    active_sym_list = []
    hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice=cash*risk,
                                        abovePrice='0.97',
                                        aboveVolume='316859' #6664151  # <1407
                                        )
    hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                            locationCode='STK.US.MAJOR',
                                            scanCode='HOT_BY_VOLUME', #'HOT_BY_VOLUME',
                                            belowPrice=cash*risk,
                                            abovePrice='0.97',
                                            aboveVolume='316859' #6664151  # <1407
                                            )
    hot_stk_by_active = ScannerSubscription(instrument='STK',
                                            locationCode='STK.US.MAJOR',
                                            scanCode='MOST_ACTIVE', #'HOT_BY_VOLUME',
                                            belowPrice=cash*risk,
                                            abovePrice='0.97',
                                            aboveVolume='316859' #6664151  # <1407
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
    scanner = gain_sym_list
    for sym in vol_sym_list:
        if sym not in scanner:
            scanner.append(sym)
    remove_duplicate()
    print('gain',gain_sym_list)
    print('vol',vol_sym_list)
    print('active',active_sym_list)
    print('scanner',scanner)

def get_qqq_d1():
    global hisBarsQQQD1
    hisBarsQQQD1 = ib.reqHistoricalData(
        contractQQQ, endDateTime='', durationStr='365 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    hisBarsQQQD1 = hisBarsQQQD1[::-1]

def check_op_limit(op):
    if(
        (op<0.97)
        or (op>10 and op<10.96)
        or op > cash*risk/3
    ): return False
    return True

def check_for_pre_open():
    hisBarsQQQD1closeArr = []
    for d in hisBarsQQQD1:
        hisBarsQQQD1closeArr.append(d.close)
    sma25QQQD1 = sma(hisBarsQQQD1closeArr[1:26], 25)
    if(
        hisBarsQQQD1[0].open < hisBarsQQQD1[1].high
        and hisBarsQQQD1[0].open > hisBarsQQQD1[1].low
        and hisBarsQQQD1[1].close > hisBarsQQQD1[2].high
        and hisBarsQQQD1[0].open > sma25QQQD1 * 1.0367
    ):  
        print("QQQ Retrace")
        return

    for symbol in scanner:
        try:
            today = ib.reqCurrentTime().today()
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
                    if date >= today and today <= date_end:
                        if direction == 'Sell':
                            continue
                    else:   break
            
            try:
                dataReader = web.get_quote_yahoo(symbol)
                marketCap = 0
                if('marketCap' in dataReader):
                    marketCap = dataReader['marketCap'][0]
                if(marketCap < 178499997): continue
                volDf = web.DataReader(symbol, "yahoo", start, end)
                volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
                # if(volavg < 13430000): continue
                # if(volavg < 13705728): continue
                # if(volavg < 8896116): continue
                if(volavg < 1573286):   continue
            except:
                pass

            contract = Stock(symbol, 'SMART', 'USD')

            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """

            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            if(len(hisBarsD1) < 330): continue
            df_d1 = pd.DataFrame(hisBarsD1)
            hisBarsD1 = hisBarsD1[::-1]
            
            # Gap
            if(
                hisBarsD1[0].open < hisBarsD1[1].close * 1.01
            ):  continue

            # Momentum
            if not (
                hisBarsD1[1].close < hisBarsD1[1].open
                and hisBarsD1[0].open / hisBarsD1[1].close > 1.09
            ):
                if(
                    hisBarsD1[1].close < hisBarsD1[120].close
                ):  continue

            op = hisBarsD1[0].open
            if not check_op_limit(op): continue

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
            ):  continue

            # 5b dwn
            if(
                hisBarsD1[5].close < hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
                and hisBarsD1[1].high > hisBarsD1[2].high
            ):  continue

            # Sell Setup
            if(
                hisBarsD1[4].close > hisBarsD1[4].open
                and hisBarsD1[3].close > hisBarsD1[3].open
                and hisBarsD1[2].close > hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
            ):  continue

            if(
                hisBarsD1[4].close > hisBarsD1[4].open
                and hisBarsD1[2].close > hisBarsD1[3].open
                and hisBarsD1[1].close < hisBarsD1[1].open
            ):  continue

            # Turn Arround
            if(
                hisBarsD1[4].close > hisBarsD1[4].open
                and hisBarsD1[3].close > hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
            ):  continue

            if(
                hisBarsD1[8].close > hisBarsD1[8].open
                and hisBarsD1[7].close > hisBarsD1[7].open
                and hisBarsD1[6].close > hisBarsD1[6].open
                and hisBarsD1[5].close > hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close < hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
            ):  continue

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
            ):  continue

            # Pivot point reversal
            if(
                hisBarsD1[2].high > hisBarsD1[3].high
                and hisBarsD1[1].high < hisBarsD1[2].high
                and hisBarsD1[1].low < hisBarsD1[2].low
            ):  continue

            # One black crow
            if(
                hisBarsD1[2].close > hisBarsD1[2].open
                and hisBarsD1[1].close < hisBarsD1[1].open
                and hisBarsD1[1].open < hisBarsD1[2].close
                and hisBarsD1[1].low < hisBarsD1[2].low
            ):  continue

            # 2 try failure
            if(
                hisBarsD1[5].close > hisBarsD1[5].open
                and hisBarsD1[4].close < hisBarsD1[4].open
                and hisBarsD1[3].close > hisBarsD1[3].open
                and hisBarsD1[2].close < hisBarsD1[2].open
                and hisBarsD1[1].close > hisBarsD1[1].open
            ):  continue

            # Distribution
            if(
                hisBarsD1[1].close > hisBarsD1[1].open
                and Check20BarRetracement(hisBarsD1)
            ):  continue

            hisBarsD1closeArr = []
            for d in hisBarsD1:
                hisBarsD1closeArr.append(d.close)

            sma20D1 = sma(hisBarsD1closeArr[1:21], 20)

            if (
                hisBarsD1[1].close / hisBarsD1[2].close >= 1.05
                and hisBarsD1[0].open / hisBarsD1[1].close >= 1.027
                and hisBarsD1[0].open > sma20D1 * 1.07
            ):  continue

            sma200D1 = sma(hisBarsD1closeArr[1:201], 200)

            # Gap close to 200ma
            if (
                hisBarsD1[0].open < sma200D1
                and hisBarsD1[0].open > sma200D1 * 0.95
            ):  continue

            if(
                hisBarsD1[2].close > sma200D1
                and hisBarsD1[1].close < sma200D1
            ):  continue

            if not (
                (
                    hisBarsD1[3].high > hisBarsD1[4].high
                    and hisBarsD1[2].high > hisBarsD1[3].high
                    and hisBarsD1[1].high > hisBarsD1[2].high
                    and hisBarsD1[3].low > hisBarsD1[4].low
                    and hisBarsD1[2].low > hisBarsD1[3].low
                    and hisBarsD1[1].low > hisBarsD1[2].low
                )
                or
                (
                    hisBarsD1[0].open > hisBarsD1[1].close * 1.41
                )
                or
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

            sma25D1 = sma(hisBarsD1closeArr[1:26], 25)
            
            bias = (hisBarsD1[1].close-sma25D1)/sma25D1
            bias2 = (hisBarsD1[2].close-sma25D1)/sma25D1

            if not (
                (
                    hisBarsD1[0].open > hisBarsD1[1].close * 1.41
                )
                or
                buy_setup
            ):
                if (
                    bias > 0.15
                    and bias2 > 0.15
                ):  
                    if (
                        hisBarsD1[0].open / hisBarsD1[1].close>1.06
                    ):
                        bias_over8_list.append(symbol)
                    else:
                        bias_over10_list.append(symbol)


            if symbol not in stock_list:
                stock_list.append(symbol)
                stock_list_marcap.append(
                    {
                        "symbol": symbol,
                        "marketCap": marketCap
                    }
                )

        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("スキャンは終わりました！,GTHF")

def check_for_open():
    today = ib.reqCurrentTime().today()
    for stock in stock_list:
        try:
            symbol = stock
            contract = Stock(symbol, 'SMART', 'USD')

            hisBarsD1 = ib.reqHistoricalData(
                        contract, endDateTime='', durationStr='360 D',
                        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            hisBarsD1=hisBarsD1[::-1]

            ask = hisBarsD1[0].close
            bid = hisBarsD1[0].close

            spread = 0

            ticker=ib.reqMktData(contract, '', False, False)
            ib.sleep(2)
            ask = ticker.ask
            bid = ticker.bid
            spread = ask-bid

            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            low1 = hisBarsD1[1].low
            if(ask>0 and bid>0):
                op = normalizeFloat(getOP(contract, bid), ask, bid)
                if not check_op_limit(op): continue
                sl = op-(op-low1) * 0.75675675675
                slMin = sl
                if(op > 100):
                    slMin = op - 1.167
                elif(op >= 50 and op < 100):
                    slMin = op - 0.577
                elif(op >= 10 and op<50):
                    slMin = op - 0.347
                elif(op < 10):
                    slMin = op - 0.145
                sl = max(slMin, sl)
                sl = normalizeFloat(sl, ask, bid)
                if(op != sl):
                    tpVal = 25.8
                    if inside_day:  tpVal = 31.9
                    if symbol in bias_over8_list:    tpVal = 3.5
                    if symbol in bias_over10_list:    tpVal = 10.4
                    tp = op + (op-sl) * tpVal #2.8 #4.496913030998851894374282433984 #2.79
                    tp = normalizeFloat(tp, ask, bid)
                    volMax = int(cash*risk/op)
                    vol = int(cash*risk/(op-sl))
                    if(vol>volMax): vol=volMax
                    if(vol>=3):
                        spread = 0
                        spread = ask-bid
                        if (spread < (op - sl) * 0.27):
                            log("BuyStop " + symbol
                                    + " vol " + str(vol)
                                    + " op " + str(op)
                                    + " sl " + str(sl)
                                    + " tp " + str(tp))
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
    print("Open終わりました！,GTHF")

keepOpenList = ['FLY']
def close_all():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        contract = position.contract
        if(contract.symbol in keepOpenList): continue
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

def main():
    update_balance()
    get_all_symbol_list()

    afterOppen = False
    if afterOppen:
        get_qqq_d1()
        check_inside_day()
        get_scanner()
        print(scanner)
        check_for_pre_open()
        print(stock_list)
        check_for_open()

    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        min = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second

        if(hour == 12 and min == 30 and sec == 0):
            get_qqq_d1()
            print(scanner)

        if(hour == 12 and min == 55 and sec == 0):
            get_scanner()
            remove_duplicate()
            print(scanner)

        # Check Inside Day
        if(hour == 13 and min == 30 and sec==0):
            check_inside_day()

        if(hour == 13 and min == 59 and sec == 0):
            get_scanner()
            remove_duplicate()
            print(scanner)

        if(hour == 14 and min == 00 and sec == 0):
            update_balance()
            check_for_pre_open()
            print(stock_list)

        if(hour == 14 and min == 15 and sec == 0):
            check_for_open()
        # EOD
        # if(hour == 20 and min == 50 and sec == 0):
        #     close_all()

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