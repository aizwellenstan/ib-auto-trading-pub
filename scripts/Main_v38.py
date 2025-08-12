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
from modules.sharpe import GetMaxDD
from modules.predict import RbfPredict, SvrLinearPredict
from modules.movingAverage import Sma
from modules.aiztradingview import GetPerformance,GetADR,GetDR,GetPerformanceJP,GetDailyWinner,GetDailyWinnerJP
from modules.shareholders import GetShareholders, GetZScore, GetOperatingCash
from modules.vwap import Vwap
from modules.rsi import Rsi
from modules.technicalAnalysis import PlotLines
from modules.slope import GetSlopeUpper, GetSlopeLower, GetSlopeUpperNew, GetSlopeLowerNew
from modules.insider import GetInsider
import yfinance as yf
from collections import defaultdict
from inspect import currentframe

import alpaca_trade_api as tradeapi
shortable_list = []
try:
    api = tradeapi.REST(,
                        secret_key="",
                        base_url='https://paper-api.alpaca.markets')
    shortable_list = [l for l in api.list_assets() if l.shortable]
except: pass

shortableSymList = []
for sym in shortable_list:
    shortableSymList.append(sym.symbol)

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

currency = 'USD'
basicPoint = 0.01

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
    # limitPrice = NormalizeFloat(op*1.003032140691, basicPoint)
    limitPrice = NormalizeFloat(min(op*1.003032140691,op+0.15), basicPoint)
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
'OPEN','RPAI','POLY','CMPX','TCS','EYEG','MCLD','AVGR',
'PLTR','SPRT',
'9318']
performanceSymList = []
drSymList = []
winnerList = []
scanner = []
adrDict = []
# ---List section---
stockList = [] # List for open
# ---end list section---

dayLightSaving = True
timeD = dt.strptime(str(ib.reqCurrentTime().date()), '%Y-%m-%d')
usCheckPreChangeTime = timeD + timedelta(hours = 22) + timedelta(minutes = 26)
usMarketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
endDateTimeD1 = ''
endDateTimePreScanner=''
endDateTimeAskBid = ''

contractIWM = Stock('IWM', 'SMART', 'USD')
contractHYG = Stock('HYG', 'SMART', 'USD')

isBearish = False

IsTesting = False
def get_linenumber():
    if IsTesting:
        cf = currentframe()
        print(cf.f_back.f_lineno)
        
def getTestingTF(date :str):
    global timeD, usCheckPreChangeTime, usMarketOpenTime, endDateTimeD1, endDateTimePreScanner, endDateTimeAskBid
    timeD = dt.strptime(str(date), '%Y-%m-%d')
    usCheckPreChangeTime = timeD + timedelta(hours = 23) + timedelta(minutes = 26)
    usMarketOpenTime = timeD + timedelta(hours = 23) + timedelta(minutes = 30)
    if dayLightSaving:
        usCheckPreChangeTime = timeD + timedelta(hours = 22) + timedelta(minutes = 27)
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
    global isBearish

    stockInfo = yf.Ticker("IWM")
    iwmDf = stockInfo.history(period="365d")
    mask = iwmDf.index < str(timeD.date())
    iwmDf = iwmDf.loc[mask]
    df = iwmDf[['Open','High','Low','Close']]
    df = df.tail(49)
    npArr = df.to_numpy()
    lower = GetSlopeLowerNew(npArr)
    if lower < 0: 
        isBearish = True
        return 0
    get_linenumber()

    df = iwmDf[['Open','High','Low','Close']]
    npArr = df.to_numpy()
    upper = GetSlopeUpper(npArr)
    if upper < 0: 
        isBearish = True
        return 0

def GetDf(symbol :str):
    stockInfo = yf.Ticker(symbol)
    df = stockInfo.history(period="max")
    mask = df.index < str(timeD.date())
    df = df.loc[mask]

    return df

def checkMarketVol():
    spydf = GetDf('SPY')
    slvdf = GetDf('SLV')
    tltdf = GetDf('TLT')
    lqddf = GetDf('LQD')
    vwodf = GetDf('VWO')
    veadf = GetDf('VEA')
    iaudf = GetDf('IAU')
    xlfdf = GetDf('XLF')
    xledf = GetDf('XLE')
    soxldf = GetDf('SOXL')
    spxudf = GetDf('SPXU')
    tzadf = GetDf('TZA')
    xludf = GetDf('XLU')
    xlpdf = GetDf('XLP')
    xlvdf = GetDf('XLV')
    qiddf = GetDf('QID')

    if (
        spydf.iloc[-1].Volume > spydf.iloc[-1].Volume and
        spydf.iloc[-2].Volume > spydf.iloc[-3].Volume
    ):
        print('increasing vol spy')
        return False
    if (
        slvdf.iloc[-1].Volume > slvdf.iloc[-1].Volume and
        slvdf.iloc[-2].Volume > slvdf.iloc[-3].Volume
    ):
        print('increasing vol SLV')
        return False
    if (
        tltdf.iloc[-1].Volume < tltdf.iloc[-1].Volume and
        tltdf.iloc[-2].Volume < tltdf.iloc[-3].Volume
    ):
        print('decresing vol TLT')
        return False
    if (
        lqddf.iloc[-1].Volume < lqddf.iloc[-1].Volume and
        lqddf.iloc[-2].Volume < lqddf.iloc[-3].Volume
    ):
        print('decresing vol LQD')
        return False
    if (
        vwodf.iloc[-1].Volume > vwodf.iloc[-1].Volume and
        vwodf.iloc[-2].Volume > vwodf.iloc[-3].Volume
    ):
        print('incresing vol VWO')
        return False
    if (
        veadf.iloc[-1].Volume > veadf.iloc[-1].Volume and
        veadf.iloc[-2].Volume > veadf.iloc[-3].Volume
    ):
        print('incresing vol VEA')
        return False
    if (
        iaudf.iloc[-1].Volume > iaudf.iloc[-1].Volume and
        iaudf.iloc[-2].Volume > iaudf.iloc[-3].Volume
    ):
        print('incresing vol IAU')
        return False
    if (
        xlfdf.iloc[-1].Volume < xlfdf.iloc[-1].Volume and
        xlfdf.iloc[-2].Volume < xlfdf.iloc[-3].Volume
    ):
        print('decresing vol XLF')
        return False
    if (
        xledf.iloc[-1].Volume < xledf.iloc[-1].Volume and
        xledf.iloc[-2].Volume < xledf.iloc[-3].Volume
    ):
        print('decresing vol XLE')
        return False
    if (
        soxldf.iloc[-1].Volume < soxldf.iloc[-1].Volume and
        soxldf.iloc[-2].Volume < soxldf.iloc[-3].Volume
    ):
        print('decresing vol SOXL')
        return False
    if (
        spxudf.iloc[-1].Volume < spxudf.iloc[-1].Volume and
        spxudf.iloc[-2].Volume < spxudf.iloc[-3].Volume
    ):
        print('decresing vol SPXU')
        return False
    if (
        tzadf.iloc[-1].Volume > tzadf.iloc[-1].Volume and
        tzadf.iloc[-2].Volume > tzadf.iloc[-3].Volume
    ):
        print('incresing vol TZA')
        return False
    if (
        xludf.iloc[-1].Volume < xludf.iloc[-1].Volume and
        xludf.iloc[-2].Volume < xludf.iloc[-3].Volume
    ):
        print('decresing vol XLU')
        return False
    if (
        xlpdf.iloc[-1].Volume < xlpdf.iloc[-1].Volume and
        xlpdf.iloc[-2].Volume < xlpdf.iloc[-3].Volume
    ):
        print('decresing vol XLP')
        return False
    if (
        xlvdf.iloc[-1].Volume > xlvdf.iloc[-1].Volume and
        xlvdf.iloc[-2].Volume > xlvdf.iloc[-3].Volume
    ):
        print('incresing vol XLV')
        return False
    if (
        qiddf.iloc[-1].Volume < qiddf.iloc[-1].Volume and
        qiddf.iloc[-2].Volume < qiddf.iloc[-3].Volume
    ):
        print('decresing vol QID')
        return False
    if (
        veadf.iloc[-1].Volume > veadf.iloc[-1].Volume and
        veadf.iloc[-2].Volume > veadf.iloc[-3].Volume
    ):
        print('incresing vol VEA')
        return False
    return True
   
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

