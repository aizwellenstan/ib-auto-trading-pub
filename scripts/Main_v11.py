from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from datetime import datetime as dt, timedelta
import pandas_datareader.data as web

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=2)

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)

day = ib.reqCurrentTime().day
# 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
risk = 0.06#0.04#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

# Scanner
hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice=cash*risk,
                                        abovePrice='6.31',
                                        aboveVolume='316859' #6664151  # <1407
                                        )

hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='MOST_ACTIVE_USD', #'HOT_BY_VOLUME',
                                        belowPrice=cash*risk,
                                        abovePrice='6.31',
                                        aboveVolume='316859' #6664151  # <1407
                                        )

gainList = ib.reqScannerData(hot_stk_by_gain, [])

volList = ib.reqScannerData(hot_stk_by_volume, [])

gainSymList = []
volSymList = []

for stock in gainList:
    symbol = stock.contractDetails.contract.symbol
    gainSymList.append(symbol)

for stock in volList:
    symbol = stock.contractDetails.contract.symbol
    volSymList.append(symbol)

duplicateList = ['SQQQ']

def GetAll():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        symbol = position.contract.symbol
        duplicateList.append(symbol)

GetAll()

scanner = list(set(gainSymList).intersection(volSymList))
scanner = gainSymList
scanner = [stock for stock in scanner if stock not in duplicateList]
stockList = []
stockListTrend = []
stockListDay = []

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    #print("price ",price)
    #print("getOP "+ str(round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)))
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

