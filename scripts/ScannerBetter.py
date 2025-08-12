from ib_insync import *
import io, sys

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=1)

hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                   locationCode='STK.US.MAJOR',
                                   scanCode='HOT_BY_VOLUME')

scanner = ib.reqScannerData(hot_stk_by_volume, [])

for stock in scanner[:11]: # loops through the first 10 stocks in the scanner
    rank = stock.rank
    contract = stock.contractDetails.contract
    secType = stock.contractDetails.contract.secType
    conId = stock.contractDetails.contract.conId
    symbol = stock.contractDetails.contract.symbol
    exchange = stock.contractDetails.contract.exchange
    currency = stock.contractDetails.contract.currency
    localSymbol = stock.contractDetails.contract.localSymbol
    tradingClass = stock.contractDetails.contract.tradingClass

    print('Stock:', rank, secType, symbol, exchange) 