def checkOPLimit(op, adr):
    op = op + basicPoint * 19
    if (
        op > total_cash/35.174947894851236 and
        adr < 9.31
    ): return False
    sl = op - 0.14
    if op > 16.5:
        sl = op * 0.9930862018
    if op > 100:
        sl = op * 0.9977520318
    if abs(op - sl) < 0.01: return False
    vol = int(total_cash * risk / (op - sl))

    if adr > 0.63: sl = op - adr * 0.4
    elif adr > 0.14: sl = op - adr * 0.35
    else: sl = op - adr * 0.05

    vol = int(total_cash*risk/(op-sl))
    maxVol = int(cash/2/(op*1.003032140691))
    if vol > maxVol: vol = maxVol
    volLimit = 7
    if op >= 14: volLimit = 5
    if adr > 0.47: volLimit = 3
    if adr > 2: volLimit = 1
    if currency == 'JPY':
        if vol < 100: return False

    if(
        op < total_cash*0.83657741748/volLimit and 
        vol >= volLimit
    ): return True

    return False

def GetSL(op, adr):
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

def GetVol(op, adr):
    op = op + basicPoint * 19
    if (
        op > total_cash/11.78749878165677 and
        adr < 9.31
    ): return 0
    sl = GetSL(op, adr)
    vol = int(total_cash*risk/(op-sl))
    if adr < 0.53:
        if vol < 3: return 0
    maxVol = int(cash/2/(op*1.003032140691))
    if vol > maxVol: vol = maxVol

    return vol

