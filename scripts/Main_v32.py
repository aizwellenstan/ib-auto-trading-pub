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
from modules.aiztradingview import GetPerformance,GetADR,GetDR,GetREIT,GetPreVolume,GetRvol,GetPerformanceJP,GetDailyWinner,GetDailyWinnerJP
from modules.shareholders import GetShareholders, GetZScore, GetOperatingCash
from modules.vwap import Vwap
from modules.rsi import Rsi
from modules.technicalAnalysis import PlotLines
from modules.slope import GetSlopeUpper, GetSlopeLower, GetSlopeUpperNew, GetSlopeLowerNew
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
'OPEN','RPAI','POLY','CMPX','TCS','EYEG','MCLD','AVGR',
'PLTR','SPRT',
'9318']
performanceSymList = []
drSymList = []
reitSymList = []
winnerList = []
scanner = []
adrDict = []
# ---List section---
stockList = [] # List for open
# ---end list section---

dayLightSaving = True
timeD = dt.strptime(str(ib.reqCurrentTime().date()), '%Y-%m-%d')
usCheckPreChangeTime = timeD + timedelta(hours = 22) + timedelta(minutes = 27)
usMarketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
endDateTimeD1 = ''
endDateTimePreScanner=''
endDateTimeAskBid = ''

contractQQQ = Stock('QQQ', 'SMART', 'USD')
contractSPY = Stock('SPY', 'SMART', 'USD')
contractVTI = Stock('VTI', 'SMART', 'USD')
contractDIA = Stock('DIA', 'SMART', 'USD')
contractIWM = Stock('IWM', 'SMART', 'USD')
contractHYG = Stock('HYG', 'SMART', 'USD')

hisBarsQQQD1 = []
hisBarsSPYD1 = []
hisBarsVTID1 = []
hisBarsDIAD1 = []
hisBarsIWMD1 = []

isBearish = False

IsTesting = False
def get_linenumber():
    if IsTesting:
        cf = currentframe()
        print(cf.f_back.f_lineno)
        
