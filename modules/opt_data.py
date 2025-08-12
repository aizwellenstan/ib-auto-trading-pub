from ib_insync import *


try:
    ib = IB()
    ib.connect('127.0.0.1',7497,clientId=6)
    print("Successfully connected to IB")
except Exception as e:
    print(str(e))

def main():
    underlying = Stock('QQQ', 'SMART', 'USD')
    ib.qualifyContracts(underlying)
    chains = ib.reqSecDefOptParams(underlying.symbol, '', underlying.secType, underlying.conId)


    for optionschain in chains:
        for strike in optionschain.strikes:
            options_contract = Option(underlying.symbol, optionschain.expirations[1], strike, 'P', 'SMART', tradingClass=underlying.symbol)
            optData = ib.reqHistoricalData(options_contract,
                                endDateTime='',
                                durationStr='2 D',
                                barSizeSetting='1 min',
                                whatToShow='TRADES',
                                useRTH=False,
                                keepUpToDate=True,)

            print(optData)

main()