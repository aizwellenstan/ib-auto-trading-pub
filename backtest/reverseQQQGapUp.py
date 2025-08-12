rootPath = '..'
import sys
sys.path.append(rootPath)
import pandas as pd
import os
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp
from modules.csvDump import LoadDict
from modules.aiztradingview import GetSqueeze

ibc = ibc.Ib()
ib = ibc.GetIB(35)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

retraceDict = {
    'QCOM': 0.99,
    'JNJ': 0.32,
    'GOOG': 0.99,
    'GOOGL': 0.99,
    'NVDA': 0.85,
    'NKE': 0.52,
    'AAPL': 0.95,
    'ROKU': 0.42,
    'AMD': 0.47,
    'ARKK': 0.18,
    'AMZN': 0.72,
    'SPY': 0.99,
    'MSFT': 0.25,
    'TSM': 0.04,
    'SQ': 0.02,
    'TQQQ': 0.99,
    'DIA': 0.05
}

noOptionList = []

shift = 42
def CheckQQQGap():
    contractQQQ = ibc.GetStockContract("QQQ")
    hisBarsQQQD1 = ib.reqHistoricalData(
        contractQQQ, endDateTime='', durationStr=f"{shift+1} D",
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if hisBarsQQQD1[-shift].open<hisBarsQQQD1[-1-shift].close:
        return False
    return True
    
def CheckGap(symbol):
    retraceVal = 0.99
    if symbol in retraceDict:
        retraceVal = retraceDict[symbol] * 0.81203007518
    
    contract = ibc.GetStockContract(symbol)
    
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr=f"{shift+1} D",
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if len(hisBarsD1) < 2: return False
    # if (
    #     (hisBarsD1[-1].high - hisBarsD1[-1].open) /
    #     (hisBarsD1[-1].high - hisBarsD1[-1].low) > 0.76
    # ):
    #     print('0.76 Retrace')
    #     return False
    # ask = ibc.GetAsk(symbol)
    ask = hisBarsD1[-shift].open
    print(ask,hisBarsD1[-1-shift].close)
    if ask < 0.01: return False
    # print(ask,hisBarsD1[-1-shift].close)
    if ask<hisBarsD1[-1-shift].close:
        tp = (
            ask
            + (hisBarsD1[-1-shift].close-ask)
            * retraceVal)
        if symbol in noOptionList: print(symbol, "NOOption")
        print(symbol,'TARGET',tp)
        if shift > 0:
            if (
                tp > hisBarsD1[-shift].high and
                hisBarsD1[-shift].close <= hisBarsD1[-shift].open
            ):  
                print("LOSS", symbol,hisBarsD1[-shift].open,hisBarsD1[-shift].close)
        return True
    return False

def HandleBuy(symbol):
    if CheckGap(symbol):
        ask, bid = ibc.GetAskBid(symbol)
        op = bid + 0.01
        if op > ask - 0.01: op = ask - 0.01
        vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
        if(ask>0 and bid>0):
            # print(f"ask {ask} bid {bid}")
            print(symbol,vol,op,sl,tp)
            # ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
            return vol
    return 0
        
ignoreList = []
passList = []
positions = ibc.GetPositions()

if CheckQQQGap():
    for symbol, retraceVal in retraceDict.items():
        if symbol not in positions:
            trade = HandleBuy(symbol)
        # if trade > 0: break
            
        