def getTestingTF(date :str):
    global timeD, usCheckPreChangeTime, usMarketOpenTime, endDateTimeD1, endDateTimePreScanner, endDateTimeAskBid
    timeD = dt.strptime(str(date), '%Y-%m-%d')
    usCheckPreChangeTime = timeD + timedelta(hours = 23) + timedelta(minutes = 27)
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
    global hisBarsQQQD1, hisBarsSPYD1, hisBarsVTID1, hisBarsDIAD1, hisBarsIWMD1, isBearish
    hisBarsQQQD1 = ib.reqHistoricalData(
    contractQQQ, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsSPYD1 = ib.reqHistoricalData(
    contractSPY, endDateTime=endDateTimeD1, durationStr='5 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsVTID1 = ib.reqHistoricalData(
    contractVTI, endDateTime=endDateTimeD1, durationStr='365 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsDIAD1 = ib.reqHistoricalData(
    contractDIA, endDateTime=endDateTimeD1, durationStr='365 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsIWMD1 = ib.reqHistoricalData(
    contractIWM, endDateTime=endDateTimeD1, durationStr='365 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

    hisBarsQQQD1 = hisBarsQQQD1[::-1]
    hisBarsSPYD1 = hisBarsSPYD1[::-1]
    hisBarsVTID1 = hisBarsVTID1[::-1]
    hisBarsDIAD1 = hisBarsDIAD1[::-1]
    hisBarsIWMD1 = hisBarsIWMD1[::-1]

    upper, lower = PlotLines(hisBarsDIAD1)
    if lower < -0.61: 
        isBearish = True
        return 0
    get_linenumber()

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
    get_linenumber()

    stockInfo = yf.Ticker("IAU")
    iauDf = stockInfo.history(period="365d")
    mask = iauDf.index < str(timeD.date())
    iauDf = iauDf.loc[mask]
    df = iauDf[['Open','High','Low','Close']]
    npArr = df.to_numpy()
    upper = GetSlopeUpper(npArr)
    if upper > 0.12: 
        isBearish = True
        return 0
    get_linenumber()

def GetDf(symbol :str):
    stockInfo = yf.Ticker(symbol)
    df = stockInfo.history(period="max")
    mask = df.index < str(timeD.date())
    df = df.loc[mask]

    return df

def checkMarketVol():
    qqqdf = GetDf('QQQ')
    spydf = GetDf('SPY')
    iwmdf = GetDf('IWM')
    vtidf = GetDf('VTI')
    diadf = GetDf('DIA')
    uvxydf = GetDf('UVXY')
    sqqqdf = GetDf('SQQQ')
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
    veadf = GetDf('VEA')

    if (len(spydf) > 200 and len(vtidf) > 200):
        closeArrVTI = vtidf.Close.values.tolist()
        SmaD1VTI = np.mean(closeArrVTI[-201:-1])
        closeArrDIA = diadf.Close.values.tolist()
        SmaD1DIA = np.mean(closeArrDIA[-201:-1])
        if (
            closeArrVTI[-1] < SmaD1VTI and
            closeArrDIA[-1] < SmaD1DIA
        ): 
            print('vti dia < sma200')
            return False

    if uvxydf.iloc[-1].Volume < iwmdf.iloc[-1].Volume:
        print('uvxyVol < iwmVol')
        return False
    if (
        qqqdf.iloc[-1].Volume > qqqdf.iloc[-2].Volume and
        qqqdf.iloc[-2].Volume > qqqdf.iloc[-3].Volume
    ):
        print('increasing vol qqq')
        return False
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

def checkHisBarsD1(vwapDf, symbol):
    try:
        op = vwapDf.iloc[-1].Close
        print(symbol,op)
        if not checkOPLimit(op): return False

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low < 0.01 or
                vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low < 0.01 or
                vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low < 0.01 or
                vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low < 0.01
            ): return False

        if len(vwapDf) > 40:
            if (
                abs(vwapDf.iloc[-1].Close - vwapDf.iloc[-20].Open) < 0.01 or
                abs(vwapDf.iloc[-21].Close - vwapDf.iloc[-40].Open) < 0.01
            ): return False

        # 3 bar up
        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open
            ): return False
        get_linenumber()

        # 3bar play
        if len(vwapDf) > 3:
            if not (
                vwapDf.iloc[-2].Open - vwapDf.iloc[-2].Close >
                vwapDf.iloc[-3].High - vwapDf.iloc[-2].Low
            ):
                if (
                    vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                    vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
                    vwapDf.iloc[-1].Low > vwapDf.iloc[-1].Vwap and
                    vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                    vwapDf.iloc[-2].High - vwapDf.iloc[-2].Low >
                    abs(vwapDf.iloc[-3].Close - vwapDf.iloc[-3].Open) and
                    vwapDf.iloc[-2].High - vwapDf.iloc[-2].Low >
                    abs(vwapDf.iloc[-4].Close - vwapDf.iloc[-4].Open)
                ): return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
                vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
                vwapDf.iloc[-1].High < vwapDf.iloc[-3].High and
                vwapDf.iloc[-1].Low > vwapDf.iloc[-3].Low
            ): return False
        get_linenumber()

        if len(vwapDf) > 2:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
                vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Open
            ): return False
        get_linenumber()

        if len(vwapDf) > 100:
            closeArr = vwapDf.Close.values.tolist()
            closeArr = closeArr[-100:]
            stddev = np.std(closeArr)
            mean = np.mean(closeArr)
            upperBand = mean+(2.4 * stddev)

            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Low > upperBand
            ): return False
        get_linenumber()

        if (
            vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
            vwapDf.iloc[-1].Rsi > 89
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

        # 4 gap down
        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Open < vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].Open < vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].Open < vwapDf.iloc[-4].Close
            ): return False
        get_linenumber()

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Vwap / vwapDf.iloc[-1].Close <
                vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close <
                vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close <
                vwapDf.iloc[-4].Vwap / vwapDf.iloc[-4].Close
            ): return False
        get_linenumber()

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

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close < vwapDf.iloc[-5].Open
            ): return False
        get_linenumber()

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

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
                vwapDf.iloc[-1].Open > vwapDf.iloc[-2].Close and
                vwapDf.iloc[-1].Close > vwapDf.iloc[-2].High
            ): return False
        get_linenumber()

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low > 0 and
                vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low > 0 and
                vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low > 0 and
                vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low > 0 and
                vwapDf.iloc[-5].High-vwapDf.iloc[-5].Low > 0
            ):
                if (
                    vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                    abs(vwapDf.iloc[-1].Close-vwapDf.iloc[-1].Open) /
                    (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low) < 0.45 and
                    abs(vwapDf.iloc[-2].Close-vwapDf.iloc[-2].Open) /
                    (vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low) < 0.45 and
                    abs(vwapDf.iloc[-3].Close-vwapDf.iloc[-3].Open) /
                    (vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low) < 0.45 and
                    abs(vwapDf.iloc[-4].Close-vwapDf.iloc[-4].Open) /
                    (vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low) < 0.45
                ): return False
        get_linenumber()

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low > 0 and
                vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low > 0 and
                vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low > 0 and
                vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low > 0 and
                vwapDf.iloc[-5].High-vwapDf.iloc[-5].Low > 0
            ):
                if (
                    vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                    abs(vwapDf.iloc[-1].Close-vwapDf.iloc[-1].Open) /
                    (vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low) < 0.5 and
                    abs(vwapDf.iloc[-2].Close-vwapDf.iloc[-2].Open) /
                    (vwapDf.iloc[-2].High-vwapDf.iloc[-2].Low) < 0.5 and
                    abs(vwapDf.iloc[-3].Close-vwapDf.iloc[-3].Open) /
                    (vwapDf.iloc[-3].High-vwapDf.iloc[-3].Low) < 0.5 and
                    abs(vwapDf.iloc[-4].Close-vwapDf.iloc[-4].Open) /
                    (vwapDf.iloc[-4].High-vwapDf.iloc[-4].Low) < 0.5 and
                    abs(vwapDf.iloc[-5].Close-vwapDf.iloc[-5].Open) /
                    (vwapDf.iloc[-5].High-vwapDf.iloc[-5].Low) < 0.5
                ): return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Vwap and
                vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Vwap
            ): return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Vwap and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Vwap
            ): return False
        get_linenumber()

        if len(vwapDf) > 4:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Vwap / vwapDf.iloc[-1].Close <
                vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].Vwap / vwapDf.iloc[-2].Close >
                vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].Vwap / vwapDf.iloc[-3].Close <
                vwapDf.iloc[-4].Vwap / vwapDf.iloc[-4].Close
            ): return False
        get_linenumber()

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].High - vwapDf.iloc[-1].Close >
                vwapDf.iloc[-2].High - vwapDf.iloc[-2].Close and
                vwapDf.iloc[-2].High - vwapDf.iloc[-2].Close >
                vwapDf.iloc[-3].High - vwapDf.iloc[-3].Close and
                vwapDf.iloc[-3].High - vwapDf.iloc[-3].Close >
                vwapDf.iloc[-4].High - vwapDf.iloc[-4].Close and
                vwapDf.iloc[-4].High - vwapDf.iloc[-4].Close >
                vwapDf.iloc[-5].High - vwapDf.iloc[-5].Close
            ): return False
        get_linenumber()

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

        # 3 month performance
        if len(vwapDf) > 63:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-21].Close and
                vwapDf.iloc[-22].Close < vwapDf.iloc[-42].Close and
                vwapDf.iloc[-43].Close < vwapDf.iloc[-63].Close
            ): return False
        get_linenumber()

        if len(vwapDf) > 75:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-25].Close and
                vwapDf.iloc[-26].Close < vwapDf.iloc[-50].Close and
                vwapDf.iloc[-51].Close < vwapDf.iloc[-75].Close
            ): return False
        get_linenumber()

        # 6 month performance
        if len(vwapDf) > 84:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-42].Close and
                vwapDf.iloc[-43].Close < vwapDf.iloc[-84].Close
            ): return False
        get_linenumber()

        if len(vwapDf) > 110:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-55].Close and
                vwapDf.iloc[-51].Close < vwapDf.iloc[-110].Close
            ): return False
        get_linenumber()

        # 3 quarter performance
        if len(vwapDf) > 189:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-63].Close and
                vwapDf.iloc[-64].Close < vwapDf.iloc[-126].Close and
                vwapDf.iloc[-127].Close < vwapDf.iloc[-189].Close
            ): return False
        get_linenumber()

        # 2 year quarter
        if len(vwapDf) > 534:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-222].Close > vwapDf.iloc[-282].Close and
                vwapDf.iloc[-474].Close > vwapDf.iloc[-534].Close
            ): return False
        get_linenumber()

        if len(vwapDf) > 2:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Vwap and
                vwapDf.iloc[-1].Low > vwapDf.iloc[-2].High
            ): return False
        get_linenumber()

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

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close > vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open and
                vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open
            ): return False
        get_linenumber()

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

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close > vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open and
                vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open
            ): return False
        get_linenumber()

        if len(vwapDf) > 5:
            if (
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close > vwapDf.iloc[-5].Open
            ): return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close > vwapDf.iloc[-3].Open
            ): return False
        get_linenumber()

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close < vwapDf.iloc[-1].Open and
                vwapDf.iloc[-2].Close < vwapDf.iloc[-2].Open and
                vwapDf.iloc[-3].Close < vwapDf.iloc[-3].Open and
                vwapDf.iloc[-4].Close < vwapDf.iloc[-4].Open and
                vwapDf.iloc[-5].Close < vwapDf.iloc[-5].Open and
                vwapDf.iloc[-6].Close > vwapDf.iloc[-6].Open
            ): return False
        get_linenumber()

        if vwapDf.iloc[-1].Rsi > 77: return False
        get_linenumber()

        if vwapDf.iloc[-1].Rsi < 17: return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].High < vwapDf.iloc[-2].High and
                vwapDf.iloc[-1].Low > vwapDf.iloc[-2].Low and
                vwapDf.iloc[-2].High < vwapDf.iloc[-3].High and
                vwapDf.iloc[-2].Low > vwapDf.iloc[-3].Low
            ): return False
        get_linenumber()

        if len(vwapDf) > 3:
            if (
                vwapDf.iloc[-1].High > vwapDf.iloc[-2].High and
                vwapDf.iloc[-1].Low < vwapDf.iloc[-2].Low and
                vwapDf.iloc[-2].High > vwapDf.iloc[-3].High and
                vwapDf.iloc[-2].Low < vwapDf.iloc[-3].Low
            ): return False
        get_linenumber()

        if len(vwapDf) > 6:
            if (
                vwapDf.iloc[-1].Close > vwapDf.iloc[-3].Close and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-4].High and
                vwapDf.iloc[-1].Close < vwapDf.iloc[-5].High and
                vwapDf.iloc[-1].Close > vwapDf.iloc[-6].Close
            ): return False
        get_linenumber()
        
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

            df = vwapDf[['Close']]
            df = df.tail(6)
            maxDD = GetMaxDD(df)
            if maxDD < -0.14: return False
            get_linenumber()
            
            df = vwapDf
            df = df[['Open','High','Low','Close']]
            npArr = df.to_numpy()
            upper = GetSlopeUpper(npArr)
            if upper < 0: return False
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
        vwapDf = stockInfo.history(period="max")
        if len(vwapDf) < 1: return False
        v = vwapDf.Volume.values
        h = vwapDf.High.values
        l = vwapDf.Low.values
        vwapDf['Vwap'] = Vwap(v,h,l)
        vwapDf['Rsi'] = Rsi(vwapDf.Close.values.tolist())

        mask = vwapDf.index < str(timeD.date())
        vwapDf = vwapDf.loc[mask]
        if not checkHisBarsD1(vwapDf,symbol):
            return False
        elif symbol not in stockList:
            shareholders = GetShareholders(symbol)
            insiderPercent = shareholders["insidersPercentHeld"]
            institutions = shareholders["institutionsCount"]
            percentHeld = shareholders["institutionsPercentHeld"]
            floatPercentHeld = shareholders["institutionsFloatPercentHeld"]
            
            if insiderPercent > 0.96936995: return False
            get_linenumber()
            # if institutions < 7: return False
            # get_linenumber()
            # if floatPercentHeld < 0.120699994: return False
            # get_linenumber()
            if floatPercentHeld > 1.0915: return False
            get_linenumber()
            # if percentHeld < 0.0095999995: return False
            # get_linenumber()
            if percentHeld > 1.08101: return False
            get_linenumber()

            operatingCash = GetOperatingCash(symbol)
            if operatingCash < -3731653000: return False
            get_linenumber()
            if symbol in adrDict:
                adr = adrDict[symbol]
            else:
                adr = vwapDf.iloc[-1].High-vwapDf.iloc[-1].Low
            tp = vwapDf.iloc[-1].High+adr*7.99631774937
            tp = NormalizeFloat(tp,basicPoint)
            stockList.append(
                {
                    's':symbol,
                    # 'close1': vwapDf.iloc[-1].Close,
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
        contract, endDateTime=usCheckPreChangeTime, durationStr='5160 S',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=4):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=usCheckPreChangeTime, durationStr='5160 S',
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

def checkPreVolume():
    rvolSymList = GetPreVolume()
    global stockList
    passedList = []
    for stock in stockList:
        try:
            symbol = stock['s']
            if symbol not in rvolSymList: continue
            passedList.append(stock)
        except Exception as e:
            print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
            print(e)
    stockList = passedList

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
    cost = 0
    if currency == 'USD':
        rvolSymList = GetRvol()
        hisBarsSPYD1 = ib.reqHistoricalData(
            contractSPY, endDateTime=endDateTimeD1, durationStr='2 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        hisBarsVTID1 = ib.reqHistoricalData(
            contractVTI, endDateTime=endDateTimeD1, durationStr='2 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        hisBarsIWMD1 = ib.reqHistoricalData(
            contractIWM, endDateTime=endDateTimeD1, durationStr='2 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        hisBarsHYGD1 = ib.reqHistoricalData(
            contractHYG, endDateTime=endDateTimeD1, durationStr='2 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        if (
            hisBarsSPYD1[-1].open < hisBarsSPYD1[-2].high and
            hisBarsVTID1[-1].open < hisBarsVTID1[-2].high and
            hisBarsIWMD1[-1].open < hisBarsIWMD1[-2].high and
            hisBarsHYGD1[-1].open > hisBarsHYGD1[-2].low
        ):
            print('Market Gap Down')
            return False
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
                    continue
            spread = ask-bid
            # if hisBarsD1[-1].open < stock['close1'] * 1.02: continue
            if currency == 'USD':
                preMaxHigh = stock['preMaxHigh']
                preMinLow = stock['preMinLow']
            print("symbol ",symbol," bid " +str(bid)," ask ",str(ask))

            if(ask>0 and bid>0):
                if currency == 'USD':
                    op = NormalizeFloat(max(preMaxHigh,bid) + 0.01 * 16, basicPoint)
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
                    if spread < 0.48: spreadPercent = 1.55
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
    if "NTRB" not in performanceSymList:
        print("WORST SCANNER IN THIS CENTURY")
    else:
        print("よくやった！")

import time
def main():
    global dayLightSaving
    dayLightSaving = True
    global IsTesting, currency, basicPoint, cash, jared
    IsTesting = False
    start = time.time()
    if IsTesting:
        getTestingTF('2022-01-12')
        # getTestingTF('2021-12-31')
        # jared = ['NTRB']
        # getTestingTF('2021-10-21')
        # jared = ['DWAC']
        # getTestingTF('2021-10-22')
        # jared = ['PHUN']
        # # # getTestingTF('2021-10-25')
        # # # jared = ['BKKT']
        # getTestingTF('2021-11-03')
        # jared = ['PTPI']
        # getTestingTF('2021-11-05')
        # jared = ['ALZN']
    currency = 'USD'
    # currency = 'JPY'
    if currency == 'JPY':
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
    get_scanner()
    getADR(currency)
    checkPreOpen()
    if currency == 'USD':
        checkForJared()
    print(stockList)
    end = time.time()
    print("time cost",end-start)

    # if currency == 'USD':
    #     checkPreVolume()
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
            #     checkPreOpen()
            #     checkForJared()
            #     print(stockList)
            if dayLightSaving:
                if(hour == 13 and minute == 18 and sec == 30):
                    checkPreVolume()

                if(hour == 13 and minute == 26 and sec == 0):
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
                if(hour == 14 and minute == 18 and sec == 0):
                    checkPreVolume()

                if(hour == 14 and minute == 26 and sec == 0):
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