
from ib_insync import *

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

contract = Stock('QQQ', 'SMART', 'USD')

bid = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='1 D',
    barSizeSetting='1 min', whatToShow='BID', useRTH=True)[0].close

ask = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='1 D',
    barSizeSetting='1 min', whatToShow='ASK', useRTH=True)[0].close

print(bid,ask)