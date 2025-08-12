from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from modules.normalizeFloat import NormalizeFloat
from modules.movingAverage import Sma

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

exchangeRate = 1
def getExhangeRate(ticker: string):
    global exchangeRate
    contract = Forex(ticker)
    ticker=ib.reqMktData(contract, '', False, False)
    ib.sleep(2)
    exchangeRate = ticker.bid
    if(exchangeRate == -1):
        """timeframes
        1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
        """
        exchangeHisBars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='30 D',
            barSizeSetting='1 day', whatToShow='BID', useRTH=True)
        exchangeHisBars=exchangeHisBars[::-1]
        exchangeRate = exchangeHisBars[0].close
    print(exchangeRate)

cash = 0
total_cash = 0
def update_balance(*args):
    global cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    cash = float(cashDf['value'])
    cash *= exchangeRate
    print(cash)

def update_total_balance(*args):
    global total_cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'TotalCashBalance']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    total_cash *= exchangeRate
    print(total_cash)

risk = 0.00613800895 #* 0.5548 * 0.675 * 0.46

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

class BracketCloseOrder(NamedTuple):
    parent: Order
    takeProfit: Order

def bracketCloseOrder(c,
        action: str, quantity: float, stopLossPrice: float, 
        takeProfitPrice1: float,
        **kwargs) -> BracketCloseOrder:

    assert action in ('BUY', 'SELL')
    reverseAction = 'BUY' if action == 'SELL' else 'SELL'

    parent = StopOrder(
        action, quantity, stopLossPrice,
        orderId=ib.client.getReqId(),
        transmit=True,
        outsideRth=True,
        tif="GTC",
        **kwargs)

    takeProfit1 = LimitOrder(
        action=action, totalQuantity=quantity, lmtPrice=takeProfitPrice1,
        orderId=ib.client.getReqId(),
        transmit=False,
        parentId=parent.orderId,
        outsideRth=False,
        tif="GTC",
        **kwargs)
    
    return BracketCloseOrder(parent, takeProfit1)

def handleBuyStop(contract, vol, op, sl, tp):
    limitPrice = NormalizeFloat(op*1.003032140691, 0.01)
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

def handleCloseOrder(contract, vol, sl, tp):
    high_bracket = bracketCloseOrder(
        contract,
        action='SELL', quantity=vol, stopLossPrice=sl,
        takeProfitPrice1=tp)
    for order in high_bracket:
        order_res = ib.placeOrder(contract=contract, order=order)
    print("Submitted "
            + contract.symbol
            + " UpdatedOrder"
            + " vol " + str(vol)
            + " sl " + str(sl)
            + " tp " + str(tp))


# Scanner
hot_stk_by_gain = ScannerSubscription(instrument='STOCK.HK', # STK
                                        locationCode='STK.HK.TSE_JPN', # STK.US.MAJOR
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice=cash*risk,
                                        abovePrice=11.57*exchangeRate,
                                        aboveVolume='149455'  # <1407
                                        )

