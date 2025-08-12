from ib_insync import *

ib = IB()

ib.connect('127.0.0.1', 7497, clientId=10)

symbol = 'IWM'
contract = Stock(symbol, 'SMART', 'USD')
chains = ib.reqSecDefOptParams(contract.symbol, '', contract.secType, 9579970)
for optionschain in chains:
    print(optionschain)