def CheckForPreOpen():
    end = dt.now()
    start = end - timedelta(days=50)
    
    for symbol in scanner:
        try:
            dataReader = web.get_quote_yahoo(symbol)
            marketCap = 0
            if('marketCap' in dataReader):
                marketCap = dataReader['marketCap'][0]
            if(marketCap < 178499997): continue
            volDf = web.DataReader(symbol, "yahoo", start, end)
            volavg = volDf.Volume.rolling(window=30).mean().iloc[-1]
            if(volavg < 1638137): continue
            contract = Stock(symbol, 'SMART', 'USD')
            contractSPY = Stock('SPY', 'SMART', 'USD')
            contractQQQ = Stock('QQQ', 'SMART', 'USD')

            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """
            hisBarsH4 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='4 D',
                barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)

            if(len(hisBarsH4) < 5): continue

            hisBarsSPYH4 = ib.reqHistoricalData(
                contractSPY, endDateTime='', durationStr='2 D',
                barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)
            
            hisBarsQQQH4 = ib.reqHistoricalData(
                contractQQQ, endDateTime='', durationStr='2 D',
                barSizeSetting='4 hours', whatToShow='ASK', useRTH=True)

            hisBarsH3 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='3 D',
                barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)

            hisBarsH2 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='2 D',
                barSizeSetting='2 hours', whatToShow='ASK', useRTH=True)

            # hisBarsSPYH3 = ib.reqHistoricalData(
            #     contractSPY, endDateTime='', durationStr='2 D',
            #     barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)

            # hisBarsQQQH3 = ib.reqHistoricalData(
            #     contractQQQ, endDateTime='', durationStr='2 D',
            #     barSizeSetting='3 hours', whatToShow='ASK', useRTH=True)
                
            hisBarsH1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='2 D',
                barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)

            # hisBarsSPYH1 = ib.reqHistoricalData(
            #     contractSPY, endDateTime='', durationStr='2 D',
            #     barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)

            # hisBarsQQQH1 = ib.reqHistoricalData(
            #     contractQQQ, endDateTime='', durationStr='2 D',
            #     barSizeSetting='1 hour', whatToShow='ASK', useRTH=True)

            hisBarsM30 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='2 D',
                barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

            hisBarsSPYM30 = ib.reqHistoricalData(
                contractSPY, endDateTime='', durationStr='2 D',
                barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

            hisBarsQQQM30 = ib.reqHistoricalData(
                contractQQQ, endDateTime='', durationStr='2 D',
                barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

            hisBarsH4 = hisBarsH4[::-1]
            hisBarsSPYH4 = hisBarsSPYH4[::-1]
            hisBarsQQQH4 = hisBarsQQQH4[::-1]

            # hisBarsH3 = hisBarsH3[::-1]
            # hisBarsSPYH3 = hisBarsSPYH3[::-1]
            # hisBarsQQQH3 = hisBarsQQQH3[::-1]

            hisBarsH1=hisBarsH1[::-1]
            # hisBarsSPYH1 = hisBarsSPYH1[::-1]
            # hisBarsQQQH1 = hisBarsQQQH1[::-1]

            # hisBarsM30 = hisBarsM30[::-1]
            # hisBarsSPYM30 = hisBarsSPYM30[::-1]
            # hisBarsQQQM30 = hisBarsQQQM30[::-1]

            biasH4 = (hisBarsH4[1].close 
                        - hisBarsH4[1].open) / hisBarsH4[1].open

            biasSPYH4 = (hisBarsSPYH4[1].close 
                        - hisBarsSPYH4[1].open) / hisBarsSPYH4[1].open

            biasQQQH4 = (hisBarsQQQH4[1].close 
                        - hisBarsQQQH4[1].open) / hisBarsQQQH4[1].open

            # biasH3 = (hisBarsH3[1].close 
            #             - hisBarsH3[1].open) / hisBarsH3[1].open

            # biasSPYH3 = (hisBarsSPYH3[1].close 
            #             - hisBarsSPYH3[1].open) / hisBarsSPYH3[1].open

            # biasQQQH3 = (hisBarsQQQH3[1].close 
            #             - hisBarsQQQH3[1].open) / hisBarsQQQH3[1].open

            # biasH1 = (hisBarsH1[1].close 
            #             - hisBarsH1[1].open) / hisBarsH1[1].open

            # biasSPYH1 = (hisBarsSPYH1[1].close 
            #             - hisBarsSPYH1[1].open) / hisBarsSPYH1[1].open

            # biasQQQH1 = (hisBarsQQQH1[1].close 
            #             - hisBarsQQQH1[1].open) / hisBarsQQQH1[1].open

            # biasM30 = (hisBarsM30[1].close 
            #             - hisBarsM30[1].open) / hisBarsM30[1].open

            # biasSPY = (hisBarsSPYM30[1].close 
            #             - hisBarsSPYM30[1].open) / hisBarsSPYM30[1].open

            # biasQQQ = (hisBarsQQQM30[1].close 
            #             - hisBarsQQQM30[1].open) / hisBarsQQQM30[1].open

            hisBars = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            hisBarsM = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='12 M',
                barSizeSetting='1M', whatToShow='ASK', useRTH=True)

            hisBarsW = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='52 W',
                barSizeSetting='1W', whatToShow='ASK', useRTH=True)

            df = pd.DataFrame(hisBars)
            # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            #     print(df)
            sma25 = 0
            # sma200 = 0
            sma25 = df.close.rolling(window=25).mean().iloc[-1]
            secondSma25 = df.close.rolling(window=25).mean().iloc[-2]
            # sma200 = df.close.rolling(window=200).mean().iloc[-1]

            hisBars = hisBars[::-1]
            hisBarsM = hisBarsM[::-1]
            hisBarsW = hisBarsW[::-1]

            # Main
            atrRange: float = 4
            size: int = 3
            sizeH8: int = 3
            sizeH4: int = 1
            sizeH3: int = 1
            sizeH2: int = 1
            sizeH1: int = 1
            sizeM30: int = 1
            sizeM20: int = 1
            sizeM15: int = 1
            sizeM10: int = 1
            sizeM5: int = 1
            sizeM3: int = 1
            sizeM2: int = 1
            k: int = 0 #26
            l: int = 0
            m: int = 0
            n: int = 0
            o: int = 0
            p: int = 0
            q: int = 0
            r: int = 0
            s: int = 0
            t: int = 0
            u: int = 0
            v: int = 0
            w: int = 0
            buy: int = 0
            sell: int = 0
            maxBar: int = 28 #63
            hisBarsLength: int = len(hisBars)

            if(hisBarsLength<6): continue
            if(hisBarsLength<size): size = hisBarsLength

            # if(len(hisBarsM)>12 and len(hisBarsW)>52):
            #     if(
            #         hisBarsM[12].close>hisBarsM[12].open
            #     ):
            #         buy += 1
            #         logSeasonTrend += 1

            #     if(
            #         hisBarsM[12].close<hisBarsM[12].open
            #     ):
            #         sell += 1

            #bias
            

            # if(hisBarsLength>25 and sma25>0):
            #     bias = (hisBars[1].close-sma25)/sma25
            #     if(bias < -0.1875976735): continue

            ATR = ((hisBars[1].high - hisBars[1].low) +
                    (hisBars[2].high - hisBars[2].low) +
                    (hisBars[3].high - hisBars[3].low) +
                    (hisBars[4].high - hisBars[4].low) +
                    (hisBars[5].high - hisBars[5].low)) / 5

            currentLongRange = hisBars[1].close - hisBars[0].low
            currentShortRange = hisBars[0].high - hisBars[1].close

            logBuySetup = 0
            logRelativeStrength = 0
            logSeasonTrend = 0
            logTrend = 0
            logBp3 = 0
            logBp4 = 0
            logBias = 0
            logH8Bp3 = 0
            logH8Bp4 = 0
            logH4Bp3 = 0
            logH4Bp4 = 0
            logH3Bp3 = 0
            logH3Bp4 = 0
            logH2Bp3 = 0
            logH1Bp3 = 0
            logM30Bp3 = 0
            logM20Bp3 = 0
            logM15Bp3 = 0
            logM10Bp3 = 0
            logM5Bp3 = 0
            logM3Bp3 = 0
            logM2Bp3 = 0

            if(hisBarsLength>25 and sma25>0):
                bias = (hisBars[1].close-sma25)/sma25
                bias2 = (hisBars[2].close-sma25)/sma25
                biasval = 0.0482831585

                if(bias < -biasval
                    and bias2 < -biasval): 
                    buy += 1
                    logBias += 1
                if(bias > biasval
                    and bias2 > biasval):
                    sell += 1

            x = 1
            if(hisBars[x*2+1].close<hisBars[x*3].open
                and hisBars[x+1].close<hisBars[x*2].open
                and hisBars[1].close>hisBars[1].open):
                buy+=1
                logBuySetup += 1

            # if(biasH4 > biasSPYH4
            #     and biasH4 > biasQQQH4):
            #     buy += 1
            #     logRelativeStrength += 1

            # if(biasH3 > biasSPYH3
            #     and biasH3 > biasQQQH3):
            #     buy += 1
            #     logRelativeStrength += 1

            # if(biasH1 > biasSPYH1
            #     and biasH1 > biasQQQH1):
            #     buy += 1
            #     logRelativeStrength += 1

            # if(biasM30 > biasSPY
            #     and biasM30 > biasQQQ):
            #     buy += 1
            #     logRelativeStrength += 1
            
            # if(hisBarsLength>25 and sma25>0):
            #     bias = (hisBars[0].open-sma25)/sma25
            #     if(hisBars[1].high > hisBars[4].close
            #         and hisBars[3].close > hisBars[3].open
            #         and bias < 0):
            #         plotLinesRes = plotLines(hisBars)
            #         if(plotLinesRes>0):
            #             buy+= 1
            #             logTrend += 1
            #     if(hisBars[1].low < hisBars[4].close
            #         and hisBars[3].close < hisBars[3].open
            #         and bias > 0):
            #         plotLinesRes = plotLines(hisBars)
            #         if(plotLinesRes<0):
            #             sell+=1
            while(k < size):
                k += 1
                maxUsedBar = 4
                if(k<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBars[k*2+1].close
                    signalCandleOpen3 = hisBars[k*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBars[k*4].high - hisBars[k*4].low
                    endCandleRange3 = abs(hisBars[1].close - hisBars[k].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 6.054347826086946):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBars[2].high < hisBars[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBars[1].close < hisBars[1].open):
                                if (hisBars[1].high - hisBars[1].close
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    buy += 1
                                    logBp3 += 1
                                    #print(symbol," ",ATR/currentLongRange)
                                    print(symbol," ",k,bigCandleRange3/smallCandleRange3)
                            else:
                                buy += 1
                                logBp3 += 1
                                print(symbol," ",ATR/currentLongRange)
                                print(symbol," ",k,bigCandleRange3/smallCandleRange3)

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBars[k+1].close-hisBars[k*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBars[2].low > hisBars[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBars[1].close > hisBars[1].open):
                                if (hisBars[1].close - hisBars[1].low
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

                maxUsedBar = 5
                if(k<maxBar/maxUsedBar and k<2):
                    signalCandleClose4 = hisBars[k*3+1].close
                    signalCandleOpen4 = hisBars[k*4].open
                    bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
                    smallCandleRange4 = hisBars[k*5].high - hisBars[k*5].low
                    endCandleRange4 = abs(hisBars[1].close - hisBars[k].open)

                    if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 6.054347826086946):
                        if (signalCandleClose4 > signalCandleOpen4
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange4
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentLongRange < ATR/atrRange):
                            if (hisBars[1].close < hisBars[1].open):
                                if (hisBars[1].high - hisBars[1].close
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    buy += 1
                                    logBp4 += 1
                            else:
                                buy += 1
                                logBp4 += 1

                        if (signalCandleClose4 < signalCandleOpen4
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange4
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentShortRange < ATR/atrRange):
                            if (hisBars[1].close > hisBars[1].open):
                                if (hisBars[1].close - hisBars[1].low
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsH8 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='8 hours', whatToShow='ASK', useRTH=False)

            hisBarsH8=hisBarsH8[::-1]

            while(l < sizeH8):
                l += 1
                maxUsedBar = 4
                if(l<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH8[l*2+1].close
                    signalCandleOpen3 = hisBarsH8[l*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsH8[l*4].high - hisBarsH8[l*4].low
                    endCandleRange3 = abs(hisBarsH8[1].close - hisBarsH8[l].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsH8[l+1].close - hisBarsH8[l*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH8[2].high < hisBarsH8[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH8[1].close < hisBarsH8[1].open):
                                if (hisBarsH8[1].high - hisBarsH8[1].close
                                        > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
                                    buy += 1
                                    logH8Bp3 += 1
                                    print(symbol," ",ATR/currentLongRange)
                                    print(symbol," ",l,bigCandleRange3/smallCandleRange3)
                            else:
                                buy += 1
                                logH8Bp3 += 1
                                print(symbol," ",ATR/currentLongRange)
                                print(symbol," ",l,bigCandleRange3/smallCandleRange3)

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsH8[l+1].close-hisBarsH8[l*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH8[2].low > hisBarsH8[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH8[1].close > hisBarsH8[1].open):
                                if (hisBarsH8[1].close - hisBarsH8[1].low
                                        > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1
                
                maxUsedBar = 5
                if(l<maxBar/maxUsedBar and l<2):
                    signalCandleClose4 = hisBarsH8[l*3+1].close
                    signalCandleOpen4 = hisBarsH8[l*4].open
                    bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
                    smallCandleRange4 = hisBarsH8[l*5].high - hisBarsH8[l*5].low
                    endCandleRange4 = abs(hisBarsH8[1].close - hisBarsH8[l].open)

                    if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
                        if (signalCandleClose4 > signalCandleOpen4
                            and abs(hisBarsH8[l*2+1].close - hisBarsH8[l*3].open) < bigCandleRange4
                            and abs(hisBarsH8[l+1].close - hisBarsH8[l*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH8[1].close < hisBarsH8[1].open):
                                if (hisBarsH8[1].high - hisBarsH8[1].close
                                        > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
                                    buy += 1
                                    logH8Bp4 += 1
                            else:
                                buy += 1
                                logH8Bp4 += 1

                        if (signalCandleClose4 < signalCandleOpen4
                            and abs(hisBarsH8[l*2+1].close - hisBarsH8[l*3].open) < bigCandleRange4
                            and abs(hisBarsH8[l+1].close - hisBarsH8[l*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH8[1].close > hisBarsH8[1].open):
                                if (hisBarsH8[1].close - hisBarsH8[1].low
                                        > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            while(m < sizeH4):
                m += 1
                maxUsedBar = 4
                if(m<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH4[m*2+1].close
                    signalCandleOpen3 = hisBarsH4[m*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBarsH4[m*4].high - hisBarsH4[m*4].low)
                    endCandleRange3 = abs(hisBarsH4[1].close - hisBarsH4[m].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsH4[m+1].close - hisBarsH4[m*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH4[2].high < hisBarsH4[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH4[1].close < hisBarsH4[1].open):
                                if (hisBarsH4[1].high - hisBarsH4[1].close
                                        > (hisBarsH4[1].high - hisBarsH4[1].low)*0.13):
                                    buy += 1
                                    logH4Bp3 += 1
                            else:
                                buy += 1
                                logH4Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsH4[m+1].close-hisBarsH4[m*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH4[2].low > hisBarsH4[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH4[1].close > hisBarsH4[1].open):
                                if (hisBarsH4[1].close - hisBarsH4[1].low
                                        > (hisBarsH4[1].high - hisBarsH4[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

                maxUsedBar = 5
                if(m<maxBar/maxUsedBar and m<2):
                    signalCandleClose4 = hisBarsH4[m*3+1].close
                    signalCandleOpen4 = hisBarsH4[m*4].open
                    bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
                    smallCandleRange4 = hisBarsH4[m*5].high - hisBarsH4[m*5].low
                    endCandleRange4 = abs(hisBarsH4[1].close - hisBarsH4[m].open)

                    if (smallCandleRange4 > 0 and bigCandleRange4 > smallCandleRange4 * 4):
                        if (signalCandleClose4 > signalCandleOpen4
                            and abs(hisBarsH4[m*2+1].close - hisBarsH4[m*3].open) < bigCandleRange4
                            and abs(hisBarsH4[m+1].close - hisBarsH4[m*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH4[1].close < hisBarsH4[1].open):
                                if (hisBarsH4[1].high - hisBarsH4[1].close
                                        > (hisBarsH4[1].high - hisBarsH4[1].low)*0.13):
                                    buy += 1
                                    logH4Bp4 += 1
                            else:
                                buy += 1
                                logH4Bp4 += 1

                        if (signalCandleClose4 < signalCandleOpen4
                            and abs(hisBarsH4[m*2+1].close - hisBarsH4[m*3].open) < bigCandleRange4
                            and abs(hisBarsH4[m+1].close - hisBarsH4[m*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH4[1].close > hisBarsH4[1].open):
                                if (hisBarsH4[1].close - hisBarsH4[1].low
                                        > (hisBarsH4[1].high - hisBarsH4[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            while(n < sizeH3):
                n += 1
                maxUsedBar = 4
                if(n<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH3[n*2+1].close
                    signalCandleOpen3 = hisBarsH3[n*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsH3[n*4].high - hisBarsH3[n*4].low
                    endCandleRange3 = abs(hisBarsH3[1].close - hisBarsH3[n].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsH3[n+1].close - hisBarsH3[n*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH3[2].high < hisBarsH3[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH3[1].close < hisBarsH3[1].open):
                                if (hisBarsH3[1].high - hisBarsH3[1].close
                                        > (hisBarsH3[1].high - hisBarsH3[1].low)*0.13):
                                    buy += 1
                                    logH3Bp3 += 1
                            else:
                                buy += 1
                                logH3Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsH3[n+1].close-hisBarsH3[n*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH3[2].low > hisBarsH3[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH3[1].close > hisBarsH3[1].open):
                                if (hisBarsH3[1].close - hisBarsH3[1].low
                                        > (hisBarsH3[1].high - hisBarsH3[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            while(o < sizeH2):
                o += 1
                maxUsedBar = 4
                if(o<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH2[o*2+1].close
                    signalCandleOpen3 = hisBarsH2[o*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsH2[o*4].high - hisBarsH2[o*4].low
                    endCandleRange3 = abs(hisBarsH2[1].close - hisBarsH2[o].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 4):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsH2[o+1].close - hisBarsH2[o*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH2[2].high < hisBarsH2[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH2[1].close < hisBarsH2[1].open):
                                if (hisBarsH2[1].high - hisBarsH2[1].close
                                        > (hisBarsH2[1].high - hisBarsH2[1].low)*0.13):
                                    buy += 1
                                    logH2Bp3 += 1
                            else:
                                buy += 1
                                logH2Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsH2[o+1].close-hisBarsH2[o*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH2[2].low > hisBarsH2[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH2[1].close > hisBarsH2[1].open):
                                if (hisBarsH2[1].close - hisBarsH2[1].low
                                        > (hisBarsH2[1].high - hisBarsH2[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            while(p < sizeH1):
                p += 1
                maxUsedBar = 4
                if(p<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH1[p*2+1].close
                    signalCandleOpen3 = hisBarsH1[p*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsH1[p*4].high - hisBarsH1[p*4].low
                    endCandleRange3 = abs(hisBarsH1[1].close - hisBarsH1[p].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsH1[p+1].close - hisBarsH1[p*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH1[2].high < hisBarsH1[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH1[1].close < hisBarsH1[1].open):
                                if (hisBarsH1[1].high - hisBarsH1[1].close
                                        > (hisBarsH1[1].high - hisBarsH1[1].low)*0.13):
                                    buy += 1
                                    logH1Bp3 += 1
                            else:
                                buy += 1
                                logH1Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsH1[p+1].close-hisBarsH1[p*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH1[2].low > hisBarsH1[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsH1[1].close > hisBarsH1[1].open):
                                if (hisBarsH1[1].close - hisBarsH1[1].low
                                        > (hisBarsH1[1].high - hisBarsH1[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            while(q < sizeM30):
                q += 1
                maxUsedBar = 4
                if(q<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM30[q*2+1].close
                    signalCandleOpen3 = hisBarsM30[q*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM30[q*4].high - hisBarsM30[q*4].low
                    endCandleRange3 = abs(hisBarsM30[1].close - hisBarsM30[q].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM30[q+1].close - hisBarsM30[q*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM30[2].high < hisBarsM30[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM30[1].close < hisBarsM30[1].open):
                                if (hisBarsM30[1].high - hisBarsM30[1].close
                                        > (hisBarsM30[1].high - hisBarsM30[1].low)*0.13):
                                    buy += 1
                                    logM30Bp3 += 1
                            else:
                                buy += 1
                                logM30Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM30[q+1].close-hisBarsM30[q*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM30[2].low > hisBarsM30[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM30[1].close > hisBarsM30[1].open):
                                if (hisBarsM30[1].close - hisBarsM30[1].low
                                        > (hisBarsM30[1].high - hisBarsM30[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsM20 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='5 D',
                barSizeSetting='20 mins', whatToShow='ASK', useRTH=False)

            hisBarsM20=hisBarsM20[::-1]

            while(r < sizeM20):
                r += 1
                maxUsedBar = 4
                if(r<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM20[r*2+1].close
                    signalCandleOpen3 = hisBarsM20[r*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM20[r*4].high - hisBarsM20[r*4].low
                    endCandleRange3 = abs(hisBarsM20[1].close - hisBarsM20[r].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM20[r+1].close - hisBarsM20[r*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM20[2].high < hisBarsM20[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM20[1].close < hisBarsM20[1].open):
                                if (hisBarsM20[1].high - hisBarsM20[1].close
                                        > (hisBarsM20[1].high - hisBarsM20[1].low)*0.13):
                                    buy += 1
                                    logM20Bp3 += 1
                            else:
                                buy += 1
                                logM20Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM20[r+1].close-hisBarsM20[r*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM20[2].low > hisBarsM20[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM20[1].close > hisBarsM20[1].open):
                                if (hisBarsM20[1].close - hisBarsM20[1].low
                                        > (hisBarsM20[1].high - hisBarsM20[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsM15 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='5 D',
                barSizeSetting='15 mins', whatToShow='ASK', useRTH=False)

            hisBarsM15=hisBarsM15[::-1]

            while(s < sizeM15):
                s += 1
                maxUsedBar = 4
                if(s<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM15[s*2+1].close
                    signalCandleOpen3 = hisBarsM15[s*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM15[s*4].high - hisBarsM15[s*4].low
                    endCandleRange3 = abs(hisBarsM15[1].close - hisBarsM15[s].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM15[s+1].close - hisBarsM15[s*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM15[2].high < hisBarsM15[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM15[1].close < hisBarsM15[1].open):
                                if (hisBarsM15[1].high - hisBarsM15[1].close
                                        > (hisBarsM15[1].high - hisBarsM15[1].low)*0.13):
                                    buy += 1
                                    logM15Bp3 += 1
                            else:
                                buy += 1
                                logM15Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM15[s+1].close-hisBarsM15[s*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM15[2].low > hisBarsM15[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM15[1].close > hisBarsM15[1].open):
                                if (hisBarsM15[1].close - hisBarsM15[1].low
                                        > (hisBarsM15[1].high - hisBarsM15[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsM10 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='5 D',
                barSizeSetting='10 mins', whatToShow='ASK', useRTH=False)

            hisBarsM10=hisBarsM10[::-1]

            while(t < sizeM10):
                t += 1
                maxUsedBar = 4
                if(t<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM10[t*2+1].close
                    signalCandleOpen3 = hisBarsM10[t*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM10[t*4].high - hisBarsM10[t*4].low
                    endCandleRange3 = abs(hisBarsM10[1].close - hisBarsM10[t].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM10[t+1].close - hisBarsM10[t*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM10[2].high < hisBarsM10[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM10[1].close < hisBarsM10[1].open):
                                if (hisBarsM10[1].high - hisBarsM10[1].close
                                        > (hisBarsM10[1].high - hisBarsM10[1].low)*0.13):
                                    buy += 1
                                    logM10Bp3 += 1
                            else:
                                buy += 1
                                logM10Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM10[t+1].close-hisBarsM10[t*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM10[2].low > hisBarsM10[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM10[1].close > hisBarsM10[1].open):
                                if (hisBarsM10[1].close - hisBarsM10[1].low
                                        > (hisBarsM10[1].high - hisBarsM10[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsM5 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='5 D',
                barSizeSetting='5 mins', whatToShow='ASK', useRTH=False)

            hisBarsM5=hisBarsM5[::-1]

            while(u < sizeM5):
                u += 1
                maxUsedBar = 4
                if(u<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM5[u*2+1].close
                    signalCandleOpen3 = hisBarsM5[u*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM5[u*4].high - hisBarsM5[u*4].low
                    endCandleRange3 = abs(hisBarsM5[1].close - hisBarsM5[u].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM5[u+1].close - hisBarsM5[u*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM5[2].high < hisBarsM5[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM5[1].close < hisBarsM5[1].open):
                                if (hisBarsM5[1].high - hisBarsM5[1].close
                                        > (hisBarsM5[1].high - hisBarsM5[1].low)*0.13):
                                    buy += 1
                                    logM5Bp3 += 1
                            else:
                                buy += 1
                                logM5Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM5[u+1].close-hisBarsM5[u*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM5[2].low > hisBarsM5[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM5[1].close > hisBarsM5[1].open):
                                if (hisBarsM5[1].close - hisBarsM5[1].low
                                        > (hisBarsM5[1].high - hisBarsM5[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsM3 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='2 D',
                barSizeSetting='3 mins', whatToShow='ASK', useRTH=False)

            hisBarsM3=hisBarsM3[::-1]

            while(v < sizeM3):
                v += 1
                maxUsedBar = 4
                if(v<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM3[v*2+1].close
                    signalCandleOpen3 = hisBarsM3[v*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM3[v*4].high - hisBarsM3[v*4].low
                    endCandleRange3 = abs(hisBarsM3[1].close - hisBarsM3[v].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM3[v+1].close - hisBarsM3[v*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM3[2].high < hisBarsM3[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM3[1].close < hisBarsM3[1].open):
                                if (hisBarsM3[1].high - hisBarsM3[1].close
                                        > (hisBarsM3[1].high - hisBarsM3[1].low)*0.13):
                                    buy += 1
                                    logM3Bp3 += 1
                            else:
                                buy += 1
                                logM3Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM3[v+1].close-hisBarsM3[v*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM3[2].low > hisBarsM3[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM3[1].close > hisBarsM3[1].open):
                                if (hisBarsM3[1].close - hisBarsM3[1].low
                                        > (hisBarsM3[1].high - hisBarsM3[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            hisBarsM2 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='2 D',
                barSizeSetting='2 mins', whatToShow='ASK', useRTH=False)

            hisBarsM2=hisBarsM2[::-1]

            while(w < sizeM2):
                w += 1
                maxUsedBar = 4
                if(w<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM2[w*2+1].close
                    signalCandleOpen3 = hisBarsM2[w*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = hisBarsM2[w*4].high - hisBarsM2[w*4].low
                    endCandleRange3 = abs(hisBarsM2[1].close - hisBarsM2[w].open)

                    if (smallCandleRange3 > 0 and bigCandleRange3 > smallCandleRange3 * 10.347826086956675):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsM2[w+1].close - hisBarsM2[w*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM2[2].high < hisBarsM2[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsM2[1].close < hisBarsM2[1].open):
                                if (hisBarsM2[1].high - hisBarsM2[1].close
                                        > (hisBarsM2[1].high - hisBarsM2[1].low)*0.13):
                                    buy += 1
                                    logM2Bp3 += 1
                            else:
                                buy += 1
                                logM2Bp3 += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBarsM2[w+1].close-hisBarsM2[w*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsM2[2].low > hisBarsM2[3].low
                                and currentShortRange < ATR/atrRange):
                            if (hisBarsM2[1].close > hisBarsM2[1].open):
                                if (hisBarsM2[1].close - hisBarsM2[1].low
                                        > (hisBarsM2[1].high - hisBarsM2[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

            # print(ATR)
            # print(currentLongRange)
            # print(currentShortRange)

            if((buy > 0 or sell > 0) and buy != sell):
                if(buy > sell):
                    stockList.append(symbol)
                    if(logBp3>0 or logBp4>0):
                        stockListDay.append(symbol)

                    # Log
                    if(logBuySetup>0): log(symbol + " BuySetup")
                    if(logRelativeStrength>0): log(symbol + " RelativeStrength")
                    if(logSeasonTrend>0): log(symbol + " SeasonTrend")
                    if(logBp3>0): log(symbol + " Bp3")
                    if(logBp4>0): log(symbol + " Bp4")
                    if(logBias>0): log(symbol + " Bias")
                    if(logH8Bp3>0): log(symbol + " H8Bp3")
                    if(logH8Bp4>0): log(symbol + " H8Bp4")
                    if(logH4Bp3>0): log(symbol + " H4Bp3")
                    if(logH4Bp4>0): log(symbol + " H4Bp4")
                    if(logH3Bp3>0): log(symbol + " H3Bp3")
                    if(logH3Bp4>0): log(symbol + " H3Bp4")
                    if(logH2Bp3>0): log(symbol + " H2Bp3")
                    if(logH1Bp3>0): log(symbol + " H1Bp3")
                    if(logM30Bp3>0): log(symbol + " M30Bp3")
                    if(logM20Bp3>0): log(symbol + " M20Bp3")
                    if(logM15Bp3>0): log(symbol + " M15Bp3")
                    if(logM10Bp3>0): log(symbol + " M10Bp3")
                    if(logM5Bp3>0): log(symbol + " M5Bp3")
                    if(logM3Bp3>0): log(symbol + " M3Bp3")
                    if(logM2Bp3>0): log(symbol + " M2Bp3")
                #elif(sell > buy):
                #    stockList.append(symbol)
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("スキャンは終わりました！,GTHF")

def CheckForOpen():
    for stock in stockList:
        try:
            symbol = stock
            contract = Stock(symbol, 'SMART', 'USD')
            hisBars = ib.reqHistoricalData(
                        contract, endDateTime='', durationStr='360 D',
                        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            hisBars=hisBars[::-1]

            ask = hisBars[0].close
            bid = hisBars[0].close

            spread = 0

            ticker=ib.reqMktData(contract, '', False, False)
            ib.sleep(2)
            ask = ticker.ask
            bid = ticker.bid
            spread = ask-bid

            #print("ticker " +str(ticker) )
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            low1 = hisBars[1].low
            if(ask>0 and bid>0):
                op = normalizeFloat(getOP(contract, bid), ask, bid)
                if(op < 13.60 or op > 50): #21.32 #19.08 #13.08
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
                        tpVal = 20.1 #21.86#7.2 #2.18181818182
                        # if(symbol in stockListTrend):
                        #     tpVal = 2.36
                        # if(symbol in stockListDay):
                        #     tpVal = 5.14
                        tp = op + (op-sl) * tpVal #2.8 #4.496913030998851894374282433984 #2.79
                        tp = normalizeFloat(tp, ask, bid)
                        volMax = int(cash*risk/op)
                        vol = int(cash*risk/(op-sl))
                        if(vol>volMax): vol=volMax
                        if(vol>=5):
                            spread = 0
                            spread = ask-bid
                            if (spread < (op - sl) * 0.27):
                                log("BuyStop " + symbol
                                        + " vol " + str(vol)
                                        + " op " + str(op)
                                        + " sl " + str(sl)
                                        + " tp " + str(tp))
                                #if(symbol != "WNW" and symbol != "AMR" and symbol != "HALL"):
                                diff = 0.00063717746183
                                if(abs((op-sl)/sl)<diff or abs(op-sl)<=0.01):
                                    print("sl too close")
                                else:
                                    if((op-sl)/sl < 0.023880598):
                                        handleBuyStop(contract,vol,op,sl,tp)
            else:
                print("ask/bid err ",ask," ",bid)
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("Open終わりました！,GTHF")

keepOpenList = ['FLY']

def CloseAll():
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

stockList = []
CheckForPreOpen()
print("gainSymList ",gainSymList)
print("volSymList ",volSymList)
print("scanner ",scanner)

print(stockList)
# CheckForOpen()

while(ib.sleep(1)):
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    sec = ib.reqCurrentTime().second

    # Pre Market Scanner
    # if(hour == 13 and min == 45 and sec==0):
    # if(hour == 13 and min == 15 and sec==0):
    #     cashDf = pd.DataFrame(ib.accountValues())
    #     cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
    #     cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    #     cash = float(cashDf['value'])
    #     print(cash)
    #     # Scanner
    #     hot_stk_by_gain = ScannerSubscription(instrument='STK',
    #                                             locationCode='STK.US.MAJOR',
    #                                             scanCode='TOP_PERC_GAIN',
    #                                             belowPrice=cash*risk,
    #                                             abovePrice='6.31',
    #                                             aboveVolume='316859' #6664151  # <1407
    #                                             )

    #     hot_stk_by_volume = ScannerSubscription(instrument='STK',
    #                                             locationCode='STK.US.MAJOR',
    #                                             scanCode='MOST_ACTIVE_USD', #'HOT_BY_VOLUME',
    #                                             belowPrice=cash*risk,
    #                                             abovePrice='6.31',
    #                                             aboveVolume='316859' #6664151  # <1407
    #                                             )

    #     gainList = ib.reqScannerData(hot_stk_by_gain, [])

    #     volList = ib.reqScannerData(hot_stk_by_volume, [])

    #     gainSymList = []
    #     volSymList = []

    #     for stock in gainList:
    #         symbol = stock.contractDetails.contract.symbol
    #         gainSymList.append(symbol)

    #     for stock in volList:
    #         symbol = stock.contractDetails.contract.symbol
    #         volSymList.append(symbol)

    #     duplicateList = ['SQQQ']
    #     scanner = list(set(gainSymList).intersection(volSymList))
    #     scanner = [stock for stock in scanner if stock not in duplicateList]
    #     print(scanner)
        # stockList = []
        # CheckForPreOpen()
        # print(stockList)
    # Pre Market Scanner
    # if(hour == 14 and min == 17 and sec==0):
    # if(hour == 13 and min == 32 and sec==0):
    if(hour == 10 and min == 55 and sec==0): #1955JST
        cashDf = pd.DataFrame(ib.accountValues())
        cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        cash = float(cashDf['value'])
        print(cash)
        # Scanner
        hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='TOP_PERC_GAIN',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='316859' #6664151  # <1407
                                                )

        hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='MOST_ACTIVE_USD', #'HOT_BY_VOLUME',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='316859' #6664151  # <1407
                                                )

        gainList = ib.reqScannerData(hot_stk_by_gain, [])

        volList = ib.reqScannerData(hot_stk_by_volume, [])

        gainSymList = []
        volSymList = []

        for stock in gainList:
            symbol = stock.contractDetails.contract.symbol
            gainSymList.append(symbol)

        for stock in volList:
            symbol = stock.contractDetails.contract.symbol
            volSymList.append(symbol)

        duplicateList = ['SQQQ']
        GetAll()
        scanner = list(set(gainSymList).intersection(volSymList))
        scanner = gainSymList
        scanner = [stock for stock in scanner if stock not in duplicateList]
        print("gainList",gainSymList)
        print("mostActive",volSymList)
        print("scanner",scanner)

    # PreMarket
    if(hour == 14 and min == 10 and sec==0):
        cashDf = pd.DataFrame(ib.accountValues())
        cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        cash = float(cashDf['value'])
        print(cash)
        # Scanner
        hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='TOP_PERC_GAIN',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='316859' #6664151  # <1407
                                                )

        hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='MOST_ACTIVE_USD', #'HOT_BY_VOLUME',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='316859' #6664151  # <1407
                                                )

        gainList = ib.reqScannerData(hot_stk_by_gain, [])

        volList = ib.reqScannerData(hot_stk_by_volume, [])

        gainSymList = []
        volSymList = []

        for stock in gainList:
            symbol = stock.contractDetails.contract.symbol
            gainSymList.append(symbol)

        for stock in volList:
            symbol = stock.contractDetails.contract.symbol
            volSymList.append(symbol)

        duplicateList = ['SQQQ']
        GetAll()
        scanner = list(set(gainSymList).intersection(volSymList))
        scanner = gainSymList
        scanner = [stock for stock in scanner if stock not in duplicateList]
        print("gainList",gainSymList)
        print("mostActive",volSymList)
        print("scanner",scanner)
        stockList = []
        CheckForPreOpen()
        print(stockList)
    #Signal Scanner
    # if(hour == 14 and min == 18 and sec == 0):
    #     stockList = []
    #     CheckForPreOpen()
    #     print(stockList)
    # Market Open Scanner
    # if(hour == 14 and min == 30 and sec == 0):
    if(hour == 14 and min == 30 and sec == 0):
        CheckForOpen()
    # EOD
    # if(hour == 20 and min == 50 and sec == 0):
    #     CloseAll()
