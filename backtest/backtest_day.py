from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from datetime import datetime as dt, timedelta
import asyncio
import nest_asyncio
import pandas_datareader.data as web

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=3)

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

cashDf = pd.DataFrame(ib.accountValues())
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)

day = ib.reqCurrentTime().day
# 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
risk = 0.06#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

# Scanner
# hot_stk_by_gain = ScannerSubscription(instrument='STK',
#                                         locationCode='STK.US.MAJOR',
#                                         scanCode='TOP_PERC_GAIN',
#                                         belowPrice=cash*risk,
#                                         abovePrice='6.31',
#                                         aboveVolume='6664151'  # <1407
#                                         )

# hot_stk_by_volume = ScannerSubscription(instrument='STK',
#                                         locationCode='STK.US.MAJOR',
#                                         scanCode='HOT_BY_VOLUME',
#                                         belowPrice=cash*risk,
#                                         abovePrice='6.31',
#                                         aboveVolume='6664151'  # <1407
#                                         )

# gainList = ib.reqScannerData(hot_stk_by_gain, [])

# volList = ib.reqScannerData(hot_stk_by_volume, [])

# gainSymList = []
# volSymList = []

# for stock in gainList:
#     symbol = stock.contractDetails.contract.symbol
#     gainSymList.append(symbol)

# for stock in volList:
#     symbol = stock.contractDetails.contract.symbol
#     volSymList.append(symbol)

# scanner = list(set(gainSymList).intersection(volSymList))

stockList = []
stockListTrend = []
stockListDay = []

trades = []

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    #print("price ",price)
    #print("getOP "+ str(round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)))
    opPrice = round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)
    # print("getOP ",str(opPrice))
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
        #print(order_res)

    print("Submitted "
            + contract.symbol
            + " BuyStop"
            + " vol " + str(vol)
            + " op " + str(op)
            + " sl " + str(sl)
            + " tp " + str(tp))

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
    
        if(slopeUpper > 0 or slopeLower > 0): return 1
        if(slopeUpper < 0 or slopeLower < 0): return -1
        return 0
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
        return 0

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

def CheckForBacktestOpen(symbol, close1, low1, time :str, bias):
    try:
        contract = Stock(symbol, 'SMART', 'USD')

        ask = close1
        bid = close1

        spread = 0

        spread = ask-bid

        #print("ticker " +str(ticker) )
        print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

        if(ask>0 and bid>0):
            op = normalizeFloat(getOP(contract, ask), ask, bid)
            sl = op-(op-low1) * 0.19080168327400598318141065947957 #0.30753353973168214654282765737875
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
                tpVal = 21.86#7.2#2.18181818182
                # if(symbol in stockListTrend):
                #     tpVal = 2.36
                # if(symbol in stockListDay):
                #     tpVal = 5.14
                tp = op + (op-sl) * tpVal #2.8 #4.496913030998851894374282433984 #2.79
                tp = normalizeFloat(tp, ask, bid)
                volMax = int(cash*risk/op)
                vol = int(cash*risk/(op-sl))
                if(vol>volMax): vol=volMax
                if(vol>=1):
                    spread = 0
                    spread = ask-bid
                    if (spread < (op - sl) * 0.28
                        and (op-sl)/sl < 0.023880598):
                        trades.append(
                            {
                                'symbol': symbol,
                                'time': time,
                                'vol': vol,
                                'op': op,
                                'sl': sl,
                                'tp': tp,
                                'bias': bias,
                            }
                        )
                        #if(symbol != "WNW" and symbol != "AMR" and symbol != "HALL"):
                        diff = 0.00063717746183
                        if(abs((op-sl)/sl)<diff or abs(op-sl)<=0.01):
                            print("sl too close")
                        # else:
                        #    handleBuyStop(contract,vol,op,sl,tp)
        else:
            print("ask/bid err ",ask," ",bid)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
    print("Open終わりました！,GTHF")

nest_asyncio.apply()
loop = asyncio.get_event_loop()

