rootPath = '.'
import sys
sys.path.append(rootPath)
import pandas as pd
import os
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp

ibc = ibc.Ib()
ib = ibc.GetIB(20)

resPath = f'{rootPath}/data/Reverse.csv'

reverseList = []
if os.path.exists(resPath):
    df = pd.read_csv(resPath)
    reverseList = list(df.Symbol.values)

def CheckLower(symbol):
    shift = 0
    contract = ibc.GetStockContract(symbol)
    hisBarsD1 = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='5 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
    if len(hisBarsD1) < 5: return False
    if hisBarsD1[-1-shift].open<hisBarsD1[-2-shift].low:
        return True
    return False

total_cash, avalible_cash = ibc.GetTotalCash()
basicPoint = 0.01

def HandleBuy(symbol):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    if op > ask - 0.01: op = ask - 0.01
    vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,tp)
        ibc.HandleBuyLimit(symbol,vol,op,sl,tp,basicPoint)
        
ignoreList = []
passList = []
positions = ibc.GetPositions()
for symbol in reverseList:
    if symbol in ignoreList: continue
    if symbol in positions: continue
    if CheckLower(symbol):
        print('REVERSE',symbol)
        HandleBuy(symbol)
        passList.append(symbol)
        break
print(passList)