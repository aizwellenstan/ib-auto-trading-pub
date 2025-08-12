import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__))
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.dividendCalendarV2 import GetExDividendWithPayment
import datetime
import modules.ib as ibc
from ib_insync import ScannerSubscription, CFD
from ib_insync.contract import TagValue
import pandas as pd
import math
from modules.trade.options import BuyOption
from config import load_credentials
from modules.trade.utils import floor_round, GetVol
from modules.trade.futures import ExecTrailMOC

CASHACCOUNT = load_credentials('cashAccount')

ibc = ibc.Ib()
ib = ibc.GetIB(7)

stock_total_cash, stock_avalible_cash = ibc.GetTotalCash(CASHACCOUNT)

hot_stk_by_gain = ScannerSubscription(instrument='STK',
                                        locationCode='STK.US.MAJOR',
                                        scanCode='TOP_PERC_GAIN',
                                        belowPrice='25',
                                        abovePrice='2.5',
                                        aboveVolume='0',  # <1407
                                        averageOptionVolumeAbove='37'
                                        )
tagvalues = [
    TagValue("changePercAbove", "17")
]
gainList = ib.reqScannerData(hot_stk_by_gain, [], tagvalues)
print(gainList)
symbolList = [stock.contractDetails.contract.symbol for stock in gainList]
print(symbolList)
# sys.exit()
for stock in gainList:
    contract = stock.contractDetails.contract
    ibc.qualifyContracts(contract)
    npArr = ibc.GetDataNpArr(contract , '1 min')
    if len(npArr) > 0:
        op = npArr[-1][3]
        sl = int(op) - 0.07
        # sl = op - 0.1
        tp = floor_round(op * 1.26315789474, 0.01)
        vol = GetVol(stock_total_cash, op, sl, tp, 1, 1, 'USD')
        MIN_VOL = 12
        if vol < MIN_VOL: 
            print(vol)
            continue
        contractCFD = CFD(contract.symbol, 'SMART', 'USD')
        ExecTrailMOC(ibc, 1, contractCFD, vol, op, sl, 0.01, CASHACCOUNT)
# for stock in gainList:
#     contract = stock.contractDetails.contract
#     ibc.qualifyContracts(contract)
#     symbol = contract.symbol
#     chains = ibc.GetChains(symbol)
    
#     tp = ibc.GetDataNpArr(contract, '1 min')[-1][3]
#     BuyOption(ib, ibc, symbol, chains, 1, 1, tp, CASHACCOUNT)