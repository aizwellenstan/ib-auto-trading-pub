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
ib = ibc.GetIB(22)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

def GetData(symbol):
    contract = ibc.GetStockContract(symbol)
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='2 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    return hisBarsD1[-1].close

retraceDict = {'PEP': 0.98}

signalSymbol = "KO"
signalClose = GetData(signalSymbol)
signalAsk, signalBid = ibc.GetAskBid(signalSymbol)

if signalBid > signalClose:
    for symbol, attr in retraceDict.items():
        close = GetData(symbol)
        ask = ibc.GetAsk(symbol)
        if ask < 0.01: continue
        if ask < close:
            print('BUY', symbol)
    