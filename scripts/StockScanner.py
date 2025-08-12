from ib_insync import *
import time
"""
starttime = time.time()
while True:
    print("tick")
    time.sleep(60.0 - ((time.time() - starttime) % 60.0))
"""
ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)


### Scanner
hot_stk_by_volume = ScannerSubscription(instrument='STK',
                                   locationCode='STK.US.MAJOR',
                                   scanCode='TOP_PERC_GAIN')

scanner = ib.reqScannerData(hot_stk_by_volume, [])

#futures = [ ib_insync.Future("ES", "CFE", localSymbol=s) for s in ["ESU8","ESZ8"]]
#scanner = Stock("")

for stock in scanner[:100]: # loops through the first 10 stocks in the scanner
    try :
        symbol = stock.contractDetails.contract.symbol
        print(symbol)
        # contract = Forex('USDCAD')
        contract = Stock(symbol, 'SMART', 'USD')

        """timeframes
        1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
        """
        hisBars = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='30 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        hisBars=hisBars[::-1]
        
        # Main
        atrRange :float = 3
        size :int = 2
        k :int = 0
        buy :int = 0
        sell :int = 0

        ATR = ((hisBars[1].high - hisBars[1].low) +
                (hisBars[2].high - hisBars[2].low) +
                (hisBars[3].high - hisBars[3].low) +
                (hisBars[4].high - hisBars[4].low) +
                (hisBars[5].high - hisBars[5].low)) /5

        currentLongRange = hisBars[1].close - hisBars[0].low
        currentShortRange = hisBars[0].high - hisBars[1].close

        while(k<size) :
            k+=1
            signalCandleClose3 = hisBars[k+2].close
            signalCandleOpen3 = hisBars[k*3].open
            bigCandleRange3 = abs(signalCandleClose3-signalCandleOpen3)
            smallCandleRange3 = abs(hisBars[k+3].close-hisBars[k*4].open)
            endCandleRange3 = abs(hisBars[1].close-hisBars[k].open)

        if  (signalCandleClose3>signalCandleOpen3
            and bigCandleRange3>smallCandleRange3*1.6
            and abs(hisBars[k+1].close-hisBars[k*2].open)<bigCandleRange3
            and endCandleRange3<bigCandleRange3*0.5
            and hisBars[1].close < hisBars[k*2].open
            and hisBars[1].close < hisBars[k].open
            and currentLongRange<ATR/atrRange) :
            buy+=1

        if  (signalCandleClose3<signalCandleOpen3
            and bigCandleRange3>smallCandleRange3*1.6
            and abs(hisBars[k+1].close-hisBars[k*2].open)<bigCandleRange3
            and endCandleRange3<bigCandleRange3*0.5
            and hisBars[1].close > hisBars[k*2].open
            and hisBars[1].close > hisBars[k].open
            and currentShortRange<ATR/atrRange)  :
            sell+=1

        # print(ATR)
        # print(currentLongRange)
        # print(currentShortRange)
        if buy>0 or sell>0 :
            if buy>sell :
                print("buy")
            else :
                print("sell")

    except Exception as e:
        print(e)