hot_stk_by_volume = ScannerSubscription(instrument='STOCK.HK', # STK
                                        locationCode='STK.HK.TSE_JPN', # STK.US.MAJOR
                                        scanCode='HOT_BY_VOLUME',
                                        belowPrice=cash*risk,
                                        abovePrice=11.57*exchangeRate,
                                        aboveVolume='149455'  # <1407
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

def checkPreMarketTime():
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    if(hour < 13 or (hour == 13 and min < 30)): return True
    return False

def CheckForPreOpen():
    for stock in scanner:
        try:
            symbol = stock
            #print(symbol)
            contract = Stock(symbol, 'SMART', 'JPY')

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
            size: int = 550
            k: int = 0 #26
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
            logBp5 = 0
            logBp6 = 0
            logBp7 = 0
            logBias = 0

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
                                    logBp3 += 1
                            else:
                                buy += 1
                                logBp3 += 1

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

                # bias
                if(hisBarsLength>25 and sma25>0):
                    bias = (hisBars[1].close-sma25)/sma25

                    if(bias < -0.2002
                        and hisBars[1].high > hisBars[3].low): 
                        buy += 1
                        logBias += 1
                    if(bias > 0.2002
                        and hisBars[1].low < hisBars[3].high):
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
                    if(logBp5>0): log(symbol + " Bp5")
                    if(logBp6>0): log(symbol + " Bp6")
                    if(logBp7>0): log(symbol + " Bp7")
                    if(logBias>0): log(symbol + " Bias")
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    print("スキャンは終わりました！,GTHF")

def CheckForOpen():
    for stock in stockList:
        try:
            symbol = stock
            contract = Stock(symbol, 'SMART', 'JPY')
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
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            low1 = hisBars[1].low
            if(ask>0 and bid>0):
                op = NormalizeFloat(getOP(contract, ask), ask, bid)
                sl = op-(op-low1)*0.30753353973168214654282765737875
                sl = NormalizeFloat(sl, ask, bid)
                if(op != sl):
                    tp = op + (op-sl) * 4.72
                    tp = NormalizeFloat(tp, ask, bid)
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


# CheckForPreOpen()
# print("gainSymList ",gainSymList)
# print("volSymList ",volSymList)
# print("scanner ",scanner)
# print(stockList)
# CheckForOpen()

while(ib.sleep(1)):
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    sec = ib.reqCurrentTime().second

    # Pre Market Scanner
    if(hour == 23 and min == 30 and sec == 0):
        cashDf = pd.DataFrame(ib.accountValues())
        cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
        cashDf = cashDf.loc[cashDf['currency'] == 'USD']
        cash = float(cashDf['value'])
        # exchange USD to JPY
        contract = Forex('USDJPY')
        ticker=ib.reqMktData(contract, '', False, False)
        ib.sleep(2)
        exchangeRate = ticker.bid
        if(exchangeRate == -1):
            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """
            exchangeHisBars = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='30 D',
                barSizeSetting='1 day', whatToShow='BID', useRTH=True)
            exchangeHisBars=exchangeHisBars[::-1]
            exchangeRate = exchangeHisBars[0].close
        print(exchangeRate)
        cash = cash*exchangeRate
        print(cash)
        # Scanner
        hot_stk_by_gain = ScannerSubscription(instrument='STOCK.HK', # STK
                                                locationCode='STK.HK.TSE_JPN', # STK.US.MAJOR
                                                scanCode='TOP_PERC_GAIN',
                                                belowPrice=cash*risk,
                                                abovePrice=11.57*exchangeRate,
                                                aboveVolume='149455'  # <1407
                                                )

        hot_stk_by_volume = ScannerSubscription(instrument='STOCK.HK', # STK
                                                locationCode='STK.HK.TSE_JPN', # STK.US.MAJOR
                                                scanCode='HOT_BY_VOLUME',
                                                belowPrice=cash*risk,
                                                abovePrice=11.57*exchangeRate,
                                                aboveVolume='149455'  # <1407
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
    # Market Open Scanner
    if(hour == 0 and min == 0 and sec == 15):
        CheckForPreOpen()
        print(stockList)
        CheckForOpen()

def cancelUntriggered():
    oos = list(ib.openOrders())
    ib.client.reqAllOpenOrders()  # issue reqAllOpenOrders() directly to IB API, this is a non blocking call
    dummy = ib.reqOpenOrders()    # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
    aoos = list(ib.openOrders())  # the orders received from issuing reqAllOpenOrders() are correctly captured
    for oo in aoos:
        print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
        if oo.orderType == "STP LMT":
            ib.cancelOrder(oo)

def cancelAllOrders():
    oos = list(ib.openOrders())
    ib.client.reqAllOpenOrders()  # issue reqAllOpenOrders() directly to IB API, this is a non blocking call
    dummy = ib.reqOpenOrders()    # blocking until openOrderEnd messages (may receive two, ib_insync seems not to care
    aoos = list(ib.openOrders())  # the orders received from issuing reqAllOpenOrders() are correctly captured
    for oo in aoos:
        print(f"  order for client {oo.clientId}, id {oo.orderId}, permid {oo.permId}")
        ib.cancelOrder(oo)

keepOpenList = []
closeByMarketList = []
def close_all():
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        contract = position.contract
        if(contract.symbol in closeByMarketList):
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
    global closeByMarketList
    positions = ib.positions()  # A list of positions, according to IB
    cancelAllOrders()
    for position in positions:
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
        if (math.isnan(bid) or bid < 0):
            try:
                bid = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

                ask = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='1 D',
                barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close
            except:
                closeByMarketList.append(contract.symbol)
                continue
        print("symbol ",contract.symbol," bid " +str(bid)," ask ",str(ask))
        if position.position > 0: # Number of active Long positions
            action = 'Sell' # to offset the long positions
        elif position.position < 0: # Number of active Short positions
            action = 'Buy' # to offset the short positions
        else:
            assert False
        if not  (math.isnan(bid) or bid < 0):
            vol = abs(position.position)
            handleCloseOrder(contract, vol, bid, ask)
            print(f'Flatten Position: {action} {vol} {contract.localSymbol}')

# import time
def main():
    # start = time.time()
    global IsTesting
    IsTesting = False
    getExhangeRate('USDJPY')
    update_total_balance()
    update_balance()
    # getPerformanceMoreSymList()
    # getDRSymList()
    # getREITSymList()
    # get_scanner()
    # remove_duplicate()
    # print(scanner)
    # getADRList()
    # getMarketCondition()
    # check_for_pre_open()
    # check_for_jared()
    # print(stock_list)

    # check_for_open()
    # end = time.time()
    # print("time cost",end-start)

    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        min = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second

        if(hour == 12 and min == 56 and sec == 0):
            update_total_balance()
            update_balance()
            getPerformanceMoreSymList()
            getDRSymList()
            getREITSymList()
            get_scanner()
            remove_duplicate()
            print(scanner)
            getADRList()
            getMarketCondition()
            # getIndustryList()
            check_for_pre_open()
            check_for_jared()
            print(stock_list)

        if(hour == 13 and min == 30 and sec == 5):
            check_for_open()

        # EOD Cancel
        if(hour == 15 and min == 00 and sec == 0):
            cancelUntriggered()

        # EOD Limit
        if(hour == 18 and min == 45 and sec == 0):
            close_all_limit()
            
        # EOD
        if(hour == 18 and min == 46 and sec == 0):
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
