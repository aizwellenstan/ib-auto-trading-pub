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
ib = ibc.GetIB(21)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

retraceDict = {
    'AAPL': 0.47,
    'QQQ': 0.51
}

def CheckGap(symbol):
    retraceVal = 0.99
    if symbol in retraceDict:
        retraceVal = retraceDict[symbol]
    shift = 0
    contract = ibc.GetStockContract(symbol)
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if len(hisBarsD1) < 2: return False
    if hisBarsD1[-1-shift].open<hisBarsD1[-2-shift].close:
        tp = (
            hisBarsD1[-1-shift].open
            + (hisBarsD1[-2-shift].close-hisBarsD1[-1-shift].open)
            * retraceVal)
        if tp > ask + 0.07:
            print(symbol,'TARGET',tp)
            return True
    return False

def HandleBuy(symbol):
    # if CheckGap(symbol):
    #     ask, bid = ibc.GetAskBid(symbol)
    #     op = bid + 0.01
    #     if op > ask - 0.01: op = ask - 0.01
    #     vol, sl, tp = GetVolSlTp(symbol, total_cash, op, 'USD')
    #     if(ask>0 and bid>0):
    #         print(f"ask {ask} bid {bid}")
    #         print(symbol,vol,op,sl,tp)
    #         # ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
    #         return vol
    CheckGap(symbol)
    return 0
        
ignoreList = []
passList = []
positions = ibc.GetPositions()

squeezeDict = GetSqueeze()

symbol = 'HIVE'
# HIVE tp 0.96
# VXX option tp 0.99

symbolList = ['QQQ','AAPL']
for symbol in symbolList:
    if symbol not in positions:
        trade = HandleBuy(symbol)
        print('Buy',symbol)
        # if trade > 0: break