def BuyAtMarkteOpen(symbol,backtestDate,low,isPreMarket):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        timedur = timedelta(minutes=29)
        if(isPreMarket): timedur = timedelta(minutes=89)
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedur, durationStr='1 D',
            barSizeSetting='1 min', whatToShow='BID', useRTH=True)
        hisBarsM1 = hisBarsM1[::-1]
        print(hisBarsM1[0].date)
        op = hisBarsM1[0].open
        if(op>=6.31):
            print("OP ",symbol,hisBarsM1[0].date," ",op)
            CheckForBacktestOpen(symbol,hisBarsM1[0].open,low,hisBarsM1[0].date, 0)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckBias(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=False)
        if(len(hisBars) < 26): return 0
        res = 0
        df = pd.DataFrame(hisBars)
        sma25 = 0
        sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        bias = (hisBars[1].open-sma25)/sma25
        bias2 = (hisBars[2].close-sma25)/sma25
        biasval = 0.0482831585
        if(bias < -biasval
            and bias2 < -biasval): 
            res = 1
            print(symbol,'Bias')
        print(backtestDate,symbol,'CheckBias')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low, False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckSeasonTrend(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0

        hisBarsM = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='12 M',
            barSizeSetting='1M', whatToShow='ASK', useRTH=True)

        hisBarsM = hisBarsM[::-1]

        if(len(hisBarsM) > 12):
            if(
                hisBarsM[12].close > hisBarsM[12].open
            ):
                res = 1
                print(symbol,'SeasonTrend')
        print(backtestDate,symbol,'CheckSeasonTrend')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low, True)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM30(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        df = pd.DataFrame(hisBars)
        sma25 = 0
        sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        bias = (hisBars[1].close-sma25)/sma25

        hisBarsM30 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=30), durationStr='2 D',
            barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

        hisBarsM30SPY = ib.reqHistoricalData(
            contractSPY, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=30), durationStr='2 D',
            barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

        hisBarsM30QQQ = ib.reqHistoricalData(
            contractQQQ, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=30), durationStr='2 D',
            barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

        hisBarsM30 = hisBarsM30[::-1]
        hisBarsM30SPY = hisBarsM30SPY[::-1]
        hisBarsM30QQQ = hisBarsM30QQQ[::-1]

        print(hisBarsM30[0].date,hisBarsM30[1].date)

        biasSPY = (hisBarsM30SPY[1].close 
                    - hisBarsM30SPY[1].open) / hisBarsM30SPY[1].open

        biasQQQ = (hisBarsM30QQQ[1].close 
                    - hisBarsM30QQQ[1].open) / hisBarsM30QQQ[1].open

        biasM30 = (hisBarsM30[1].close 
                    - hisBarsM30[1].open) / hisBarsM30[1].open

        if(biasM30 > biasSPY
            and biasM30 > biasQQQ):
            res = 1
            print(symbol,'RelativeStrengthM30')
        print(backtestDate,symbol,'CheckRelativeStrengthM30')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low, False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM20(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        # bias = (hisBars[1].close-sma25)/sma25

        hisBarsM20 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=40), durationStr='2 D',
            barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

        hisBarsSPYM20 = ib.reqHistoricalData(
            contractSPY, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=40), durationStr='2 D',
            barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

        hisBarsQQQM20 = ib.reqHistoricalData(
            contractQQQ, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=40), durationStr='2 D',
            barSizeSetting='20 mins', whatToShow='ASK', useRTH=True)

        hisBarsM20 = hisBarsM20[::-1]
        hisBarsSPYM20 = hisBarsSPYM20[::-1]
        hisBarsQQQM20 = hisBarsQQQM20[::-1]

        print(hisBarsM20[0].date,hisBarsM20[1].date)

        biasM20 = (hisBarsM20[1].close 
                    - hisBarsM20[1].open) / hisBarsM20[1].open

        biasSPYM20 = (hisBarsSPYM20[1].close 
                    - hisBarsSPYM20[1].open) / hisBarsSPYM20[1].open

        biasQQQM20 = (hisBarsQQQM20[1].close 
                    - hisBarsQQQM20[1].open) / hisBarsQQQM20[1].open

        if(biasM20 > biasSPYM20
            and biasM20 > biasQQQM20):
            res = 1
            print(symbol,'RelativeStrengthM20')
        print(backtestDate,symbol,'CheckRelativeStrengthM20')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low, False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM15(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        # bias = (hisBars[1].close-sma25)/sma25

        hisBarsM15 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=30), durationStr='2 D',
            barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)

        hisBarsSPYM15 = ib.reqHistoricalData(
            contractSPY, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=30), durationStr='2 D',
            barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)
        
        hisBarsQQQM15 = ib.reqHistoricalData(
            contractQQQ, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=30), durationStr='2 D',
            barSizeSetting='15 mins', whatToShow='ASK', useRTH=True)

        hisBarsM15 = hisBarsM15[::-1]
        hisBarsSPYM15 = hisBarsSPYM15[::-1]
        hisBarsQQQM15 = hisBarsQQQM15[::-1]

        print(hisBarsM15[0].date,hisBarsM15[1].date)

        biasM15 = (hisBarsM15[1].close 
                    - hisBarsM15[1].open) / hisBarsM15[1].open

        biasSPYM15 = (hisBarsSPYM15[1].close 
                    - hisBarsSPYM15[1].open) / hisBarsSPYM15[1].open

        biasQQQM15 = (hisBarsQQQM15[1].close 
                    - hisBarsQQQM15[1].open) / hisBarsQQQM15[1].open

        if(biasM15 > biasSPYM15
            and biasM15 > biasQQQM15):
            res = 1
            print(symbol,'RelativeStrengthM15')
        print(backtestDate,symbol,'CheckRelativeStrengthM15')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM10(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        # bias = (hisBars[1].close-sma25)/sma25

        hisBarsM10 = ib.reqHistoricalData(
            contract,  endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=40), durationStr='2 D',
            barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)

        hisBarsSPYM10 = ib.reqHistoricalData(
            contractSPY,  endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=40), durationStr='2 D',
            barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)
        
        hisBarsQQQM10 = ib.reqHistoricalData(
            contractQQQ,  endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=40), durationStr='2 D',
            barSizeSetting='10 mins', whatToShow='ASK', useRTH=True)

        hisBarsM10=hisBarsM10[::-1]
        hisBarsSPYM10 = hisBarsSPYM10[::-1]
        hisBarsQQQM10 = hisBarsQQQM10[::-1]

        print(hisBarsM10[0].date,hisBarsM10[1].date)

        biasM10 = (hisBarsM10[1].close 
                    - hisBarsM10[1].open) / hisBarsM10[1].open

        biasSPYM10 = (hisBarsSPYM10[1].close 
                    - hisBarsSPYM10[1].open) / hisBarsSPYM10[1].open

        biasQQQM10 = (hisBarsQQQM10[1].close 
                    - hisBarsQQQM10[1].open) / hisBarsQQQM10[1].open

        if(biasM10 > biasSPYM10
            and biasM10 > biasQQQM10):
            res = 1
            print(symbol,'RelativeStrengthM10')
        print(backtestDate,symbol,'CheckRelativeStrengthM10')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM5(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        # bias = (hisBars[1].close-sma25)/sma25

        hisBarsM5 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=5*5), durationStr='2 D',
            barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

        hisBarsSPYM5 = ib.reqHistoricalData(
            contractSPY, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=5*5), durationStr='2 D',
            barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

        hisBarsQQQM5 = ib.reqHistoricalData(
            contractQQQ, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=5*5), durationStr='2 D',
            barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

        hisBarsM5 = hisBarsM5[::-1]
        hisBarsSPYM5 = hisBarsSPYM5[::-1]
        hisBarsQQQM5 = hisBarsQQQM5[::-1]

        print(hisBarsM5[0].date,hisBarsM5[1].date)

        biasM5 = (hisBarsM5[1].close 
                    - hisBarsM5[1].open) / hisBarsM5[1].open

        biasSPYM5 = (hisBarsSPYM5[1].close 
                    - hisBarsSPYM5[1].open) / hisBarsSPYM5[1].open

        biasQQQM5 = (hisBarsQQQM5[1].close 
                    - hisBarsQQQM5[1].open) / hisBarsQQQM5[1].open

        if(biasM5 > biasSPYM5
            and biasM5 > biasQQQM5):
            res = 1
            print(symbol,'RelativeStrengthM5')
        print(backtestDate,symbol,'CheckRelativeStrengthM5')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM3(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        # bias = (hisBars[1].close-sma25)/sma25

        hisBarsM3 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=5*5), durationStr='2 D',
            barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)

        hisBarsSPYM3 = ib.reqHistoricalData(
            contractSPY, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=5*5), durationStr='2 D',
            barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)

        hisBarsQQQM3 = ib.reqHistoricalData(
            contractQQQ, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=5*5), durationStr='2 D',
            barSizeSetting='3 mins', whatToShow='ASK', useRTH=True)

        hisBarsM3 = hisBarsM3[::-1]
        hisBarsSPYM3 = hisBarsSPYM3[::-1]
        hisBarsQQQM3 = hisBarsQQQM3[::-1]

        print(hisBarsM3[0].date,hisBarsM3[1].date)

        biasM3 = (hisBarsM3[1].close 
                    - hisBarsM3[1].open) / hisBarsM3[1].open

        biasSPYM3 = (hisBarsSPYM3[1].close 
                    - hisBarsSPYM3[1].open) / hisBarsSPYM3[1].open

        biasQQQM3 = (hisBarsQQQM3[1].close 
                    - hisBarsQQQM3[1].open) / hisBarsQQQM3[1].open

        if(biasM3 > biasSPYM3
            and biasM3 > biasQQQM3):
            res = 1
            print(symbol,'RelativeStrengthM3')
        print(backtestDate,symbol,'CheckRelativeStrengthM3')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckRelativeStrengthM2(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        # bias = (hisBars[1].close-sma25)/sma25

        hisBarsM2 = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=42), durationStr='2 D',
            barSizeSetting='2 mins', whatToShow='ASK', useRTH=True)

        hisBarsSPYM2 = ib.reqHistoricalData(
            contractSPY, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=42), durationStr='2 D',
            barSizeSetting='2 mins', whatToShow='ASK', useRTH=True)

        hisBarsQQQM2 = ib.reqHistoricalData(
            contractQQQ, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1)-timedelta(minutes=42), durationStr='2 D',
            barSizeSetting='2 mins', whatToShow='ASK', useRTH=True)

        hisBarsM2 = hisBarsM2[::-1]
        hisBarsSPYM2 = hisBarsSPYM2[::-1]
        hisBarsQQQM2 = hisBarsQQQM2[::-1]

        print(hisBarsM2[0].date,hisBarsM2[1].date)

        biasM2 = (hisBarsM2[1].close 
                    - hisBarsM2[1].open) / hisBarsM2[1].open

        biasSPYM2 = (hisBarsSPYM2[1].close 
                    - hisBarsSPYM2[1].open) / hisBarsSPYM2[1].open

        biasQQQM2 = (hisBarsQQQM2[1].close 
                    - hisBarsQQQM2[1].open) / hisBarsQQQM2[1].open

        if(biasM2 > biasSPYM2
            and biasM2 > biasQQQM2):
            res = 1
            print(symbol,'RelativeStrengthM2')
        print(backtestDate,symbol,'CheckRelativeStrengthM2')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckBuySetup(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]

        k = 1
        while(k<=1):
            if(hisBars[k*2+1].close<hisBars[k*3].open
                and hisBars[k+1].close<hisBars[k*2].open
                and hisBars[1].close>hisBars[1].open):
                res += 1
                print(symbol,'BuySetup')
            k += 1
        print(backtestDate,symbol,'CheckBuySetup')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def Check4bBuySetup(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]

        k = 1
        while(k<=1):
            if(hisBars[k*3+1].close<hisBars[k*4].open
                and hisBars[k*2+1].close<hisBars[k*3].open
                and hisBars[k+1].close<hisBars[k*2].open
                and hisBars[1].close>hisBars[1].open):
                res += 1
                print(symbol,'4bBuySetup')
            k += 1
        print(backtestDate,symbol,'Check4bBuySetup')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckAll(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        df = pd.DataFrame(hisBars)
        sma25 = 0
        sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]
        bias = (hisBars[1].open-sma25)/sma25
        bias2 = (hisBars[2].close-sma25)/sma25
        biasval = 0.0482831585

        if(bias < -biasval
            and bias2 < -biasval):
            res += 1
            print(symbol,'Bias')
        k = 1

        
        if(hisBars[k*2+1].close<hisBars[k*3].open
            and hisBars[k+1].close<hisBars[k*2].open
            and hisBars[1].close>hisBars[1].open):
            res += 1
            print(symbol,'BuySetup')
        print(backtestDate,symbol,'CheckAll')
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

