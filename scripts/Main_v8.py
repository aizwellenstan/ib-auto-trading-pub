from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log

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
risk = 0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

# Scanner
hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice=cash*risk,
                                        abovePrice='6.31',
                                        aboveVolume='6036850'  # <1407
                                        )

hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='HOT_BY_VOLUME',
                                        belowPrice=cash*risk,
                                        abovePrice='6.31',
                                        aboveVolume='6036850'  # <1407
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

scanner = list(set(gainSymList).intersection(volSymList))
stockList = []

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    #print("price ",price)
    #print("getOP "+ str(round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)))
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

def CheckForPreOpen():
    for stock in scanner:
        try:
            symbol = stock
            #print(symbol)
            contract = Stock(symbol, 'SMART', 'USD')

            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """
            hisBars = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            df = pd.DataFrame(hisBars)
            # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            #     print(df)
            sma25 = 0
            # sma200 = 0
            sma25 = df.close.rolling(window=25).mean().iloc[-1]
            secondSma25 = df.close.rolling(window=25).mean().iloc[-2]
            # sma200 = df.close.rolling(window=200).mean().iloc[-1]

            hisBars=hisBars[::-1]

            # Main
            atrRange: float = 4
            size: int = 4 #4
            sizeH8: int = 30
            sizeH4: int = 30
            sizeH3: int = 2
            sizeH2: int = 2
            sizeH1: int = 2
            sizeM30: int = 1
            k: int = 0 #26
            l: int = 0
            m: int = 0
            n: int = 0
            o: int = 0
            p: int = 0
            q: int = 0
            buy: int = 0
            sell: int = 0
            maxBar: int = 28 #63
            hisBarsLength: int = len(hisBars)

            if(hisBarsLength<5): continue
            if(hisBarsLength<size): size = hisBarsLength

            ATR = ((hisBars[1].high - hisBars[1].low) +
                    (hisBars[2].high - hisBars[2].low) +
                    (hisBars[3].high - hisBars[3].low) +
                    (hisBars[4].high - hisBars[4].low) +
                    (hisBars[5].high - hisBars[5].low)) / 5

            currentLongRange = hisBars[1].close - hisBars[0].low
            currentShortRange = hisBars[0].high - hisBars[1].close

            logBp3 = 0
            logBp4 = 0
            logBias = 0
            logH8Bp3 = 0
            logH8Bp4 = 0
            logH4Bp3 = 0
            logH3Bp3 = 0
            logH2Bp3 = 0
            logH1Bp3 = 0
            logM30Bp3 = 0

            while(k < size):
                k += 1
                maxUsedBar = 4
                if(k<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBars[k*2+1].close
                    signalCandleOpen3 = hisBars[k*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBars[k*3+1].close - hisBars[k*4].open)
                    endCandleRange3 = abs(hisBars[1].close - hisBars[k].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
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
                            else:
                                buy += 1
                                logBp3 += 1

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
                # bias
                # if(hisBarsLength>25 and sma25>0):
                #     bias = (hisBars[1].close-sma25)/sma25
                #     bias2 = (hisBars[2].close-secondSma25)/secondSma25

                #     if(bias < -0.0482831585
                #         and bias2 < -0.0482831585
                #         and bias2 > bias):
                #         buy += 1
                #         logBias += 1
                #     if(bias > 0.0482831585
                #         and bias2 > 0.0482831585
                #         and bias2 < bias):
                #         sell += 1

                # #bias
                if(hisBarsLength>25 and sma25>0):
                    bias = (hisBars[1].close-sma25)/sma25
                    bias2 = (hisBars[2].close-sma25)/sma25

                    if(bias < -0.2002
                        and bias2 < -0.2002
                        and hisBars[1].high > hisBars[3].low
                        and hisBars[1].high > hisBars[6].high): 
                        buy += 1
                        logBias += 1
                    if(bias > 0.2002
                        and bias2 > 0.2002
                        and hisBars[1].low < hisBars[3].high
                        and hisBars[1].low < hisBars[6].low):
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
                    smallCandleRange3 = abs(hisBarsH8[l*3+1].close - hisBarsH8[l*4].open)
                    endCandleRange3 = abs(hisBarsH8[1].close - hisBarsH8[l].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
                        if (signalCandleClose3 > signalCandleOpen3
                            and abs(hisBarsH8[l+1].close - hisBarsH8[l*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                            and hisBarsH8[2].high < hisBarsH8[3].high
                                and currentLongRange < ATR/atrRange):
                            if (hisBarsH8[1].close < hisBarsH8[1].open):
                                if (hisBarsH8[1].high - hisBarsH8[1].close
                                        > (hisBarsH8[1].high - hisBarsH8[1].low)*0.13):
                                    buy += 1
                                    logBp3 += 1
                            else:
                                buy += 1
                                logH8Bp3 += 1

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

            hisBarsH4 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='4 hours', whatToShow='ASK', useRTH=False)

            hisBarsH4=hisBarsH4[::-1]

            while(m < sizeH4):
                m += 1
                maxUsedBar = 4
                if(m<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH4[m*2+1].close
                    signalCandleOpen3 = hisBarsH4[m*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBarsH4[m*3+1].close - hisBarsH4[m*4].open)
                    endCandleRange3 = abs(hisBarsH4[1].close - hisBarsH4[m].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
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
            
            hisBarsH3 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='3 hours', whatToShow='ASK', useRTH=False)

            hisBarsH3=hisBarsH3[::-1]

            while(n < sizeH3):
                n += 1
                maxUsedBar = 4
                if(n<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH3[n*2+1].close
                    signalCandleOpen3 = hisBarsH3[n*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBarsH3[n*3+1].close - hisBarsH3[n*4].open)
                    endCandleRange3 = abs(hisBarsH3[1].close - hisBarsH3[n].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
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

            hisBarsH2 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='30 D',
                barSizeSetting='2 hours', whatToShow='ASK', useRTH=False)

            hisBarsH2=hisBarsH2[::-1]

            while(o < sizeH2):
                o += 1
                maxUsedBar = 4
                if(o<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH2[o*2+1].close
                    signalCandleOpen3 = hisBarsH2[o*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBarsH2[o*3+1].close - hisBarsH2[o*4].open)
                    endCandleRange3 = abs(hisBarsH2[1].close - hisBarsH2[o].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
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

            hisBarsH1 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='30 D',
                barSizeSetting='1 hour', whatToShow='ASK', useRTH=False)

            hisBarsH1=hisBarsH1[::-1]

            while(p < sizeH1):
                p += 1
                maxUsedBar = 4
                if(p<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsH1[p*2+1].close
                    signalCandleOpen3 = hisBarsH1[p*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBarsH1[p*3+1].close - hisBarsH1[p*4].open)
                    endCandleRange3 = abs(hisBarsH1[1].close - hisBarsH1[p].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
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

            hisBarsM30 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='30 D',
                barSizeSetting='30 mins', whatToShow='ASK', useRTH=False)

            hisBarsM30=hisBarsM30[::-1]

            while(q < sizeM30):
                q += 1
                maxUsedBar = 4
                if(q<maxBar/maxUsedBar):
                    signalCandleClose3 = hisBarsM30[q*2+1].close
                    signalCandleOpen3 = hisBarsM30[q*3].open
                    bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
                    smallCandleRange3 = abs(hisBarsM30[q*3+1].close - hisBarsM30[q*4].open)
                    endCandleRange3 = abs(hisBarsM30[1].close - hisBarsM30[q].open)

                    if (bigCandleRange3 > smallCandleRange3 * 4):
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

            # print(ATR)
            # print(currentLongRange)
            # print(currentShortRange)

            if((buy > 0 or sell > 0) and buy != sell):
                if(buy > sell):
                    stockList.append(symbol)

                    # Log
                    if(logBp3>0): log(symbol + " Bp3")
                    if(logBp4>0): log(symbol + " Bp4")
                    if(logBias>0): log(symbol + " Bias")
                    if(logH8Bp3>0): log(symbol + " H8Bp3")
                    if(logH8Bp4>0): log(symbol + " H8Bp4")
                    if(logH4Bp3>0): log(symbol + " H4Bp3")
                    if(logH3Bp3>0): log(symbol + " H3Bp3")
                    if(logH2Bp3>0): log(symbol + " H2Bp3")
                    if(logH1Bp3>0): log(symbol + " H1Bp3")
                    if(logM30Bp3>0): log(symbol + " M30Bp3")
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
                op = normalizeFloat(getOP(contract, ask), ask, bid)
                sl = op-(op-low1)*0.30753353973168214654282765737875
                sl = normalizeFloat(sl, ask, bid)
                if(op != sl):
                    tp = op + (op-sl) * 2.79#4.72
                    tp = normalizeFloat(tp, ask, bid)
                    volMax = int(cash*risk/op)
                    vol = int(cash*risk/(op-sl))
                    if(vol>volMax): vol=volMax
                    if(vol>=1):
                        spread = 0
                        spread = ask-bid
                        if (spread < (op - sl) * 0.28):
                            log("BuyStop " + symbol
                                    + " vol " + str(vol)
                                    + " op " + str(op)
                                    + " sl " + str(sl)
                                    + " tp " + str(tp))
                            #if(symbol != "WNW" and symbol != "AMR" and symbol != "HALL"):
                            diff = 0.00063717746183
                            if(abs((op-sl)/sl)<diff):
                                print("sl too close")
                            else:
                               handleBuyStop(contract,vol,op,sl,tp)
            else:
                print("ask/bid err ",ask," ",bid)
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("Open終わりました！,GTHF")

stockList = []
CheckForPreOpen()
print("gainSymList ",gainSymList)
print("volSymList ",volSymList)
print("scanner ",scanner)

print(stockList)
CheckForOpen()

while(ib.sleep(1)):
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    sec = ib.reqCurrentTime().second

    # Pre Market Scanner
    if(hour == 13 and min == 45 and sec==0):
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
                                                aboveVolume='6036850'  # <1407
                                                )

        hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='HOT_BY_VOLUME',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='6036850'  # <1407
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

        scanner = list(set(gainSymList).intersection(volSymList))
        CheckForPreOpen()
        print(stockList)
    # Pre Market Scanner
    if(hour == 12 and min == 45 and sec==0):
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
                                                aboveVolume='6036850'  # <1407
                                                )

        hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='HOT_BY_VOLUME',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='6036850'  # <1407
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

        scanner = list(set(gainSymList).intersection(volSymList))
        stockList = []
        CheckForPreOpen()
        print(stockList)
    # Pre Market Scanner
    if(hour == 13 and min == 25 and sec==0):
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
                                                aboveVolume='6036850'  # <1407
                                                )

        hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                                locationCode='STK.US.MAJOR',
                                                scanCode='HOT_BY_VOLUME',
                                                belowPrice=cash*risk,
                                                abovePrice='6.31',
                                                aboveVolume='6036850'  # <1407
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

        scanner = list(set(gainSymList).intersection(volSymList))
        stockList = []
        CheckForPreOpen()
        print(stockList)
    # Market Open Scanner
    if(hour == 13 and min == 30 and sec == 0):
        CheckForOpen()
