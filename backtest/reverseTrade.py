rootPath = '..'
import sys
sys.path.append(rootPath)
import modules.ib as ibc
import pandas as pd

ibc = ibc.Ib()
ib = ibc.GetIB(20)
symbol = "CBRL"
contract = ibc.GetStockContract(symbol)
bid = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1 D',
        barSizeSetting='1 min', whatToShow='BID', useRTH=True)
ask = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='1 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=True)
# print(bid, ask)
bid = pd.DataFrame(bid)
ask = pd.DataFrame(ask)
print(bid.iloc[1])
print(ask.iloc[1])