def checkHisBarsD1(vwapDf, symbol, adr):
    try:
        op = vwapDf.iloc[-1].Close
        print(symbol,op)
        
        if not checkOPLimit(op, adr): return False

        if len(vwapDf) > 1:
            if vwapDf.iloc[-1].Volume < 1900: return False
        get_linenumber()

        if len(vwapDf) > 1:
            if vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low < 0.01: return False
        get_linenumber()

        if len(vwapDf) > 1:
            if vwapDf.iloc[-1].Close/vwapDf.iloc[-1].Vwap>6.8: return False
        get_linenumber()

        # # 3 bar up
        # if len(vwapDf) > 3:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open
        #     ): return False
        # get_linenumber()

        # # 3bar play
        # if len(vwapDf) > 3:
        #     if not (
        #         vwapDf.iloc[-2].Open - vwapDf.iloc[-2].Close >
        #         vwapDf.iloc[-3].High - vwapDf.iloc[-2].Low
        #     ):
        #         if (
        #             vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #             vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
        #             vwapDf.iloc[-1].Low > vwapDf.iloc[-1].Vwap and
        #             vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #             vwapDf.iloc[-2].High - vwapDf.iloc[-2].Low >
        #             abs(vwapDf.iloc[-3].Close - vwapDf.iloc[-3].Open) and
        #             vwapDf.iloc[-2].High - vwapDf.iloc[-2].Low >
        #             abs(vwapDf.iloc[-4].Close - vwapDf.iloc[-4].Open)
        #         ): return False
        # get_linenumber()

        # # last 50 day trend
        # if len(vwapDf) > 50:
        #     if (
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-50].Close * 0.5186480010297015
        #     ):
        #         dwn = 0
        #         for i in range(1, 50):
        #             if vwapDf.iloc[i].Close < vwapDf.iloc[i].Open:
        #                 dwn += 1
        #         if dwn/50 > 0.51: return False
        # get_linenumber()

        if (
            vwapDf.iloc[-1].Open == vwapDf.iloc[-1].Low and
            vwapDf.iloc[-1].Close == vwapDf.iloc[-1].High
        ): return False
        get_linenumber()

        # if len(vwapDf) > 2:
        #     if (
        #         vwapDf.iloc[-2].High < vwapDf.iloc[-3].Low and
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 9:
        #     if (
        #         vwapDf.iloc[-9].Close > vwapDf.iloc[-9].Open and
        #         vwapDf.iloc[-2].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-2].Low > vwapDf.iloc[-9].Low and
        #         vwapDf.iloc[-3].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-3].Low > vwapDf.iloc[-9].Low and
        #         vwapDf.iloc[-4].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-4].Low > vwapDf.iloc[-9].Low and
        #         vwapDf.iloc[-5].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-5].Low > vwapDf.iloc[-9].Low and
        #         vwapDf.iloc[-6].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-6].Low > vwapDf.iloc[-9].Low and
        #         vwapDf.iloc[-7].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-7].Low > vwapDf.iloc[-9].Low and
        #         vwapDf.iloc[-8].High < vwapDf.iloc[-9].High and
        #         vwapDf.iloc[-8].Low > vwapDf.iloc[-9].Low
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-2].Open < vwapDf.iloc[-3].Low and
                vwapDf.iloc[-2].High > vwapDf.iloc[-3].High and
                vwapDf.iloc[-2].Low < vwapDf.iloc[-3].Low and
                vwapDf.iloc[-2].High > vwapDf.iloc[-4].High and
                vwapDf.iloc[-2].Low < vwapDf.iloc[-4].Low
            ): return False
        get_linenumber()

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low > 0.01 and
                vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low > 0.01
            ):
                if (
                    vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                    vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open and
                    vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                    vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                    vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
                    vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
                    (
                        (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Close) /
                        (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low)
                    ) > 0.74 and
                    (
                        (vwapDf.iloc[-2].High-vwapDf.iloc[-2].Close) /
                        (vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low)
                    ) > 0.74
                ): return False
        get_linenumber()

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-3].Open > vwapDf.iloc[-4].High
            ): return False
        get_linenumber()

        # if len(vwapDf) > 3:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
        #         vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
        #         vwapDf.iloc[-1].High < vwapDf.iloc[-3].High and
        #         vwapDf.iloc[-1].Low > vwapDf.iloc[-3].Low
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 2:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
        #         vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Open
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 100:
        #     closeArr = vwapDf.Close.values.tolist()
        #     closeArr = closeArr[-100:]
        #     stddev = np.std(closeArr)
        #     mean = np.mean(closeArr)
        #     upperBand = mean+(2.4 * stddev)

        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Low > upperBand
        #     ): return False
        # get_linenumber()

        if (
            vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
            vwapDf.iloc[-1].Rsi > 96.97
        ): return False
        get_linenumber()

        # gap & failed
        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-1].Open > vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-2].Open > vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-3].Open > vwapDf.iloc[-4].Close and
                vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
                vwapDf.iloc[-4].Open > vwapDf.iloc[-5].Close
            ): return False
        get_linenumber()

        # # 4 gap down
        # if len(vwapDf) > 4:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Open < vwapDf.iloc[-2].Close and
        #         vwapDf.iloc[-2].Open < vwapDf.iloc[-3].Close and
        #         vwapDf.iloc[-3].Open < vwapDf.iloc[-4].Close
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 4:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Vwap / vwapDf.iloc[-1].Close <
        #         vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close and
        #         vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close <
        #         vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close and
        #         vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close <
        #         vwapDf.iloc[-4].Vwap / vwapDf.iloc[-4].Close
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Open / vwapDf.iloc[-1].Close >
                vwapDf.iloc[-2].Open / vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-2].Open / vwapDf.iloc[-2].Close >
                vwapDf.iloc[-3].Open / vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-3].Open / vwapDf.iloc[-3].Close >
                vwapDf.iloc[-4].Open / vwapDf.iloc[-4].Close and
                vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
                vwapDf.iloc[-4].Open / vwapDf.iloc[-4].Close >
                vwapDf.iloc[-5].Open / vwapDf.iloc[-5].Close
            ): return False
        get_linenumber()

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Open / vwapDf.iloc[-1].Close >
                vwapDf.iloc[-2].Open / vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].Open / vwapDf.iloc[-2].Close >
                vwapDf.iloc[-3].Open / vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].Open / vwapDf.iloc[-3].Close >
                vwapDf.iloc[-4].Open / vwapDf.iloc[-4].Close and
                vwapDf.iloc[-4].Open / vwapDf.iloc[-4].Close >
                vwapDf.iloc[-5].Open / vwapDf.iloc[-5].Close and
                vwapDf.iloc[-5].Open / vwapDf.iloc[-5].Close >
                vwapDf.iloc[-6].Open / vwapDf.iloc[-6].Close
            ): return False
        get_linenumber()

        # if len(vwapDf) > 5:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
        #         vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
        #         vwapDf.iloc[-5].Close < vwapDf.iloc[-5].Open
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-1].Open > vwapDf.iloc[-2].Close and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-2].Low
            ): return False
        get_linenumber()

        # if len(vwapDf) > 4:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
        #         vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
        #         vwapDf.iloc[-1].Open > vwapDf.iloc[-2].Close and
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-2].High
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 5:
        #     if (
        #         vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low > 0 and
        #         vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low > 0 and
        #         vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low > 0 and
        #         vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low > 0 and
        #         vwapDf.iloc[-5].High-vwapDf.iloc[-5].Low > 0
        #     ):
        #         if (
        #             vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #             abs(vwapDf.iloc[-1].Close-vwapDf.iloc[-1].Open) /
        #             (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low) < 0.45 and
        #             abs(vwapDf.iloc[-2].Close-vwapDf.iloc[-2].Open) /
        #             (vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low) < 0.45 and
        #             abs(vwapDf.iloc[-3].Close-vwapDf.iloc[-3].Open) /
        #             (vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low) < 0.45 and
        #             abs(vwapDf.iloc[-4].Close-vwapDf.iloc[-4].Open) /
        #             (vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low) < 0.45
        #         ): return False
        # get_linenumber()

        # if len(vwapDf) > 5:
        #     if (
        #         vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low > 0 and
        #         vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low > 0 and
        #         vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low > 0 and
        #         vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low > 0 and
        #         vwapDf.iloc[-5].High-vwapDf.iloc[-5].Low > 0
        #     ):
        #         if (
        #             vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #             abs(vwapDf.iloc[-1].Close-vwapDf.iloc[-1].Open) /
        #             (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low) < 0.5 and
        #             abs(vwapDf.iloc[-2].Close-vwapDf.iloc[-2].Open) /
        #             (vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low) < 0.5 and
        #             abs(vwapDf.iloc[-3].Close-vwapDf.iloc[-3].Open) /
        #             (vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low) < 0.5 and
        #             abs(vwapDf.iloc[-4].Close-vwapDf.iloc[-4].Open) /
        #             (vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low) < 0.5 and
        #             abs(vwapDf.iloc[-5].Close-vwapDf.iloc[-5].Open) /
        #             (vwapDf.iloc[-5].High-vwapDf.iloc[-5].Low) < 0.5
        #         ): return False
        # get_linenumber()

        # if len(vwapDf) > 3:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Vwap and
        #         vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Vwap
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 3:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Vwap and
        #         vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Vwap
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 4:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Vwap / vwapDf.iloc[-1].Close <
        #         vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close and
        #         vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close >
        #         vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close and
        #         vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close <
        #         vwapDf.iloc[-4].Vwap / vwapDf.iloc[-4].Close
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 5:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].High - vwapDf.iloc[-1].Close >
        #         vwapDf.iloc[-2].High - vwapDf.iloc[-2].Close and
        #         vwapDf.iloc[-2].High - vwapDf.iloc[-2].Close >
        #         vwapDf.iloc[-3].High - vwapDf.iloc[-3].Close and
        #         vwapDf.iloc[-3].High - vwapDf.iloc[-3].Close >
        #         vwapDf.iloc[-4].High - vwapDf.iloc[-4].Close and
        #         vwapDf.iloc[-4].High - vwapDf.iloc[-4].Close >
        #         vwapDf.iloc[-5].High - vwapDf.iloc[-5].Close
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].High - vwapDf.iloc[-1].Close >
                vwapDf.iloc[-2].High - vwapDf.iloc[-2].Close and
                vwapDf.iloc[-1].Volume < vwapDf.iloc[-2].Volume and
                vwapDf.iloc[-2].High - vwapDf.iloc[-2].Close >
                vwapDf.iloc[-3].High - vwapDf.iloc[-3].Close and
                vwapDf.iloc[-2].Volume < vwapDf.iloc[-3].Volume and
                vwapDf.iloc[-3].High - vwapDf.iloc[-3].Close >
                vwapDf.iloc[-4].High - vwapDf.iloc[-4].Close and
                vwapDf.iloc[-3].Volume < vwapDf.iloc[-4].Volume
            ): return False
        get_linenumber()

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close - vwapDf.iloc[-1].Low <
                vwapDf.iloc[-2].Close - vwapDf.iloc[-2].Low and
                vwapDf.iloc[-2].Close - vwapDf.iloc[-2].Low <
                vwapDf.iloc[-3].Close - vwapDf.iloc[-3].Low and
                vwapDf.iloc[-3].Close - vwapDf.iloc[-3].Low <
                vwapDf.iloc[-4].Close - vwapDf.iloc[-4].Low and
                vwapDf.iloc[-4].Close - vwapDf.iloc[-4].Low <
                vwapDf.iloc[-5].Close - vwapDf.iloc[-5].Low
            ): return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close - vwapDf.iloc[-1].Low >
                vwapDf.iloc[-2].Close - vwapDf.iloc[-2].Low and
                vwapDf.iloc[-1].Volume < vwapDf.iloc[-2].Volume and
                vwapDf.iloc[-2].Close - vwapDf.iloc[-2].Low >
                vwapDf.iloc[-3].Close - vwapDf.iloc[-3].Low and
                vwapDf.iloc[-2].Volume < vwapDf.iloc[-3].Volume
            ): return False
        get_linenumber()

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close < vwapDf.iloc[-5].Open and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-2].Low and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-3].Low
            ): return False
        get_linenumber()

        if len(vwapDf) > 31:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-11].Close and
                vwapDf.iloc[-12].Close < vwapDf.iloc[-21].Close and
                vwapDf.iloc[-22].Close < vwapDf.iloc[-31].Close
            ): return False
        get_linenumber()
        
        if len(vwapDf) > 45:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-15].Close and
                vwapDf.iloc[-16].Close < vwapDf.iloc[-30].Close and
                vwapDf.iloc[-31].Close < vwapDf.iloc[-45].Close
            ): return False
        get_linenumber()

        # # 3 month performance
        # if len(vwapDf) > 63:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-21].Close and
        #         vwapDf.iloc[-22].Close < vwapDf.iloc[-42].Close and
        #         vwapDf.iloc[-43].Close < vwapDf.iloc[-63].Close
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 75:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-25].Close and
                vwapDf.iloc[-26].Close < vwapDf.iloc[-50].Close and
                vwapDf.iloc[-51].Close < vwapDf.iloc[-75].Close
            ): return False
        get_linenumber()

        # # 6 month performance
        # if len(vwapDf) > 84:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-42].Close and
        #         vwapDf.iloc[-43].Close < vwapDf.iloc[-84].Close
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 110:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-55].Close and
        #         vwapDf.iloc[-51].Close < vwapDf.iloc[-110].Close
        #     ): return False
        # get_linenumber()

        # # 3 quarter performance
        # if len(vwapDf) > 189:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-63].Close and
        #         vwapDf.iloc[-64].Close < vwapDf.iloc[-126].Close and
        #         vwapDf.iloc[-127].Close < vwapDf.iloc[-189].Close
        #     ): return False
        # get_linenumber()

        # # 2 year quarter
        # if len(vwapDf) > 534:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-222].Close > vwapDf.iloc[-282].Close and
        #         vwapDf.iloc[-474].Close > vwapDf.iloc[-534].Close
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 2:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
        #         vwapDf.iloc[-1].Low > vwapDf.iloc[-2].High
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open and
                vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open and
                vwapDf.iloc[-1].Volume > vwapDf.iloc[-4].Volume and
                vwapDf.iloc[-1].Volume > vwapDf.iloc[-5].Volume and
                vwapDf.iloc[-1].Volume > vwapDf.iloc[-6].Volume and
                vwapDf.iloc[-2].Volume > vwapDf.iloc[-4].Volume and
                vwapDf.iloc[-2].Volume > vwapDf.iloc[-5].Volume and
                vwapDf.iloc[-2].Volume > vwapDf.iloc[-6].Volume and
                vwapDf.iloc[-3].Volume > vwapDf.iloc[-4].Volume and
                vwapDf.iloc[-3].Volume > vwapDf.iloc[-5].Volume and
                vwapDf.iloc[-3].Volume > vwapDf.iloc[-6].Volume
            ): return False
        get_linenumber()

        # if len(vwapDf) > 6:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open and
        #         vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
        #         vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open and
        #         vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open
        #     ): return False
        # get_linenumber()

        # Sell setup
        if len(vwapDf) > 8:
            if (
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open and
                vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open and
                vwapDf.iloc[-7].Close > vwapDf.iloc[-7].Open and
                vwapDf.iloc[-8].Close > vwapDf.iloc[-8].Open
            ): return False
        get_linenumber()

        # if len(vwapDf) > 6:
        #     if (
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
        #         vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
        #         vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open and
        #         vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 5:
        #     if (
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
        #         vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
        #         vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 3:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 6:
        #     if (
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
        #         vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
        #         vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
        #         vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
        #         vwapDf.iloc[-5].Close < vwapDf.iloc[-5].Open and
        #         vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open
        #     ): return False
        # get_linenumber()

        # if vwapDf.iloc[-1].Rsi > 77: return False
        # get_linenumber()

        # if vwapDf.iloc[-1].Rsi < 17: return False
        # get_linenumber()

        # if len(vwapDf) > 3:
        #     if (
        #         vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
        #         vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
        #         vwapDf.iloc[-2].High < vwapDf.iloc[-3].High and
        #         vwapDf.iloc[-2].Low > vwapDf.iloc[-3].Low
        #     ): return False
        # get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].High > vwapDf.iloc[-2].High and
                vwapDf.iloc[-1].Low < vwapDf.iloc[-2].Low and
                vwapDf.iloc[-2].High > vwapDf.iloc[-3].High and
                vwapDf.iloc[-2].Low < vwapDf.iloc[-3].Low
            ): return False
        get_linenumber()

        # if len(vwapDf) > 6:
        #     if (
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-3].Close and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-4].High and
        #         vwapDf.iloc[-1].Close < vwapDf.iloc[-5].High and
        #         vwapDf.iloc[-1].Close > vwapDf.iloc[-6].Close
        #     ): return False
        # get_linenumber()
        
    #    if len(vwapDf) > 2:
    #         closeArr = vwapDf.Close.values.tolist()
    #         stddev = np.std(closeArr)
    #         mean = np.mean(closeArr)
    #         upperBand = mean+(2 * stddev)

    #         if vwapDf.iloc[-1].High > upperBand:
    #             return False
    #     get_linenumber()

        # if len(vwapDf) > 10:
        #     closeArr = vwapDf.Close.values.tolist()
        #     SmaD1 = np.mean(closeArr[-10:])
        #     std = np.std(closeArr[-10:])
        #     if (
        #         closeArr[-1] < SmaD1 - std * 1.3
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 25:
        #     closeArr = vwapDf.Close.values.tolist()
        #     SmaD1 = np.mean(closeArr[-25:])
        #     std = np.std(closeArr[-25:])
        #     if (
        #         closeArr[-1] < SmaD1 + std * 1.2
        #     ): return False
        # get_linenumber()

        # if len(vwapDf) > 1:
        #     vwapDf = vwapDf.assign(stddev=vwapDf.Close.std())
        #     vwapDf = vwapDf.assign(sma=vwapDf.Close.mean())
        #     vwapDf = vwapDf.assign(upperBand=vwapDf.sma+(2 * vwapDf.stddev))

        #     if vwapDf.iloc[-1].High > vwapDf.iloc[-1].upperBand: return False
        # get_linenumber()

        if symbol in shortableSymList:
            df = vwapDf[['Close']]
            df = df.tail(4)
            maxDD = GetMaxDD(df)
            if maxDD < -0.26: return False
        get_linenumber()

        # # Industry
        # if symbol in shortableSymList or currency != 'USD':
        #     industryCheck = False
        #     curV1V2 = vwapDf.iloc[-1].Volume / vwapDf.iloc[-2].Volume
        #     industryLeader = curV1V2
        #     if symbol in industryDict:
        #         industry = industryDict[symbol]
        #         groupList = industryListGroup[industry]
        #         if len(groupList) > 1:
        #             if industry in industryLeaderBoard:
        #                 industryLeader = industryLeaderBoard[industry]
        #             else:
        #                 for sym2 in groupList:
        #                     print(sym2)
        #                     if sym2 in duplicate_list: continue
        #                     vwapDf = vwapDfDict[sym2]
        #                     mask = vwapDf.Date < str(backtestTime.date())
        #                     vwapDf = vwapDf.loc[mask]
        #                     if len(vwapDf) < 2: continue 
        #                     if vwapDf.iloc[-2].Volume < 1: continue 
        #                     v1v2 = vwapDf.iloc[-1].Volume / vwapDf.iloc[-2].Volume
        #                     if v1v2 > industryLeader:
        #                         industryLeader = v1v2
        #                 industryLeaderBoard[industry] = industryLeader
        #         else:
        #             industryCheck = True
                    
        #         if (
        #             curV1V2 > industryLeader * 0.45
        #         ):  industryCheck = True
        #         if not industryCheck: return False
        print(symbol,"passed")
        return True
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def checkInsider(symbol :str):
    insider = GetInsider(symbol)
    if len(insider>1):
        mask = insider.index < str(timeD.date())
        insider = insider.loc[mask]
        dollarAmount = insider['dollarAmount'].sum()
        if dollarAmount < -615634793.8467: return False
    return True

