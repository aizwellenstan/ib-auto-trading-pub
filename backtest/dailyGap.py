import sys 
mainFolder = '..'
sys.path.append(mainFolder)
import datetime as dt
from modules.expir import GetExpir
from modules.discord import Alert
import os
import pandas as pd
import numpy as np
from modules.movingAverage import Sma
from modules.aiztradingview import GetAttr
from numba import types
from numba.typed import Dict
from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=15)

options = ['NVDA', 'MSFT', 'NFLX', 'QCOM', 'AMZN', 'TGT', 
'AFRM', 'AAPL', 'SQ', 'AMD', 'ROKU', 'NKE', 'MRVL', 'BA', 
'WMT', 'JPM', 'PYPL', 'DIS', 'MU', 'IBM', 'SBUX', 'UPST', 
'PG', 'TSM', 'JNJ', 'ORCL', 'C', 'NEM', 'RBLX', 'RCL', 
'UAL', 'MARA', 'KO', 'INTC',
'WFC', 'DAL', 'PLUG', 'JD', 'AA', 'PFE', 'FCX', 'UBER', 
'PINS', 'BAC', 'PARA', 'GOLD', 'LYFT', 'DKNG', 'RIVN', 
'LI', 'GM', 'WBA', 'CCJ', 'NCLH', 'XOM', 'AAL', 
'CLF', 'SLB', 'CMCSA', 'RIOT', 'HAL', 'QS', 'SOFI', 
'CCL', 'M', 'SNAP', 'PLTR', 'F', 'X', 'HOOD', 'CGC', 
'CHPT', 'OXY', 'VZ', 'WBD', 'PTON', 'FCEL', 'KHC', 'MO', 
'AMC', 'TLRY', 'FUBO', 'DVN', 'AVYA', 'BP', 'GOEV', 
'NKLA', 'BMY', 'JWN',
'ET', 'T', 'NIO', 'GPS', 'BBIG', 'NU', 'SIRI', 'MNMD', 
'VALE', 'MRO', 'SWN', 'GSAT', 'WEBR',
'PBR', 'BBBY', 'BABA', 'GOOG',
'GOOGL', 'MMM', 'HD', 'DLTR', 'CRM', 'CRWD', 'TSLA', 
'TXN', 'ZS', 'V', 'MRNA', 'CLAR', 'SE', 'ZM', 
'DOCU', 'SPLK', 'CVNA', 'TDOC', 'PDD', 'SHOP', 'ZIM', 
'BYND', 'ENVX', 'MET', 'DISH', 'GME', 'ISEE', 'CVX', 
'XPEV', 'UMC', 'ATVI', 'FSLR', 'APA', 'MOS', 'NEOG', 
'EQT', 'SNOW', 'COIN']

marketCapDict = GetAttr("market_cap_basic")
newMarCapDict = Dict.empty(key_type=types.unicode_type,value_type=types.uint64)
for symbol, v in marketCapDict.items():
    if symbol in options:
        # if symbol not in performanceList: continue
        if marketCapDict[symbol] < 27705021: continue
        newMarCapDict[np.unicode_(symbol)] = np.uint64(marketCapDict[symbol])
marketCapDict = newMarCapDict

newOptions = []
for symbol in options:
    if symbol in marketCapDict:
        newOptions.append(symbol)
print(newOptions)

def GetData(symbol):
    try:
        contract = Stock(symbol, 'SMART', 'USD')
        data = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='300 D',
            barSizeSetting='1 day', whatToShow='ASK', useRTH=False)
        df = pd.DataFrame(data)
        df = df[['open','high','low','close']]
        npArr = df.to_numpy()
        return npArr
    except: return []

def CheckGap(npArr):
    closeArr = npArr[:,3]
    sma200 = Sma(closeArr, 200)
    bias200 = (closeArr[-1] - sma200) / sma200
    if bias200 < 0.12:
        return False
    return True

dataDict = Dict.empty(key_type=types.unicode_type,value_type=types.float32[:, :])

def main():
    shift = 3
    for symbol in options:
        if symbol not in marketCapDict: continue
        npArr = GetData(symbol)
        npArr2 = npArr[:-shift]
        if len(npArr2) < 1: continue
        if CheckGap(npArr2):
            if npArr[-shift][0] > npArr[-1-shift][3]:
                print('BUY', symbol)

if __name__ == '__main__':
    main()