rootPath = "."
import os
from modules.aiztradingview import GetPerformanceJP
from ib_insync import *

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=2)

symbolList = GetPerformanceJP()

hot_stk_by_gain = ScannerSubscription(instrument='STOCK.HK', # STK
                                        locationCode='STK.HK.TSE_JPN', # STK.US.MAJOR
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice=3000,
                                        abovePrice=500
                                        )

gainList = ib.reqScannerData(hot_stk_by_gain, [])

gainSymList = []

for stock in gainList:
    symbol = stock.contractDetails.contract.symbol
    gainSymList.append(symbol)

# print(gainSymList)

tradableList = []
for symbol in gainSymList:
    if symbol in symbolList:
        tradableList.append(symbol)
print(tradableList)