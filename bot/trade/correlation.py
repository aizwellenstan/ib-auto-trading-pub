rootPath = '../..'
import sys
sys.path.append(rootPath)
import pandas as pd
import os
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp
from modules.csvDump import LoadDict
from modules.aiztradingview import GetSqueeze
from modules.data import GetNpData
import numpy as np

ibc = ibc.Ib()
ib = ibc.GetIB(34)

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

correlationThresholdDict = {
'HOOD': 0.11, 
'BYND': 1.0, 
'UBER': 0.11, 'AFRM':0.35, 'GME': 0.27}

retraceDict = {
'HOOD': 0.34, 
'BYND': 0.2, 
'UBER': 0.88, 
'AFRM': 0.17, 'GME': 1.0, 
}

noOptionList = ["WMT", "BBIG", "SWN"]
shift = 19
def CheckGap(signalArr,symbol):
    npArr = GetNpData(symbol)
    # npArr = npArr[-1058:]
    # if len(npArr) < 1058: 
    #     print(symbol, len(npArr))
    #     return False
    minLength = min(len(signalArr),len(npArr),1058)
    signalArr = signalArr[-minLength:]
    npArr = npArr[-minLength:]
    if npArr[-shift][0] >= npArr[-1-shift][3]: return False
    correlation = np.corrcoef(signalArr[:,3][:-1-shift], npArr[:,3][:-1-shift])[0, 1]
    correlation_threshold = correlationThresholdDict[symbol]
    if correlation < correlation_threshold:
        tp = (npArr[-1-shift][3] - npArr[-shift][0]) * retraceDict[symbol] + npArr[-shift][0]
        print(symbol,'BUY', 'TP', tp)
        if shift > 0:
            if (
                tp > npArr[-shift][1] and
                npArr[-shift][3] <= npArr[-shift][0]
            ):  
                print("LOSS", symbol,npArr[-shift][0],npArr[-shift][3])
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

squeezeDict = GetSqueeze()

qqqArr = GetNpData("QQQ")
qqqArr = qqqArr[-1058:]
while shift < 999:
    for symbol, retraceVal in retraceDict.items():
        if symbol not in positions:
            trade = CheckGap(qqqArr,symbol)
        # if trade > 0: break
    shift += 1
            
        
