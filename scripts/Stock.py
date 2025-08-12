from ib_insync import *

ib = IB()

# TWS
ib.connect('127.0.0.1', 7497, clientId=3)

# contract = Stock(conId=3691937, symbol='AMZN', exchange='NASDAQ', currency='USD', localSymbol='AMZN', tradingClass='NMS')
contract = Stock(conId=14487893, symbol='GCBC', exchange='NASDAQ', currency='USD', localSymbol='GCBC', tradingClass='SCM')
contract = Option(conId=569900471, symbol='SPY', lastTradeDateOrContractMonth='20220805', strike=285.0, right='P', multiplier='100', currency='USD', localSymbol='SPY   220805P00285000', tradingClass='SPY')

print(contract.strike)

if contract.strike > 0: print('Option')
data = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='365 D',
    barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
if len(data) < 1:
    contract.exchange = 'NYSE'
    data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='365 D',
        barSizeSetting='1 day', whatToShow='ASK', useRTH=True)

print(data)