def checkScanner(shift, symbol):
    try:
        # Pre check bars before marketopen
        if IsTesting: print(symbol)
        if symbol in shortableSymList:
            if isBearish: return False
        try:
            if currency != 'JPY':
                stockInfo = yf.Ticker(symbol)
            else:
                stockInfo = yf.Ticker(symbol+'.T')
        except:
            return False
        optionChain=list(stockInfo.options)
        haveOptionChain = False
        if len(optionChain) > 0:
            haveOptionChain = True
        vwapDf = stockInfo.history(period="669d")
        if len(vwapDf) < 1: return False
        v = vwapDf.Volume.values
        h = vwapDf.High.values
        l = vwapDf.Low.values
        vwapDf['Vwap'] = Vwap(v,h,l)
        vwapDf['Rsi'] = Rsi(vwapDf.Close.values.tolist())

        mask = vwapDf.index < str(timeD.date())
        vwapDf = vwapDf.loc[mask]
        adr = 0.01
        if symbol in adrDict: adr = adrDict[symbol]
        else: adr = vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low
        if not checkHisBarsD1(vwapDf, symbol, adr): return False
        elif symbol not in stockList:
            shareholders = GetShareholders(symbol)
            if "insidersPercentHeld" in shareholders:
                insiderPercent = shareholders["insidersPercentHeld"]
                if insiderPercent > 2.00177: return False
                get_linenumber()
            # if "institutionsPercentHeld" in shareholders:
            #     percentHeld = shareholders["institutionsPercentHeld"]
            #     if percentHeld > 1.08396: return False
            #     get_linenumber()
                # if percentHeld < 0.0095999995: return False
                # get_linenumber()
            if symbol in shortableSymList:
                if "institutionsCount" in shareholders:
                    institutions = shareholders["institutionsCount"]
                    if institutions < 6: return False
                    get_linenumber()
            if "institutionsFloatPercentHeld" in shareholders:
                floatPercentHeld = shareholders["institutionsFloatPercentHeld"]
                if floatPercentHeld > 1.29213: return False
                get_linenumber()
                # if floatPercentHeld < 0.120699994: return False
                # get_linenumber()

            operatingCash = GetOperatingCash(symbol)
            if operatingCash < -3731653000: return False
            get_linenumber()

            if not checkInsider(symbol): return False
            get_linenumber()
            # tp = vwapDf.iloc[-1].High+adr*7.99631774937
            # tp = vwapDf.iloc[-1].High+adr*3.2274342400824505
            tp = vwapDf.iloc[-1].High+adr*0.032793916372638295
            tp = NormalizeFloat(tp,basicPoint)
            op = vwapDf.iloc[-1].Close
            vol = GetVol(op, adr)
            if vol < 1: return False
            stockList.append(
                {
                    's':symbol,
                    # 'close1': vwapDf.iloc[-1].Close,
                    'adr': adr,
                    'tp': tp,
                    'vol': vol,
                    'haveOptionChain': haveOptionChain
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

def getADR(currency :str):
    global adrDict
    adrDict = GetADR(currency)

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
    if IsTesting:
        for sym in winnerList:
            if sym not in scanner:
                scanner.append(sym)
    remove_duplicate()
    print('scanner',scanner)

def checkPreOpen():
    try:
        shift = 0
        if checkPreMarketTime(): shift = 1
        if currency == 'USD':
            if not checkMarketVol(): return False
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
        contract, endDateTime=usCheckPreChangeTime, durationStr='33960 S',
        barSizeSetting='1 min', whatToShow='BID', useRTH=False)
    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=3):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=usCheckPreChangeTime, durationStr='33960 S',
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
                if preMarketChange < 1.04376: continue
                print("preMaxHigh",preMaxHigh,"preMinLow",preMinLow)
                stock['preMaxHigh'] = preMaxHigh
                stock['preMinLow'] = preMinLow
                passedList.append(stock)
            
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    stockList = passedList

