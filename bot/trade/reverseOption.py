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
ib = ibc.GetIB(23)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

noOptionList = ["MARA","NTRA","PFE","LCID"]

retraceDict = {'MARA': 0.57}

shift = 46
def CheckGap(symbol):
    retraceVal = 0.99
    if symbol in retraceDict:
        retraceVal = retraceDict[symbol]
    contract = ibc.GetStockContract(symbol)
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr=f"{shift+1} D",
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if len(hisBarsD1) < 2: return False
    # ask = ibc.GetAsk(symbol)
    # if ask < 0.01: return False
    ask = hisBarsD1[-shift].open
    print(symbol,'ask',ask)
    if ask<hisBarsD1[-1-shift].close:
        tp = (
            ask
            + (hisBarsD1[-1-shift].close-ask)
            * retraceVal)
        if (
            symbol in noOptionList or 
            tp - ask < 0.07
        ):
            print(symbol,'NOOption','TARGET',tp)
        else:
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

shift = 46
while shift < 999:
    for symbol, retraceVal in retraceDict.items():
        if symbol not in positions:
            trade = HandleBuy(symbol)
    shift += 1
            
        
