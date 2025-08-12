from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from modules.aiztradingview import GetLowFloat
import modules.ib as ibc
from modules.trade.vol import GetVolSlTp

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=36)

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
gain_sym_list = []
for stock in scanner:
    symbol = stock.contractDetails.contract.symbol
    gain_sym_list.append(symbol)
print(gain_sym_list)
