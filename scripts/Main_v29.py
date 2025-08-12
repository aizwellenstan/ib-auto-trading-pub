from ib_insync import *
import numpy as np
import pandas as pd
import math
from typing import NamedTuple
import sys
sys.path.append('.')
from logger import log
from datetime import datetime as dt, timedelta
import json
from modules.normalizeFloat import NormalizeFloat
from modules.movingAverage import Sma
from modules.aiztradingview import GetPerformance,GetADR,GetIndustry,GetDR,GetREIT,GetRvol,GetPerformanceJP,GetDailyWinner,GetDailyWinnerJP
from modules.vwap import Vwap
import yfinance as yf
from collections import defaultdict
from inspect import currentframe

import alpaca_trade_api as tradeapi
api = tradeapi.REST(,
                    secret_key="",
                    base_url='https://paper-api.alpaca.markets')
shortable_list = [l for l in api.list_assets() if l.shortable]


shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

exchangeRate = 1
currency = 'USD'
basicPoint = 0.01
def getExhangeRate(ticker :str):
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

def getOP(price, basicPoint):
    return price + basicPoint

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
    limitPrice = NormalizeFloat(op*1.003032140691, basicPoint)
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

duplicate_list = ['SOXL','PLTR','SPCE','CSCO','SHIP','ABNB','FIVE','ALF',
'OPINL','SDHY','PSTH','AEI','TUEM','VOLT','ALF','MCFE','PEB PRG','CRBU',
'NGTF','ISPI','MATW','KEYS','CAT','GPRO','SEM','BPOP','ACCD','TREX','ISUN',
'AUUD','AXR','APLS','SMTC','CCEP','FANG','CULL','PLAN','LIFE','LBRT','DRKA',
'TRKA','XEC','JUPW','ABNB','GOOS','UROY','GBS','MNMD','MRUS','FTEK','IVT',
'SMH','NXTD','PVAC','AGRO','CLEU','CLDR','CYBR','SDIG','LQDA','RBOT','BENE',
'OPEN','RPAI','POLY','CMPX','TCS',
'PLTR','SPRT',
'9318']
performanceSymList = []
drSymList = []
reitSymList = []
winnerList = []
scanner = []
adrDict = []
industryDict = {}
industryListGroup = {}
industryLeaderBoard = {}
# ---List section---
stockList = [] # List for open
# ---end list section---

timeD = dt.strptime(str(ib.reqCurrentTime().date()), '%Y-%m-%d')
usCheckPreChangeTime = timeD + timedelta(hours = 22) + timedelta(minutes = 28)
usMarketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
endDateTimeD1 = ''
endDateTimePreScanner=''
endDateTimeAskBid = ''

contractQQQ = Stock('QQQ', 'SMART', 'USD')
contractSPY = Stock('SPY', 'SMART', 'USD')
contractVTI = Stock('VTI', 'SMART', 'USD')
contractDIA = Stock('DIA', 'SMART', 'USD')
contractIWM = Stock('IWM', 'SMART', 'USD')

hisBarsQQQD1 = []
hisBarsSPYD1 = []
hisBarsVTID1 = []
hisBarsDIAD1 = []
hisBarsIWMD1 = []
hisBarsD1Dict = {}

IsTesting = False
def get_linenumber():
    if IsTesting:
        cf = currentframe()
        print(cf.f_back.f_lineno)
        
def getTestingTF(date :str):
    global timeD, usCheckPreChangeTime, usMarketOpenTime, endDateTimeD1, endDateTimePreScanner, endDateTimeAskBid
    timeD = dt.strptime(str(date), '%Y-%m-%d')
    usCheckPreChangeTime = timeD + timedelta(hours = 22) + timedelta(minutes = 29)
    usMarketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
    jpMarketOpenTime = timeD + timedelta(hours = 0) + timedelta(minutes = 0)
    if currency == 'USD':
        endDateTimeD1 = usMarketOpenTime+timedelta(minutes=1)
        endDateTimePreScanner = timeD + timedelta(hours = 21) + timedelta(minutes = 56)
        endDateTimeAskBid = usMarketOpenTime+timedelta(seconds=10)
    else:
        endDateTimeD1 = jpMarketOpenTime+timedelta(minutes=1)
        endDateTimePreScanner = timeD -timedelta(days = 1) + timedelta(hours = 23) + timedelta(minutes = 26)
        endDateTimeAskBid = jpMarketOpenTime+timedelta(seconds=10)