oppened_list = []
# positions = ib.positions()  # A list of positions, according to IB
# for position in positions:
#     contract = position.contract
#     oppened_list.append(contract.symbol)
def checkOpen():
    print(stockList)
    cost = 0
    # global stockList
    for stock in stockList:
        try:
            symbol = stock['s']
            if symbol in oppened_list: continue
            contract = Stock(symbol, 'SMART', currency)

            hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=endDateTimeD1, durationStr='2 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
            if len(hisBarsD1) < 2: continue
            if hisBarsD1[-1].open-hisBarsD1[-2].close < 0.16: 
                print(symbol,"hisBarsD1[-1].open-hisBarsD1[-2].close < 0.16",hisBarsD1[-1].open,hisBarsD1[-2].close)
                continue
            # if hisBarsD1[-1].open/hisBarsD1[-2].close < 1.111756168359943: 
            #     continue
            if hisBarsD1[-1].open/hisBarsD1[-2].close < 1.0055493895671478: 
                print(symbol,"hisBarsD1[-1].open/hisBarsD1[-2].close < 1.0055493895671478")
                continue
            # if hisBarsD1[-1].open/hisBarsD1[-2].close < 0.9146697837521918: 
            #     continue
            if IsTesting: print(symbol)

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
                    print("math.isnan(bid) or bid < 0.2")
                    continue
            spread = ask-bid
            # if hisBarsD1[-1].open < stock['close1'] * 1.02: continue
            preMaxHigh = 0.0
            preMinLow = 0.0
            if currency == 'USD':
                preMaxHigh = stock['preMaxHigh']
                preMinLow = stock['preMinLow']
                # if(ask-preMinLow)/(preMaxHigh-preMinLow) < 0.9803921568627455: continue
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))         

            if(ask>0 and bid>0):
                op = 0.0
                if currency == 'USD':
                    op = max(preMaxHigh,ask) + basicPoint * 1
                    # op = max(preMaxHigh,ask) + basicPoint * 19
                    # op = max(preMaxHigh,ask) + basicPoint * 11
                else:
                    op = ask + basicPoint * 1
                # if op < hisBarsD1[-2].close * 0.9479836353009935: continue
                op = NormalizeFloat(op, basicPoint)
                sl = GetSL(op, stock['adr'])
                if sl < hisBarsD1[-2].close or op - sl < basicPoint * 2: 
                    sl = hisBarsD1[-2].close
                sl = NormalizeFloat(sl, basicPoint)
                print("op",op,"sl",sl)
                # tp = stock['tp']
                # if (tp-op) / (op-sl) < 2.308823529411767:
                #     tp = op + (op-sl) * 13.588235294117656
                #     tp = NormalizeFloat(tp, basicPoint)
                # tp = op + (op-sl) * 1.0810810810810794
                # tp = op + (op-sl) * 1.02283105
                # tp = op + (op-sl) * 1.05
                tp = op + (op-sl) * 1.15
                tp = NormalizeFloat(tp, basicPoint)
                vol = stock['vol']
                spread = 0
                spread = ask-bid
                spreadPercent = 0.32
                if currency == 'JPY':
                    spreadPercent = 0.51
                # spreadFixed = 2.1
                spreadFixed = 9.75
                print(symbol,"spreadPercent",spread/(op - sl),spread)
                if spread < 9.75: spreadPercent = 97.5
                # if spread < 0.89: spreadPercent = 1.52
                # if spread < 0.48: spreadPercent = 1.55
                # if spread < 0.19: spreadPercent = 1.64
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

