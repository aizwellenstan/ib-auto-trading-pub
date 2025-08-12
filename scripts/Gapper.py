from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from modules.aiztradingview import GetLowFloat
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp

ibc = ibc.Ib()
ibc.GetIB(36)

total_cash, avalible_cash = ibc.GetTotalCash()

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=0)

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)
risk = 0.021

closeDict = GetLowFloat()
symbolList = list(closeDict.keys())

# Scanner
hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.NYSE,STK.NASDAQ',
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice=19.72,
                                        abovePrice=1.2,
                                        marketCapBelow=1276710213.848115
                                        # aboveVolume=''  # <1407
                                        )

scanner = ib.reqScannerData(hot_stk_by_gain, [])

total_cash, avalible_cash = ibc.GetTotalCash()

# optionCost = 259 + 80 + 307 + 102
# optionCost = 259 + 61 + 5 + 729 + 102 + 42
optionCost = 0
# optionCost = 4386
total_cash -= optionCost
print(total_cash)

def floor_to_nearest_100(number):
    return (number // 100) * 100

basicPoint = 0.01
def HandleBuy(symbol):
    ask, bid = ibc.GetAskBid(symbol)
    op = bid + 0.01
    if op > ask - 0.01: op = ask - 0.01
    vol, sl, tp = GetVolSlTp(symbol, total_cash, avalible_cash, op, 'USD')
    print(vol)
    if(ask>0 and bid>0):
        print(f"ask {ask} bid {bid}")
        print(symbol,vol,op,sl,tp)
        ibc.HandleBuyLimitFree(symbol,vol,op,sl,tp,basicPoint)
        return vol
    return 0


gainList = []
for stock in scanner:
    symbol = stock.contractDetails.contract.symbol
    if symbol not in symbolList: continue
    gainList.append(symbol)
    print(symbol)
print(gainList)

for symbol in gainList:
    vol = HandleBuy(symbol)
    if vol > 0: break
