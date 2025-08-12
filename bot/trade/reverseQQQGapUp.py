rootPath = '../..'
import sys
sys.path.append(rootPath)
import pandas as pd
import os
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp
from modules.csvDump import LoadDict
from modules.aiztradingview import GetSqueeze

ibc = ibc.Ib()
ib = ibc.GetIB(34)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

retraceDict = {
    'GOOG': 0.99,
    'TQQQ': 0.99
}

noOptionList = []
shift = 105
def CheckGap(symbol):
    retraceVal = 0.99
    if symbol in retraceDict:
        retraceVal = retraceDict[symbol]
    
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
    CheckGap(symbol)
    # if CheckGap(symbol):
    #     ask, bid = ibc.GetAskBid(symbol)
    #     op = bid + 0.01
    #     if op > ask - 0.01: op = ask - 0.01
    #     vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    #     if(ask>0 and bid>0):
    #         # print(f"ask {ask} bid {bid}")
    #         print(symbol,vol,op,sl,tp)
    #         # ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
    #         return vol
    return 0
        
ignoreList = []
passList = []
positions = ibc.GetPositions()

squeezeDict = GetSqueeze()

contract = ibc.GetStockContract("QQQ")


shift = 106
while shift < 999:
    bid = ib.reqHistoricalData(
    contract, endDateTime='', durationStr=f"{shift+1} D",
    barSizeSetting='1 day', whatToShow='BID', useRTH=True)
    ask = ib.reqHistoricalData(
    contract, endDateTime='', durationStr=f"{shift+1} D",
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if bid[-shift].open > ask[-shift-1].close:
        for symbol, retraceVal in retraceDict.items():
            if symbol not in positions:
                trade = HandleBuy(symbol)
    shift += 1
        # if trade > 0: break
            
        
