rootPath = '../..'
import sys
sys.path.append(rootPath)
from modules.dict import take
from modules.aiztradingview import GetClose
import pandas as pd
import math
from typing import NamedTuple
from modules.normalizeFloat import NormalizeFloat
from modules.aiztradingview import GetADR
from modules.discord import Alert
from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=14)


risk = 0.00613800895 #* 0.5548 * 0.675 * 0.46

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
        transmit=True,
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

def handleBuyStop(contract, vol, op, sl, tp, basicPoint):
    vol = int(vol)
    limitPrice = NormalizeFloat(min(op*1.003032140691,op+0.15), basicPoint)
    high_bracket = bracketStopLimitOrderTwoTargets(
        contract,
        action='BUY', quantity=vol, stopPrice=op,
        limitPrice=limitPrice,
        takeProfitPrice1=tp,
        stopLossPrice=sl)
    for order in high_bracket:
        order_res = ib.placeOrder(contract=contract, order=order)
    trade = f"Submitted {contract.symbol} BuyStop vol {vol} op {op} sl {sl} tp {tp}"
    print(trade)
    Alert(trade)

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
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    print(total_cash)

def GetSL(op, adr, basicPoint):
    sl = op - 0.14
    if op > 16.5: sl = op * 0.9930862018
    if op > 100: sl = op * 0.9977520318
    if adr > 0.63: sl = op - adr * 0.4
    elif adr > 0.14: sl = op - adr * 0.35
    else: sl = op - adr * 0.05
    if adr > 1.21:
        if op - sl < basicPoint * 63:
            sl = op - basicPoint * 63
        if sl < 0:
            sl = op - basicPoint * 40
    elif adr > 0.47:
        if op - sl < basicPoint * 49:
            sl = op - basicPoint * 49
        if sl < 0:
            sl = op - basicPoint * 40
    elif adr > 0.2:
        if op - sl < basicPoint * 40:  
            sl = op - basicPoint * 40
    else:
        if (
            op - sl < basicPoint * 2 or
            op - sl > basicPoint * 40
        ):  
            sl = op - basicPoint * 40
        if op - sl < basicPoint * 40:
            sl = op - basicPoint * 40
    return sl

def HandleBuyMarket(symbol, vol, adrDict, currency):
    if vol < 1: return 0
    contract = Stock(symbol, 'SMART', 'USD')

    ask = 0.0
    bid = 0.0

    ticker=ib.reqMktData(contract, '', False, False)
    ib.sleep(2)
    ask = ticker.ask
    bid = ticker.bid
    retryCount = 0
    while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
        print("retry")
        ticker=ib.reqMktData(contract, '', False, False)
        ib.sleep(3)
        ask = ticker.ask
        bid = ticker.bid
        retryCount += 1

    if (math.isnan(bid) or bid < 0.2):
        try:
            bid = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='1 D',
            barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

            ask = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='1 D',
            barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close
        except:
            print("math.isnan(bid) or bid < 0.2")
            return 0

    if(ask>0 and bid>0):
        op = ask
        basicPoint = 0.01
        sl = GetSL(op, adrDict[symbol], basicPoint)
        print(f"ask {ask} bid {bid}")
        # hisBarsD1 = ib.reqHistoricalData(
        #     contract, endDateTime='', durationStr='2 D',
        #     barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        # if sl < hisBarsD1[-2].close or op - sl < basicPoint * 2: 
        #     sl = hisBarsD1[-2].close
        sl = NormalizeFloat(sl, basicPoint)
        tp = op + (op-sl) * 15.42857143
        tp = NormalizeFloat(tp, basicPoint)
        spread = ask-bid
        spreadPercent = 0.32
        if currency == 'JPY':
            spreadPercent = 0.51
        spreadFixed = 9.75
        print(symbol,"spreadPercent",spread/(op - sl),spread)
        if spread < 9.75: spreadPercent = 97.5
        if (spread < (op - sl) * spreadPercent and spread < spreadFixed):
            # handleBuyStop(contract,vol,op,sl,tp,basicPoint)
            action = 'Buy'
            order = MarketOrder(action=action, totalQuantity=int(vol))
            trade = ib.placeOrder(contract, order)
    # print(contract,order)
    return vol

def GetTotalCash(*args):
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidationByCurrency']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    return total_cash


def GetVol(op, adr, basicPoint):
    op = op + basicPoint * 19
    if (
        op > total_cash/11.78749878165677 and
        adr < 9.31
    ): return 0
    sl = GetSL(op, adr, basicPoint)
    vol = int(total_cash*risk/(op-sl))
    if adr < 0.53:
        if vol < 3: return 0
    maxVol = int(cash/2/(op*1.003032140691))
    if vol > maxVol: vol = maxVol

    return vol

def main():
    total_cash = GetTotalCash()
    update_balance()
    update_total_balance()

    # optionCost = 259 + 80 + 307 + 102
    # optionCost = 259 + 61 + 5 + 729 + 102
    optionCost = 4386
    total_cash -= optionCost
    total_cash /= 2

    currency = 'USD'

    adrDict = GetADR(currency)
    basicPoint = 0.01
    noTradeList = ['TENX']
    tradeList = ['CHRS']
    for symbol in tradeList:
        print(symbol)
        adr = adrDict[symbol]
        ask = 0.0
        bid = 0.0
        contract = Stock(symbol, 'SMART', currency)
        ticker=ib.reqMktData(contract, '', False, False)
        ib.sleep(2)
        ask = ticker.ask
        bid = ticker.bid
        retryCount = 0

        while (math.isnan(bid) or bid < 0.2) and retryCount < 1:
            print("retry")
            ticker=ib.reqMktData(contract, '', False, False)
            ib.sleep(3)
            ask = ticker.ask
            bid = ticker.bid
            retryCount += 1

        if (math.isnan(bid) or bid < 0.2):
            try:
                bid = ib.reqHistoricalData(
                contract, endDateTime=endDateTimeAskBid, durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

                ask = ib.reqHistoricalData(
                contract, endDateTime=endDateTimeAskBid, durationStr='1 D',
                barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close
            except:
                print("math.isnan(bid) or bid < 0.2")
                continue
            spread = ask-bid
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))         

        if(ask>0 and bid>0):
            op = ask + basicPoint * 1
            op = NormalizeFloat(op, basicPoint)
            vol = GetVol(op, adr, basicPoint)
            print(op, adr)
            print(symbol, vol)
        else:
            print(ask,bid)
    
    # for symbol, vol in openDict.items():
    #     HandleBuyMarket(symbol, vol, adrDict, currency)

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