async def CheckBuySetupH8(symbol, backtestDate):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        contractSPY = Stock('SPY', 'SMART', 'USD')
        contractQQQ = Stock('QQQ', 'SMART', 'USD')
        hisBars = ib.reqHistoricalData(
            contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='365 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if(len(hisBars) < 26): return 0
        res = 0
        # df = pd.DataFrame(hisBars)
        # sma25 = 0
        # sma25 = df.close.rolling(window=25).mean().iloc[-1]
        hisBars = hisBars[::-1]

        # hisBarsH8 = ib.reqHistoricalData(
        #             contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='360 D',
        #             barSizeSetting='8 hours', whatToShow='ASK', useRTH=True)

        # hisBarsH8 = hisBarsH8[::-1]

        # hisBarsH3 = ib.reqHistoricalData(
        #             contract, endDateTime=dt.strptime(backtestDate, '%Y-%m-%d')+timedelta(days=1), durationStr='360 D',
        #             barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)

        hisBarsH3 = hisBarsH3[::-1]

        if(len(hisBars)<5): return
        k = 1
        while(k<=3):
            if(hisBars[k*2+1].close<hisBars[k*3].open
                and hisBars[k+1].close<hisBars[k*2].open
                and hisBars[1].close>hisBars[1].open):
                res +=1
                print(symbol,'BuySetup')
            k += 1
        if(res>0):
            BuyAtMarkteOpen(symbol,backtestDate,hisBars[1].low,False)
        print(backtestDate,symbol,'CheckBuySetup')
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

N = 25
async def AsyncCheckOpen():
    scannerDf = pd.read_csv (r'./scanner.csv')

    contractSPY = Stock('SPY', 'SMART', 'USD')
    contractQQQ = Stock('QQQ', 'SMART', 'USD')

    tasks = asyncio.Queue()

    try:
        for index, row in scannerDf.iterrows():
            scanner = scannerDf['stocks'][index].split(",")
            backtestDate = scannerDf['date'][index]
            print('date',backtestDate)
            print('scanner',scanner)
            
            for symbol in scanner:
                #tasks.put_nowait(CheckBias(symbol,backtestDate))
                #tasks.put_nowait(CheckBuySetup(symbol,backtestDate))
                tasks.put_nowait(Check4bBuySetup(symbol,backtestDate))
                # tasks.put_nowait(CheckAll(symbol,backtestDate))
                #tasks.put_nowait(CheckSeasonTrend(symbol,backtestDate))

        async def worker():
            while not tasks.empty():
                await tasks.get_nowait()
        await asyncio.gather(*[worker() for _ in range(N)])
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

asyncio.run(AsyncCheckOpen())

df = pd.DataFrame(trades)
df.to_csv('./trades.csv')
