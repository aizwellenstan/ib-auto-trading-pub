from ib_insync import *

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

contract = Stock('QQQ', 'SMART', 'USD')
hisBarsM1 = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='10 Y',
    barSizeSetting='1 min', whatToShow='ASK', useRTH=False)

print(hisBarsM1)