portfolioPath = './data/Portfolio.csv'
import os
if os.path.exists(portfolioPath):
    df = pd.read_csv(portfolioPath)
    keepOpenList = list(df.Symbol.values)

closeByMarketList = []
def closeAll(currency):
    positions = ib.positions()  # A list of positions, according to IB
    for position in positions:
        contract = position.contract
        if contract.strike > 0: continue
        symbol = contract.symbol
        if(contract.symbol in closeByMarketList):
            contract = Stock(symbol, 'SMART', currency)
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

def closeAllLimit(currency):
    global closeByMarketList
    positions = ib.positions()  # A list of positions, according to IB
    cancelAllOrders()
    for position in positions:
        contract = position.contract
        if contract.strike > 0: continue
        if contract.secType == 'CASH': continue
        symbol = contract.symbol
        if(symbol in keepOpenList): continue
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

import time
def main():
    global dayLightSaving
    dayLightSaving = True
    global IsTesting, currency, basicPoint, cash, jared
    IsTesting = False
    start = time.time()
    jared = []
    if IsTesting:
        getTestingTF('2022-09-12')
        jared = ['PNT']
        # getTestingTF('2022-09-07')
        # jared = ['QNRX']
        # getTestingTF('2022-09-01')
        # jared = ['SHPH','JZ']
        # getTestingTF('2022-08-30')
        # jared = ['INAB']
        # getTestingTF('2022-08-25')
        # jared = ['DRUG']
        # getTestingTF('2022-08-23')
        # jared = ['INDO','ENVX']
        # getTestingTF('2022-08-18')
        # jared = ['DRUG']
        # getTestingTF('2022-08-17')
        # jared = ['BWV']
        # getTestingTF('2022-08-15')
        # jared = ['MEGL']
        # getTestingTF('2022-08-12')
        # jared = ['VEEE']
        # getTestingTF('2022-08-04')
        # jared = ['NVIV','COIN']
        # getTestingTF('2022-08-03')
        # jared = ['QNRX']
        # getTestingTF('2022-08-02')
        # jared = ['APDN']
        # getTestingTF('2022-07-27')
        # jared = ['PGY']
        # getTestingTF('2022-07-27')
        # jared = ['PGY']
        # getTestingTF('2022-07-26')
        # jared = ['PGY']
        # getTestingTF('2022-07-20')
        # jared = ['TBLT']
        # getTestingTF('2022-07-19')
        # jared = ['SIDU']
        # getTestingTF('2022-07-18')
        # jared = ['ILAG']
        # getTestingTF('2022-07-15')
        # jared = ['USEA']
        # getTestingTF('2022-06-28')
        # jared = ['AGRX']
        # getTestingTF('2022-06-06')
        # jared = ['PEGY']
        # getTestingTF('2022-05-26')
        # jared = ['NKE']
        # getTestingTF('2022-05-23')
        # jared = ['AAPL']
        # getTestingTF('2022-05-17')
        # jared = ['PPSI']
        # getTestingTF('2022-05-16')
        # jared = ['AMC']
        # getTestingTF('2022-05-13')
        # jared = ['GM']
        # getTestingTF('2022-05-11')
        # jared = ['IBM','BHC']
        # getTestingTF('2022-05-10')
        # jared = ['HAL','INDO']
        # getTestingTF('2022-05-10')
        # jared = ['CYN']
        # getTestingTF('2022-05-04')
        # jared = ['RVSN']
        # getTestingTF('2022-04-26')
        # jared = ['NUTX']
        # getTestingTF('2022-04-25')
        # jared = ['NKTX']
        # getTestingTF('2022-04-21')
        # jared = ['UAL']
        # getTestingTF('2022-04-20')
        # jared = ['LLAP']
        # getTestingTF('2022-04-19')
        # jared = ['STSS']
        # getTestingTF('2022-04-12')
        # jared = ['HAL']
        # getTestingTF('2022-04-06')
        # jared = ['TLRY']
        # getTestingTF('2022-04-11')
        # jared = ['VERU','IVDA']
        # getTestingTF('2022-04-05')
        # jared = ['SST']
        # getTestingTF('2022-04-04')
        # jared = ['LLL']
        # getTestingTF('2022-03-29')
        # jared = ['DRCT']
        # getTestingTF('2022-03-28')
        # jared = ['DRTS']
        # getTestingTF('2022-03-25')
        # jared = ['ALLG']
        # getTestingTF('2022-03-22')
        # jared = ['LLL']
        # getTestingTF('2022-03-21')
        # jared = ['NRSN','BBLG','EIGR']
        # getTestingTF('2022-03-11')
        # jared = ['MGLD']
        # getTestingTF('2022-03-07')
        # jared = ['MXC']
        # getTestingTF('2022-03-04')
        # jared = ['INDO']
        # getTestingTF('2022-03-02')
        # jared = ['FL']
        # getTestingTF('2022-02-28')
        # jared = ['LFLY']
        # getTestingTF('2022-02-17')
        # jared = ['ISPO','BRCC','ANGH']
        # getTestingTF('2022-01-05')
        # jared = ['ZEV']
        # getTestingTF('2021-12-31')
        # jared = ['NTRB']
        # getTestingTF('2021-11-17')
        # jared = ['OPK','EYPT']
        # getTestingTF('2021-11-12')
        # jared = ['MRAM']
        # getTestingTF('2021-11-11')
        # jared = ['BBBY','PPSI']

        # 2021-11-07 day light saving 

        # getTestingTF('2021-11-05')
        # jared = ['ALZN']
        # getTestingTF('2021-11-03')
        # jared = ['PTPI']
        # # # getTestingTF('2021-10-25')
        # # # jared = ['BKKT']
        # getTestingTF('2021-10-26')
        # jared = ['LIDR']
        # getTestingTF('2021-10-22')
        # jared = ['PHUN']
        # getTestingTF('2021-10-21')
        # jared = ['DWAC']
        # getTestingTF('2021-09-09')
        # jared = ['RKLB']
        # getTestingTF('2021-09-01')
        # jared = ['FCUV','BBIG','EVAX']
        # getTestingTF('2021-08-27')
        # jared = ['BBIG','ATER']
        # getTestingTF('2021-08-26')
        # jared = ['VRPX']
        # getTestingTF('2021-08-24')
        # jared = ['TKAT','DATS']
        # getTestingTF('2021-08-19')
        # jared = ['GOVX']
        # getTestingTF('2021-08-18')
        # jared = ['PMCB']
        # getTestingTF('2021-08-17')
        # jared = ['VRPX']
        # getTestingTF('2021-08-16')
        # jared = ['NAOV']
        # getTestingTF('2021-08-10')
        # jared = ['FULC','ZEV']
        # getTestingTF('2021-07-26')
        # jared = ['SGRP']
        # getTestingTF('2021-07-21')
        # jared = ['NURO','CEMI']
        # getTestingTF('2021-07-13')
        # jared = ['AHPI']
        # getTestingTF('2021-07-09')
        # jared = ['CARV']
        # getTestingTF('2021-07-07')
        # jared = ['BON','VRPX']
        # getTestingTF('2021-06-29')
        # jared = ['CERE','BSQR']
        # getTestingTF('2021-06-28')
        # jared = ['ADIL']
        # getTestingTF('2021-06-24')
        # jared = ['DBGI']
        # getTestingTF('2021-06-10')
        # jared = ['GLTO','MEDS']
        # getTestingTF('2021-06-08')
        # jared = ['CLOV']
        # getTestingTF('2021-06-04')
        # jared = ['LEDS']
        # getTestingTF('2021-06-02')
        # jared = ['AMC','UONE']
        # getTestingTF('2021-05-27')
        # jared = ['GME']
        # getTestingTF('2021-05-24')
        # jared = ['SCPS']
        # getTestingTF('2021-05-21')
        # jared = ['ANVS']
        # getTestingTF('2021-05-12')
        # jared = ['IHT']
        # getTestingTF('2021-05-10')
        # jared = ['PTIX']
        # getTestingTF('2021-05-07')
        # jared = ['RHE']
        # getTestingTF('2021-05-06')
        # jared = ['LEDS','RHE']
        # getTestingTF('2021-05-05')
        # jared = ['RHE']
        # getTestingTF('2021-05-03')
        # jared = ['RHE']
        # getTestingTF('2021-04-30')
        # jared = ['BTX']
        # getTestingTF('2021-04-27')
        # jared = ['TIRX']
        # getTestingTF('2021-04-23')
        # jared = ['TKAT','BTX']
        # getTestingTF('2021-04-22')
        # jared = ['CVM','TKAT','BTX']
        # getTestingTF('2021-04-16')
        # jared = ['CVM','TKAT','BTX']
        # getTestingTF('2021-04-15')
        # jared = ['WHLM']
        # getTestingTF('2021-04-05')
        # jared = ['ACY']
        # getTestingTF('2021-03-31')
        # jared = ['WAFU']
        # getTestingTF('2021-03-30')
        # jared = ['VTSI']
        # getTestingTF('2021-03-26')
        # jared = ['WAFU','WKEY']
        # getTestingTF('2021-02-19')
        # jared = ['VCNX']
        # getTestingTF('2020-12-09')
        # jared = ['GLSI','XBIO','DYAI','BNTC']
        # getTestingTF('2020-12-07')
        # jared = ['GTEC','BVXV']
        # getTestingTF('2020-11-16')
        # jared = ['ATHE']
        # getTestingTF('2020-10-29')
        # jared = ['POLA']
        # getTestingTF('2020-10-06')
        # jared = ['PPSI','CHCI']
        # getTestingTF('2020-09-24')
        # jared = ['SUNW','POLA']
        # getTestingTF('2020-09-21')
        # jared = ['CLSK']
        # getTestingTF('2020-08-28')
        # jared = ['VVPR']
        # getTestingTF('2020-08-27')
        # jared = ['PED']
        # getTestingTF('2020-08-25')
        # jared = ['VIVE']
        # getTestingTF('2020-08-11')
        # jared = ['JAN']
        # getTestingTF('2020-08-10')
        # jared = ['CLSK']
        # getTestingTF('2020-08-07')
        # jared = ['OPGN','CARV']
        # getTestingTF('2020-08-06')
        # jared = ['KODK']
        # getTestingTF('2020-07-31')
        # jared = ['SONN']
        # getTestingTF('2020-07-30')
        # jared = ['KODK']
        # getTestingTF('2020-07-27')
        # jared = ['WHLM','MNOV']
        # getTestingTF('2020-07-22')
        # jared = ['USEG']
        # getTestingTF('2020-07-20')
        # jared = ['IMRN','CAPR','LGHL']
        # getTestingTF('2020-07-15')
        # jared = ['GENE']
        # getTestingTF('2020-07-13')
        # jared = ['WIMI','EQ']
        # getTestingTF('2020-07-08')
        # jared = ['AIHS']
        # getTestingTF('2020-07-06')
        # jared = ['AYRO']
        # getTestingTF('2020-07-02')
        # jared = ['JOB']
        # getTestingTF('2020-06-29')
        # jared = ['WKHS','PDSB']
        # getTestingTF('2020-06-25')
        # jared = ['EKSO','NNVC']
        # getTestingTF('2020-06-24')
        # jared = ['INO']
        # getTestingTF('2020-06-23')
        # jared = ['FFHL','UONE']
        # getTestingTF('2020-06-19')
        # jared = ['UONE','BYFC']
        # getTestingTF('2020-06-18')
        # jared = ['CARV']
        # getTestingTF('2020-06-17')
        # jared = ['CARV','COHN','LMFA']
        # getTestingTF('2020-06-16')
        # jared = ['UONE']
        # getTestingTF('2020-06-11')
        # jared = ['WAFU','FFHL']
        # getTestingTF('2020-06-10')
        # jared = ['JFIN','AVCT','CRIS']
        # getTestingTF('2020-06-09')
        # jared = ['IMRN','DGLY','MIST']
        # getTestingTF('2020-06-08')
        # jared = ['ADIL','MXC']
        # getTestingTF('2020-06-04')
        # jared = ['CIDM','GNUS']
        # getTestingTF('2020-06-03')
        # jared = ['GNUS']
        # getTestingTF('2020-05-29')
        # jared = ['SNOA']
        # getTestingTF('2020-05-28')
        # jared = ['ABIO','FTSI','GMBL']
        # getTestingTF('2020-05-27')
        # jared = ['MRSN']
        # getTestingTF('2020-05-19')
        # jared = ['PIXY','NNDM','ITRM','CYCC']
        # getTestingTF('2020-05-18')
        # jared = ['ACB']
        # getTestingTF('2020-05-15')
        # jared = ['SRNE','ACB']
        # getTestingTF('2020-04-14')
        # jared = ['SONN']

        #20200319
        # getTestingTF('2020-03-10')
        # jared = ['SFET']
        # getTestingTF('2020-02-21')
        # jared = ['TSRI']
        # getTestingTF('2020-02-18')
        # jared = ['BLPH']
        # getTestingTF('2020-02-10')
        # jared = ['PLAG']
        # getTestingTF('2020-02-07')
        # jared = ['YTEN']
        # getTestingTF('2020-02-05')
        # jared = ['MYO']
    currency = 'USD'
    # currency = 'JPY'
    if currency == 'JPY':
        basicPoint = 1
    update_total_balance()
    update_balance()
    if IsTesting:
        cash = total_cash
        getWinnerList(currency)
    else:
        getPerformanceSymList(currency)
    # if currency == 'USD':
    #     if not IsTesting:
    #         getDRSymList()
    #     getMarketCondition()
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
            #     get_scanner()
            #     getADR(currency)
            #     getMarketCondition()
            #     checkPreOpen()
            #     checkForJared()
            #     print(stockList)
            if dayLightSaving:
                if(hour == 13 and minute == 26 and sec == 0):
                    checkPreChange()

                if(hour == 13 and minute == 30 and sec == 0):
                    checkOpen()

                # EOD Limit
                if(hour == 13 and minute == 55 and sec == 0):
                # if(hour == 16 and minute == 16 and sec == 56):
                    closeAllLimit(currency)
                    
                # EOD
                if(hour == 13 and minute == 56 and sec == 0):
                # if(hour == 16 and minute == 18 and sec == 0):
                    closeAll(currency)

                # EOD Cancel
                # if(hour == 14 and minute == 10 and sec == 0):
                # if(hour == 14 and minute == 46 and sec == 0):
                # if(hour == 17 and minute == 15 and sec == 0):
                if(hour == 19 and minute == 18 and sec == 0):
                    cancelUntriggered()

                # Move SL to BE + spread + commision+0.01 14:30

                # EOD Limit
                if(hour == 17 and minute == 46 and sec == 0):
                # if(hour == 16 and minute == 16 and sec == 56):
                    closeAllLimit(currency)
                    
                # EOD
                if(hour == 17 and minute == 47 and sec == 0):
                # if(hour == 16 and minute == 18 and sec == 0):
                    closeAll(currency)

                # EOD Limit
                if(hour == 19 and minute == 25 and sec == 0):
                    closeAllLimit(currency)
                    
                # EOD
                if(hour == 19 and minute == 26 and sec == 0):
                    closeAll(currency)
            else:
                if(hour == 14 and minute == 26 and sec == 0):
                    checkPreChange()

                if(hour == 14 and minute == 30 and sec == 0):
                    checkOpen()

                # EOD Limit
                if(hour == 14 and minute == 55 and sec == 0):
                # if(hour == 17 and minute == 16 and sec == 56):
                    closeAllLimit(currency)
                    
                # EOD
                if(hour == 14 and minute == 56 and sec == 0):
                # if(hour == 17 and minute == 18 and sec == 0):
                    closeAll(currency)

                # EOD Cancel
                # if(hour == 15 and minute == 10 and sec == 0):
                # if(hour == 15 and minute == 46 and sec == 0):
                # if(hour == 18 and minute == 15 and sec == 0):
                if(hour == 20 and minute == 18 and sec == 0):
                    cancelUntriggered()

                # Move SL to BE + spread + commision+0.01 15:30

                # EOD Limit
                if(hour == 18 and minute == 46 and sec == 0):
                # if(hour == 17 and minute == 16 and sec == 56):
                    closeAllLimit(currency)
                    
                # EOD
                if(hour == 18 and minute == 47 and sec == 0):
                # if(hour == 17 and minute == 18 and sec == 0):
                    closeAll(currency)

                # EOD Limit
                if(hour == 20 and minute == 25 and sec == 0):
                    closeAllLimit(currency)
                    
                # EOD
                if(hour == 20 and minute == 26 and sec == 0):
                    closeAll(currency)
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
                closeAllLimit(currency)
                
            # EOD
            if(hour == 2 and minute == 12 and sec == 0):
                closeAll(currency)

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