rootPath = '.'
import sys
sys.path.append(rootPath)
import yfinance as yf
import pandas as pd
import os
from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=21)

resPath = f'{rootPath}/data/ReverseOption.csv'

reverseList = []
if os.path.exists(resPath):
    df = pd.read_csv(resPath)
    reverseList = list(df.Symbol.values)

def CheckLower(symbol):
    contract = Stock(symbol, 'SMART', 'USD')
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='4 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if len(hisBarsD1) < 4: return False
    if hisBarsD1[-1].open<hisBarsD1[-2].low:
        return True
    return False 

passList = []
for symbol in reverseList:
    if CheckLower(symbol):
        print('REVERSE',symbol)
        passList.append(symbol)
print(passList)