def getMarketCondition():
    global hisBarsQQQD1, hisBarsSPYD1, hisBarsVTID1, hisBarsDIAD1, hisBarsIWMD1
    hisBarsQQQD1 = ib.reqHistoricalData(
    contractQQQ, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsSPYD1 = ib.reqHistoricalData(
    contractSPY, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsVTID1 = ib.reqHistoricalData(
    contractVTI, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsDIAD1 = ib.reqHistoricalData(
    contractDIA, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsIWMD1 = ib.reqHistoricalData(
    contractIWM, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsQQQD1 = hisBarsQQQD1[::-1]
    hisBarsSPYD1 = hisBarsSPYD1[::-1]
    hisBarsVTID1 = hisBarsVTID1[::-1]
    hisBarsDIAD1 = hisBarsDIAD1[::-1]
    hisBarsIWMD1 = hisBarsIWMD1[::-1]

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
    minute = ib.reqCurrentTime().minute
    if IsTesting: return False
    if currency == 'USD':
        if(hour < 13 or (hour == 13 and minute < 30)): return True
    else:
        if hour <= 23 and hour > 9: return True
    return False

def checkHisBarsD1(shift, hisBarsD1, symbol):
    global industryLeaderBoard, industryDict, hisBarsD1Dict
    op = hisBarsD1[0].close
    print(symbol,op)
    
    try:
        if not checkOPLimit(op): return False
        if (
            hisBarsD1[4-shift].high-hisBarsD1[4-shift].low < 0.01 or
            hisBarsD1[3-shift].high-hisBarsD1[3-shift].low < 0.01 or
            hisBarsD1[2-shift].high-hisBarsD1[2-shift].low < 0.01 or
            hisBarsD1[1-shift].high-hisBarsD1[1-shift].low < 0.01
        ): return False

        if len(hisBarsD1) > 41:
            if (
                abs(hisBarsD1[1-shift].close - hisBarsD1[20-shift].open) < 0.01 or
                abs(hisBarsD1[21-shift].close - hisBarsD1[40-shift].open) < 0.01
            ): return False
        get_linenumber()

        stockInfo = yf.Ticker(symbol)
        vwapDf = stockInfo.history(period="365d")
        v = vwapDf.Volume.values
        h = vwapDf.High.values
        l = vwapDf.Low.values
        vwapDf['Vwap'] = Vwap(v,h,l)

        mask = vwapDf.index < str(timeD.date())
        vwapDf = vwapDf.loc[mask]
        vwap = vwapDf.iloc[-1].Vwap

        if len(hisBarsD1) > 5:
            # mfi
            typicalPrice = (
                vwapDf['Close']+vwapDf['High']
                +vwapDf['Low']
            ) / 3

            moneyFlow = typicalPrice * vwapDf['Volume']

            negativeFlow = []
            positiveFlow = []

            period = 5
            for i in range(1, period+1):
                if typicalPrice[i] > typicalPrice[i-1]:
                    positiveFlow.append(moneyFlow[i-1])
                    negativeFlow.append(0)
                elif typicalPrice[i] < typicalPrice[i-1]:
                    positiveFlow.append(0)
                    negativeFlow.append(moneyFlow[i-1])
                else:
                    positiveFlow.append(0)
                    negativeFlow.append(0)

            positiveMf = []
            negativeMf = []

            
            for i in range(period-1, len(positiveFlow)):
                positiveMf.append(sum(positiveFlow[i+1-period:i+1]))
            for i in range(period-1, len(negativeFlow)):
                negativeMf.append(sum(negativeFlow[i+1-period:i+1]))

            mfi = 100*(np.array(positiveMf))/(np.array(positiveMf)+np.array(negativeMf))
            if mfi[-1] > 87: return False

        volList = []
        volPeriod = 2
        for i in range(1,volPeriod+1):
            volList.append(vwapDf.iloc[-i].Volume)

        SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)
        bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
        if bias < -0.53: return False
        get_linenumber()

        volPeriod = 3
        volList.append(vwapDf.iloc[-volPeriod].Volume)
        SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

        bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
        if bias < -0.69: return False
        get_linenumber()

        volPeriod = 4
        volList.append(vwapDf.iloc[-volPeriod].Volume)
        SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

        bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
        if bias < -0.79: return False
        get_linenumber()

        if len(hisBarsD1) > 8:
            volList = []
            volPeriod = 8
            for i in range(1,volPeriod+1):
                volList.append(vwapDf.iloc[-i].Volume)
            SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

            bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
            if bias < -0.67: return False
            get_linenumber()

            if len(hisBarsD1) > 17:
                volList = []
                volPeriod = 17
                for i in range(1,volPeriod+1):
                    volList.append(vwapDf.iloc[-i].Volume)
                SmaVolD1 = Sma(volList[0:volPeriod], volPeriod)

                bias = (vwapDf.iloc[-1].Volume-SmaVolD1)/SmaVolD1
                if bias < -0.64: return False
            get_linenumber()

        bias = (hisBarsD1[1-shift].low-vwap)/vwap
        if bias > 1.31: return False
        get_linenumber()

        if symbol in shortableSymList:
            if bias > 0.71: return False
        get_linenumber()

        bias = (hisBarsD1[1-shift].close-vwap)/vwap

        if bias > 1.07: return False
        get_linenumber()

        if symbol in shortableSymList:
            if bias > 0.7: return False
        get_linenumber()

        if symbol in shortableSymList:
            if len(hisBarsD1) > 121:
                if hisBarsD1[1-shift].close / hisBarsD1[120-shift].close < 0.44:
                    return False
            get_linenumber()
            if len(hisBarsD1) > 181:
                if hisBarsD1[1-shift].close / hisBarsD1[180-shift].close < 0.64:
                    return False
        get_linenumber()

        if currency == 'USD':
            if (
                hisBarsQQQD1[1-shift].close > hisBarsQQQD1[1-shift].open * 1.0003 and
                hisBarsSPYD1[1-shift].close > hisBarsSPYD1[1-shift].open * 1.0003 and
                hisBarsVTID1[1-shift].close > hisBarsVTID1[1-shift].open * 1.0003 and
                hisBarsDIAD1[1-shift].close > hisBarsDIAD1[1-shift].open * 1.0003 and
                hisBarsIWMD1[1-shift].close > hisBarsIWMD1[1-shift].open * 1.0003 and
                hisBarsD1[1-shift].close < hisBarsD1[1-shift].open * 0.98
            ): return False
            get_linenumber()

            if (
                hisBarsQQQD1[2-shift].close > hisBarsQQQD1[2-shift].open and
                hisBarsQQQD1[1-shift].close > hisBarsQQQD1[1-shift].open and
                hisBarsSPYD1[2-shift].close > hisBarsSPYD1[2-shift].open and
                hisBarsSPYD1[1-shift].close > hisBarsSPYD1[1-shift].open and
                hisBarsD1[2-shift].close < hisBarsD1[2-shift].open * 0.97 and
                hisBarsD1[1-shift].close < hisBarsD1[1-shift].open * 0.97
            ): return False
        get_linenumber()

        if symbol in shortableSymList:
            if hisBarsD1[1-shift].close / hisBarsD1[1-shift].open > 1.08:
                return False
            if hisBarsD1[1-shift].close / hisBarsD1[2-shift].close > 1.12:
                return False
            if hisBarsD1[1-shift].close / hisBarsD1[3-shift].close > 1.08:
                return False
            if hisBarsD1[1-shift].close / hisBarsD1[3-shift].open > 1.47:
                return False
            if hisBarsD1[1-shift].close / hisBarsD1[4-shift].close > 1.15:
                return False

            get_linenumber()
            
            if hisBarsD1[1-shift].close / hisBarsD1[3-shift].open > 1.47:
                print(hisBarsD1[1-shift].close / hisBarsD1[3-shift].open)
                return False
        get_linenumber()

        if (
            hisBarsD1[4-shift].close >= hisBarsD1[4-shift].open and
            hisBarsD1[2-shift].close >= hisBarsD1[2-shift].open and
            hisBarsD1[1-shift].close >= hisBarsD1[1-shift].open
        ):
            if hisBarsD1[1-shift].close / hisBarsD1[5-shift].open > 1.08:
                return False
        get_linenumber()

        if not (
            (
                hisBarsD1[2-shift].close < hisBarsD1[2-shift].open and
                hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
            ) or
            (
                hisBarsD1[4-shift].close < hisBarsD1[4-shift].open and
                hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
                hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
                hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
            ) or
            hisBarsD1[1-shift].close / hisBarsD1[1-shift].low > 1.1180648619673 or
            (
                hisBarsD1[3-shift].close > hisBarsD1[3-shift].open and
                hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
                hisBarsD1[1-shift].close > hisBarsD1[1-shift].open
            )
        ):
            if hisBarsD1[1-shift].close / hisBarsD1[5-shift].open > 1.18:
                return False
        get_linenumber()

        hisBarsD1avgPriceArr = []
        hisBarsD1closeArr = []
        for d in hisBarsD1:
            avgPrice = (d.high+d.low) / 2
            hisBarsD1avgPriceArr.append(avgPrice)
            hisBarsD1closeArr.append(d.close)

        if symbol in shortableSymList:
            smaD1 = Sma(hisBarsD1avgPriceArr[1-shift:4-shift], 3)
            bias = (hisBarsD1[1-shift].close-smaD1)/smaD1
            if bias < -0.17: return False

            smaD1 = Sma(hisBarsD1avgPriceArr[1-shift:5-shift], 4)
            bias = (hisBarsD1[1-shift].close-smaD1)/smaD1
            if bias < -0.07: return False

        if len(hisBarsD1) > 29:
            if not (
                hisBarsD1[1-shift].close <= hisBarsD1[1-shift].open or
                (
                    hisBarsD1[1].close > hisBarsD1[4].high and
                    hisBarsD1[1].close > hisBarsD1[3].high and
                    hisBarsD1[1].close > hisBarsD1[2].high
                )
            ):
                smaD1 = Sma(hisBarsD1avgPriceArr[1-shift:29-shift], 28)
                bias = (hisBarsD1[1-shift].close-smaD1)/smaD1
                if bias < -0.17: return False
        get_linenumber()

        if symbol in shortableSymList and len(hisBarsD1) > 51:
            smaD1 = Sma(hisBarsD1closeArr[1-shift:51-shift], 50)
            bias = (hisBarsD1[1-shift].close-smaD1)/smaD1
            if bias > 0.55: return False
            if symbol in shortableSymList:
                if bias < -0.31: return False
        get_linenumber()

        if len(hisBarsD1) > 9:
            if not (
                (
                    hisBarsD1[2-shift].close > hisBarsD1[2-shift].open and
                    hisBarsD1[1-shift].close < hisBarsD1[1-shift].open
                ) or
                (
                    ((hisBarsD1[4-shift].high-hisBarsD1[4-shift].close) / (hisBarsD1[4-shift].high-hisBarsD1[4-shift].low) > 0.76) and
                    ((hisBarsD1[3-shift].high-hisBarsD1[3-shift].close) / (hisBarsD1[3-shift].high-hisBarsD1[3-shift].low) > 0.76) and
                    ((hisBarsD1[2-shift].high-hisBarsD1[2-shift].close) / (hisBarsD1[2-shift].high-hisBarsD1[2-shift].low) > 0.76) and
                    ((hisBarsD1[1-shift].high-hisBarsD1[1-shift].close) / (hisBarsD1[1-shift].high-hisBarsD1[1-shift].low) > 0.76)
                )
            ):
                smaD1 = Sma(hisBarsD1closeArr[1-shift:9-shift], 8)
                bias = (hisBarsD1[1-shift].close-smaD1)/smaD1
                if bias < - 0.09: return False
            get_linenumber()

        # Industry
        if symbol in shortableSymList or currency != 'USD':
            industryCheck = False
            industryCheckPeriod = 4
            curIndustryGain = hisBarsD1[1-shift].close / hisBarsD1[industryCheckPeriod-shift].open
            industryLeader = curIndustryGain
            if symbol in industryDict:
                industry = industryDict[symbol]
                groupList = industryListGroup[industry]
                if len(groupList) > 1:
                    if industry in industryLeaderBoard:
                        industryLeader = industryLeaderBoard[industry]
                    else:
                        for sym2 in groupList:
                            print(sym2)
                            if sym2 in duplicate_list: continue
                            sym2hisBarsD1 = []
                            if sym2 not in hisBarsD1Dict:
                                sym2contract = Stock(sym2, 'SMART', 'USD')
                                sym2hisBarsD1 = ib.reqHistoricalData(
                                    sym2contract, endDateTime='', durationStr='60 D',
                                    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                                if len(sym2hisBarsD1) < 5: continue
                                sym2hisBarsD1 = sym2hisBarsD1[::-1]
                                hisBarsD1Dict[sym2] = sym2hisBarsD1
                            else:
                                sym2hisBarsD1 = hisBarsD1Dict[sym2]
                            industryGain = sym2hisBarsD1[1-shift].close / sym2hisBarsD1[industryCheckPeriod-shift].open
                            if industryGain > industryLeader:
                                industryLeader = industryGain
                        industryLeaderBoard[industry] = industryLeader
                else:
                    industryCheck = True
                
                qqqGain = hisBarsQQQD1[1-shift].close / hisBarsQQQD1[industryCheckPeriod-shift].open
                spyGain = hisBarsSPYD1[1-shift].close / hisBarsSPYD1[industryCheckPeriod-shift].open
                
                if (
                    industryLeader > qqqGain * 0.95 and
                    industryLeader > spyGain * 0.96
                ):
                    if (
                        curIndustryGain > industryLeader * 0.47
                    ):  industryCheck = True
                if not industryCheck: return False
        
        print(symbol,"passed")
        return True
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def checkScanner(shift, symbol):
    global hisBarsD1Dict
    try:
        # Pre check bars before marketopen
        hisBarsD1 = []
        if symbol not in hisBarsD1Dict:
            contract = Stock(symbol, 'SMART', currency)
            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=endDateTimeD1, durationStr='60 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            count = 0
            while len(hisBarsD1) < 1 and count < 7:
                ib.sleep(1)
                hisBarsD1 = ib.reqHistoricalData(
                    contract, endDateTime=endDateTimeD1, durationStr='60 D',
                    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                count += 1
            if len(hisBarsD1) < 5: return False
            hisBarsD1 = hisBarsD1[::-1]
            hisBarsD1Dict[symbol] = hisBarsD1
        else:
            hisBarsD1 = hisBarsD1Dict[symbol]
        if not checkHisBarsD1(shift,hisBarsD1,symbol):
            return False
        elif symbol not in stockList:
            if symbol in adrDict:
                adr = adrDict[symbol]
            else:
                adr = hisBarsD1[1].high-hisBarsD1[1].low
            tp = hisBarsD1[1-shift].high+adr*3.7109498732843145
            tp = NormalizeFloat(tp,basicPoint)
            stockList.append(
                {
                    's':symbol,
                    'close1':hisBarsD1[1-shift].close,
                    'adr': adr,
                    'tp': tp
                }
            )
        return True
    except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)

def getPerformanceSymList(currency :str):
    global performanceSymList
    if currency == 'USD':
        performanceSymList = GetPerformance()
    else:
        performanceSymList = GetPerformanceJP()

def getDRSymList():
    global drSymList
    drSymList = GetDR()

def getREITSymList(currency :str):
    global reitSymList
    reitSymList = GetREIT()

def getADR(currency :str):
    global adrDict
    adrDict = GetADR(currency)

def getIndustryDict(currency :str):
    global industryDict, industryListGroup
    industryDict = GetIndustry(currency)
    industryListGroup = defaultdict(list)
    for key, val in sorted(industryDict.items()):
        industryListGroup[val].append(key)

def getWinnerList(currency :str):
    global winnerList
    if currency == 'USD':
        winnerList = GetDailyWinner()
    else:
        winnerList = GetDailyWinnerJP()
        
# Scanner
def get_scanner():
    global scanner

    for sym in performanceSymList:
        if sym not in scanner:
            scanner.append(sym)
    for sym in drSymList:
        if sym not in scanner:
            scanner.append(sym)
    for sym in reitSymList:
        if sym not in scanner:
            scanner.append(sym)
    if IsTesting:
        for sym in winnerList:
            if sym not in scanner:
                scanner.append(sym)
    remove_duplicate()
    print('scanner',scanner)

def checkOPLimit(op):
    if op > total_cash/45.9122298953: return False
    sl = op - 0.14
    if op > 16.5:
        sl = op * 0.9930862018
    if op > 100:
        sl = op * 0.9977520318
    if abs(op - sl) < 0.01: return False
    vol = int(total_cash * risk / (op - sl))
    volLimit = 1
    if currency == 'JPY':
        volLimit = 100
    if(
        op < total_cash*0.83657741748/volLimit
        and vol >= volLimit
    ): return True

    return False

def checkPreOpen():
    try:
        shift = 0
        if checkPreMarketTime(): shift = 1
        for sym in scanner:
            checkScanner(shift,sym)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
    print("スキャンは終わりました！,GTHF")

jared = []
def checkForJared():
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
        contract, endDateTime=usCheckPreChangeTime, durationStr='5280 S',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=4):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=usCheckPreChangeTime, durationStr='5280 S',
            barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
        maxTrys += 1
    preMaxHigh = 0
    preMinLow = 9999
    for i in hisBarsM1:
        if i.high > preMaxHigh:
            preMaxHigh = i.high
        if i.low < preMinLow:
            preMinLow = i.low
    preMarketChange = hisBarsM1[-1].close / hisBarsM1[0].open
    return preMaxHigh, preMinLow, preMarketChange

def checkPreChange():
    global stockList
    passedList = []
    for stock in stockList:
        try:
            symbol = stock['s']
            contract = Stock(symbol, 'SMART', currency)

            if currency == 'USD':
                preMaxHigh, preMinLow, preMarketChange = getPreMarketRange(contract)
                # if preMarketChange < 1.0231189575451873: continue
                print(symbol,"preMarketChange",preMarketChange)
                
                if preMaxHigh - preMinLow < 0.01: continue
                print("preMaxHigh",preMaxHigh,"preMinLow",preMinLow)
                stock['preMaxHigh'] = preMaxHigh
                stock['preMinLow'] = preMinLow
                passedList.append(stock)
            
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    stockList = passedList

oppened_list = []
def checkOpen():
    print(stockList)
    qqqgapRangeHigh = 0.0
    iwmgapRangeHigh = 0.0
    qqqgapRange = 0.0
    spygapRange = 0.0
    vtigapRange = 0.0
    diagapRange = 0.0
    iwmgapRange = 0.0

    if currency == 'USD':
        global hisBarsQQQD1, hisBarsSPYD1, hisBarsVTID1, hisBarsDIAD1, hisBarsIWMD1
        hisBarsQQQD1 = ib.reqHistoricalData(
        contractQQQ, endDateTime=endDateTimeD1, durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        hisBarsSPYD1 = ib.reqHistoricalData(
        contractSPY, endDateTime=endDateTimeD1, durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        hisBarsVTID1 = ib.reqHistoricalData(
        contractVTI, endDateTime=endDateTimeD1, durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        hisBarsDIAD1 = ib.reqHistoricalData(
        contractDIA, endDateTime=endDateTimeD1, durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        hisBarsIWMD1 = ib.reqHistoricalData(
        contractIWM, endDateTime=endDateTimeD1, durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

        qqqgapRangeHigh = hisBarsQQQD1[-1].open/hisBarsQQQD1[-2].high
        iwmgapRangeHigh = hisBarsIWMD1[-1].open/hisBarsIWMD1[-2].high

        qqqgapRange = hisBarsQQQD1[-1].open/hisBarsQQQD1[-2].close
        spygapRange = hisBarsSPYD1[-1].open/hisBarsSPYD1[-2].close
        vtigapRange = hisBarsVTID1[-1].open/hisBarsVTID1[-2].close
        diagapRange = hisBarsDIAD1[-1].open/hisBarsDIAD1[-2].close
        iwmgapRange = hisBarsIWMD1[-1].open/hisBarsIWMD1[-2].close

    cost = 0
    if currency == 'USD':
        rvolSymList = GetRvol()
    # global stockList
    for stock in stockList:
        try:
            symbol = stock['s']
            if currency == 'USD':
                if symbol not in rvolSymList: continue
            if symbol in oppened_list: continue
            contract = Stock(symbol, 'SMART', currency)

            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=endDateTimeD1, durationStr='9 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            if len(hisBarsD1) < 6: continue

            gapRange = hisBarsD1[-1].open - hisBarsD1[-2].close

            if IsTesting: print(symbol)
            
            if currency == 'USD':
                gap = hisBarsD1[-1].open/hisBarsD1[-2].high
                if (
                    gap < qqqgapRangeHigh * 0.937 or 
                    gap < iwmgapRangeHigh * 0.937
                ):
                    if IsTesting:
                        print(gap / qqqgapRange)
                        print(gap / iwmgapRange)
                    continue
                get_linenumber()
                
                gap = hisBarsD1[-1].open/hisBarsD1[-2].close
                if (
                    gap < qqqgapRange * 1.014 or 
                    gap < spygapRange * 1.014 or
                    gap < vtigapRange * 1.014 or
                    gap < diagapRange * 1.014 or
                    gap < iwmgapRange * 1.014
                ): 
                    if IsTesting:
                        print(gap / qqqgapRange)
                        print(gap / spygapRange)
                        print(gap / vtigapRange)
                        print(gap / diagapRange)
                        print(gap / iwmgapRange)
                    continue
                get_linenumber()

            spread = 0.0
            ask = 0.0
            bid = 0.0

            if not IsTesting:
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
                    continue
            spread = ask-bid
            opM30 = getOP(ask,basicPoint)
            print(symbol,opM30)
            if opM30 < stock['close1'] * 1.02: continue
            if currency == 'USD':
                preMaxHigh = stock['preMaxHigh']
                preMinLow = stock['preMinLow']
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            if(ask>0 and bid>0):
                if currency == 'USD':
                    op = NormalizeFloat(preMaxHigh + 0.01 * 16, basicPoint)
                else:
                    op = NormalizeFloat(ask + 0.01 * 16, basicPoint)
                if op > total_cash/45.9122298953: continue
                sl = NormalizeFloat(op - stock['adr'] * 0.05, basicPoint)
                if stock['adr'] > 0.14:
                    sl = NormalizeFloat(op - stock['adr'] * 0.35, basicPoint)
                if sl < hisBarsD1[-2].close: sl = hisBarsD1[-2].close
                if op - sl < basicPoint * 2: continue
                print("op",op,"sl",sl)
                vol = int(total_cash*risk/(op-sl))
                maxVol = int(cash/2/(op*1.003032140691))
                if vol > maxVol: vol = maxVol
                volLimit = 7
                if op >= 14: volLimit = 5
                if stock['adr'] > 2: volLimit = 1
                if currency == 'JPY':
                    if vol < 100: continue
                if(vol >= volLimit):
                    tp = stock['tp']
                    if (tp-op) / (op-sl) < 1: continue
                    spread = 0
                    spread = ask-bid
                    spreadPercent = 0.32
                    if currency == 'JPY':
                        spreadPercent = 0.51
                    spreadFixed = 2.1
                    print(symbol,"spreadPercent",spread/(op - sl))
                    if spread < 0.89: spreadPercent = 1.52
                    if spread < 0.19: spreadPercent = 1.64
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
def closeAll():
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

def closeAllLimit():
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

def checkScannerFilter(currency):
    performanceSymList = []
    if currency == 'USD':
        performanceSymList = GetPerformance()
    else:
        performanceSymList = GetPerformanceJP()
    if "ALZN" not in performanceSymList:
        print("WORST SCANNER IN THIS CENTURY")
    else:
        print("よくやった！")

import time
def main():
    dayLightSaving = True
    global IsTesting, currency, basicPoint, cash, jared
    IsTesting = False
    start = time.time()
    if IsTesting:
        getTestingTF('2021-11-05')

        # getTestingTF('2021-10-21')
        # jared = ['DWAC']
        # getTestingTF('2021-10-22')
        # jared = ['PHUN']
        # # getTestingTF('2021-10-25')
        # # jared = ['BKKT']
        # getTestingTF('2021-11-03')
        # jared = ['PTPI']
        # getTestingTF('2021-11-05')
        # jared = ['ALZN']
    currency = 'USD'
    # currency = 'JPY'
    if currency == 'JPY':
        getExhangeRate('USDJPY')
        basicPoint = 1
    update_total_balance()
    update_balance()
    if IsTesting:
        cash = total_cash
        getWinnerList(currency)
        checkScannerFilter(currency)
    else:
        getPerformanceSymList(currency)
    if currency == 'USD':
        if not IsTesting:
            getDRSymList()
            getREITSymList(currency)
        getMarketCondition()
    getIndustryDict(currency)
    get_scanner()
    getADR(currency)
    checkPreOpen()
    if currency == 'USD':
        checkForJared()
    print(stockList)
    end = time.time()
    print("time cost",end-start)

    # if currency == 'USD':
    #     checkPreChange()
    # checkOpen()
    while(ib.sleep(1)):
        hour = ib.reqCurrentTime().hour
        minute = ib.reqCurrentTime().minute
        sec = ib.reqCurrentTime().second

        if currency == 'USD':
            # if(hour == 12 and minute == 55 and sec == 0):
            #     update_total_balance()
            #     update_balance()
            #     getPerformanceSymList(currency)
            #     getDRSymList()
            #     getREITSymList(currency)
            #     get_scanner()
            #     getADR(currency)
            #     getMarketCondition()
            #     getIndustryDict(currency)
            #     checkPreOpen()
            #     checkForJared()
            #     print(stockList)
            if dayLightSaving:
                if(hour == 13 and minute == 28 and sec == 0):
                    checkPreChange()

                if(hour == 13 and minute == 30 and sec == 5):
                    checkOpen()

                # EOD Cancel
                if(hour == 13 and minute == 46 and sec == 0):
                    cancelUntriggered()

                # EOD Limit
                if(hour == 17 and minute == 46 and sec == 0):
                    closeAllLimit()
                    
                # EOD
                if(hour == 17 and minute == 47 and sec == 0):
                    closeAll()
            else:
                if(hour == 14 and minute == 28 and sec == 0):
                    checkPreChange()

                if(hour == 14 and minute == 30 and sec == 5):
                    checkOpen()

                # EOD Cancel
                if(hour == 14 and minute == 46 and sec == 0):
                    cancelUntriggered()

                # EOD Limit
                if(hour == 18 and minute == 46 and sec == 0):
                    closeAllLimit()
                    
                # EOD
                if(hour == 18 and minute == 47 and sec == 0):
                    closeAll()
        else:
            if(hour == 23 and minute == 26 and sec == 0):
                update_total_balance()
                update_balance()
                getPerformanceSymList(currency)
                get_scanner()
                getADR(currency)
                checkPreOpen()
                print(stockList)

            if(hour == 0 and minute == 0 and sec == 0):
                checkOpen()

            # EOD Cancel
            if(hour == 1 and minute == 30 and sec == 0):
                cancelUntriggered()

            # EOD Limit
            if(hour == 2 and minute == 11 and sec == 0):
                closeAllLimit()
                
            # EOD
            if(hour == 2 and minute == 12 and sec == 0):
                closeAll()

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