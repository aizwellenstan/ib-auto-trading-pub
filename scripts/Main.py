from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

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

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    print("price ",price)
    print("getOP "+ str(round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)))
    return round(price + ib.reqContractDetails(c)[0].minTick * 1,dps)

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
        outsideRth=True,
        **kwargs)
    stopLoss = StopOrder(
        reverseAction, quantity, stopLossPrice,
        orderId=ib.client.getReqId(),
        transmit=True,
        parentId=parent.orderId,
        outsideRth = True,
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

def CheckForOpen():
    # Scanner
    hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                            locationCode='STK.US.MAJOR',
                                            scanCode='TOP_PERC_GAIN',
                                            # belowPrice='20',
                                            # abovePrice='0.01',
                                            aboveVolume='1408'  # <1407
                                            )

    scanner = ib.reqScannerData(hot_stk_by_volume, [])

    for stock in scanner[:100]:  # loops through the first 10 stocks in the scanner
        try:
            symbol = stock.contractDetails.contract.symbol
            #print(symbol)
            contract = Stock(symbol, 'SMART', 'USD')

            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """
            hisBars = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='360 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

            df = pd.DataFrame(hisBars)
            sma25 = 0
            sma200 = 0
            sma25 = df.close.rolling(window=25).mean().iloc[-1]
            sma200 = df.close.rolling(window=200).mean().iloc[-1]

            hisBars=hisBars[::-1]

            # Main
            atrRange: float = 3.5
            size: int = 100
            k: int = 30 #26
            buy: int = 0
            sell: int = 0
            maxBar: int = 28 #63
            hisBarsLength: int = len(hisBars)

            if(hisBarsLength<size): size = hisBarsLength

            ATR = ((hisBars[1].high - hisBars[1].low) +
                    (hisBars[2].high - hisBars[2].low) +
                    (hisBars[3].high - hisBars[3].low) +
                    (hisBars[4].high - hisBars[4].low) +
                    (hisBars[5].high - hisBars[5].low)) / 5

            currentLongRange = hisBars[1].close - hisBars[0].low
            currentShortRange = hisBars[0].high - hisBars[1].close

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
                                and currentLongRange < ATR/atrRange):
                            if (hisBars[1].close < hisBars[1].open):
                                if (hisBars[1].high - hisBars[1].close
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    buy += 1
                            else:
                                buy += 1

                        if (signalCandleClose3 < signalCandleOpen3
                            and abs(hisBars[k+1].close-hisBars[k*2].open) < bigCandleRange3
                            and endCandleRange3 < bigCandleRange3*0.5
                                and currentShortRange < ATR/atrRange):
                            if (hisBars[1].close > hisBars[1].open):
                                if (hisBars[1].close - hisBars[1].low
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

                maxUsedBar = 7
                if(k<maxBar/maxUsedBar):
                    signalCandleClose6 = hisBars[k*5+1].close
                    signalCandleOpen6 = hisBars[k*6].open
                    bigCandleRange6 = abs(signalCandleClose6 - signalCandleOpen6)
                    smallCandleRange6 = abs(hisBars[k*6+1].close - hisBars[k*7].open)
                    endCandleRange6 = abs(hisBars[1].close - hisBars[k].open)

                    if (bigCandleRange6 > smallCandleRange6 * 4):
                        if (signalCandleClose6 > signalCandleOpen6
                            and abs(hisBars[k*4+1].close - hisBars[k*5].open) < bigCandleRange6
                            and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange6
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange6
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange6
                            and endCandleRange6 < bigCandleRange6*0.5
                                and currentLongRange < ATR/atrRange):
                            if (hisBars[1].close < hisBars[1].open):
                                if (hisBars[1].high - hisBars[1].close
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    buy += 1
                            else:
                                buy += 1

                        if (signalCandleClose6 < signalCandleOpen6
                            and abs(hisBars[k*4+1].close - hisBars[k*5].open) < bigCandleRange6
                            and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange6
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange6
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange6
                            and endCandleRange6 < bigCandleRange6*0.5
                                and currentShortRange < ATR/atrRange):
                            if (hisBars[1].close > hisBars[1].open):
                                if (hisBars[1].close - hisBars[1].low
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

                maxUsedBar = 6
                if(k<maxBar/maxUsedBar):
                    signalCandleClose5 = hisBars[k*4+1].close
                    signalCandleOpen5 = hisBars[k*5].open
                    bigCandleRange5 = abs(signalCandleClose5 - signalCandleOpen5)
                    smallCandleRange5 = abs(hisBars[k*5+1].close - hisBars[k*6].open)
                    endCandleRange5 = abs(hisBars[1].close - hisBars[k].open)

                    if (bigCandleRange5 > smallCandleRange5 * 4):
                        if (signalCandleClose5 > signalCandleOpen5
                            and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange5
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange5
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange5
                            and endCandleRange5 < bigCandleRange5*0.5
                                and currentLongRange < ATR/atrRange):
                            if (hisBars[1].close < hisBars[1].open):
                                if (hisBars[1].high - hisBars[1].close
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    buy += 1
                            else:
                                buy += 1

                        if (signalCandleClose5 < signalCandleOpen5
                            and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange5
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange5
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange5
                            and endCandleRange5 < bigCandleRange5*0.5
                                and currentShortRange < ATR/atrRange):
                            if (hisBars[1].close > hisBars[1].open):
                                if (hisBars[1].close - hisBars[1].low
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    sell += 1
                            else:
                                sell += 1

                maxUsedBar = 5
                if(k<maxBar/maxUsedBar):
                    signalCandleClose4 = hisBars[k*3+1].close
                    signalCandleOpen4 = hisBars[k*4].open
                    bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
                    smallCandleRange4 = abs(hisBars[k*4+1].close - hisBars[k*5].open)
                    endCandleRange4 = abs(hisBars[1].close - hisBars[k].open)

                    if (bigCandleRange4 > smallCandleRange4 * 4):
                        if (signalCandleClose4 > signalCandleOpen4
                            and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange4
                            and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange4
                            and endCandleRange4 < bigCandleRange4*0.5
                                and currentLongRange < ATR/atrRange):
                            if (hisBars[1].close < hisBars[1].open):
                                if (hisBars[1].high - hisBars[1].close
                                        > (hisBars[1].high - hisBars[1].low)*0.13):
                                    buy += 1
                            else:
                                buy += 1

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

                # --- 4btp
                maxUsedBar = 5
                if(k<maxBar/maxUsedBar):
                    if (hisBars[k*4+1].close < hisBars[k*5].open
                        and hisBars[k*3+1].close < hisBars[k*4].open
                        and hisBars[k*2+1].close > hisBars[k*3].open
                        and hisBars[2].close > hisBars[k*2].open
                        and hisBars[1].volume > hisBars[2].volume
                        and hisBars[1].close < hisBars[2].close
                            and currentLongRange < ATR/atrRange):
                        buy += 1

                    if (hisBars[k*4+1].close > hisBars[k*5].open
                        and hisBars[k*3+1].close > hisBars[k*4].open
                        and hisBars[k*2+1].close < hisBars[k*3].open
                        and hisBars[2].close < hisBars[k*2].open
                        and hisBars[1].volume > hisBars[2].volume
                        and hisBars[1].close > hisBars[2].close
                            and currentShortRange < ATR/atrRange):
                        sell += 1

                # bias
                if(hisBarsLength>25 and sma25>0):
                    bias = (hisBars[1].close-sma25)/sma25

                    if(bias < -0.0482831585):
                        buy += 1
                    if(bias > 0.0482831585):
                        sell += 1

                # sma200
                if(hisBarsLength>200 and sma200>0):
                    if(hisBars[1].close < hisBars[2].close
                            and hisBars[1].close > sma200):
                        buy += 1
                    if(hisBars[1].close > hisBars[2].close
                            and hisBars[1].close < sma200):
                        sell += 1
                
                # 8btp
                maxUsedBar = 8
                if(k<maxBar/maxUsedBar):
                    if (hisBars[k*7+1].close < hisBars[k*8].open
                        and hisBars[k*6+1].close < hisBars[k*7].open
                        and hisBars[k*5+1].close < hisBars[k*6].open
                        and hisBars[k*4+1].close < hisBars[k*5].open
                        and hisBars[k*3+1].close > hisBars[k*4].open
                        and hisBars[k*2+1].close > hisBars[k*3].open
                        and hisBars[k+1].close > hisBars[k*2].open
                        and hisBars[1].close < hisBars[k].close
                        and currentLongRange < ATR/atrRange):
                        buy += 1

                    if (hisBars[k*7+1].close > hisBars[k*8].open
                        and hisBars[k*6+1].close < hisBars[k*7].open
                        and hisBars[k*5+1].close < hisBars[k*6].open
                        and hisBars[k*4+1].close < hisBars[k*5].open
                        and hisBars[k*3+1].close > hisBars[k*4].open
                        and hisBars[k*2+1].close > hisBars[k*3].open
                        and hisBars[k+1].close > hisBars[k*2].open
                        and hisBars[1].close < hisBars[k].close
                        and currentShortRange < ATR/atrRange):
                        sell += 1

            # print(ATR)
            # print(currentLongRange)
            # print(currentShortRange)

            if((buy > 0 or sell > 0) and buy != sell):
                if(buy > sell):
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
                        sl = op-(op-low1)*0.3
                        sl = normalizeFloat(sl, ask, bid)
                        if(op != sl):
                            tp = op + (op-sl) * 2
                            tp = normalizeFloat(tp, ask, bid)
                            volMax = int(cash*0.00903/op)
                            vol = int(cash*0.00903/(op-sl))
                            if(vol>volMax): vol=volMax
                            if(vol>=1):
                                spread = 0
                                spread = ask-bid
                                if (spread < (op - sl) * 0.32):
                                    print("BuyStop " + symbol
                                            + " vol " + str(vol)
                                            + " op " + str(op)
                                            + " sl " + str(sl)
                                            + " tp " + str(tp))
                                    #if(symbol != "WNW" and symbol != "AMR" and symbol != "HALL"):
                                    handleBuyStop(contract,vol,op,sl,tp)
                    else:
                        print("ass/bid err ",ask," ",bid)
                """
                elif(sell > buy):
                    high1 = hisBars[1].high
                    op = ask1+(high1-ask)*0.3
                    sl= bid
                    op = normalizeFloat(op, ask, bid)
                    tp = op + (op-sl) * 2
                    tp = normalizeFloat(tp, ask, bid)
                    volMax = int(cash*0.00903/op)
                    vol = int(cash*0.00903/(op-sl))
                    if(vol>volMax): vol=volMax
                    if(vol>=1):
                        if (spread < (op - sl) * 0.32):
                            print("cusBuyStop " + symbol
                                    + " vol " + str(vol)
                                    + " op " + str(op)
                                    + " sl " + str(sl)
                                    + " tp " + str(tp))
                """
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("スキャンは終わりました！,GTHF")

# CheckForOpen()
while(ib.sleep(1)):
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    # sec = ib.reqCurrentTime().second

    # Pre Market Scanner
    if(hour == 13 and min == 45):
        cashDf = pd.DataFrame(ib.accountValues())
        cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        cash = float(cashDf['value'])

    # Market Open Scanner
    if(hour == 14 and min == 30):
        CheckForOpen()
