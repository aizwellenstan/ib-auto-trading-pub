from ib_insync import *
import pandas as pd
import math

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=1)

contract = Forex('USDCAD')
# contract = Stock('AMD', 'SMART', 'USD')

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.floor(price * factor) / factor

df = pd.DataFrame(ib.accountValues())
df = df.loc[df['tag'] == 'BuyingPower']
bp = float(df['value'])
print(bp)

def CheckForOpen():
    try:
        symbol = contract.symbol
        """timeframes
        1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 
        30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
        """
        hisBars = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='365 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
        
        df = pd.DataFrame(hisBars)
        sma25 = df.close.rolling(window=25).mean().iloc[-1]
        sma200 = df.close.rolling(window=200).mean().iloc[-1]

        hisBars=hisBars[::-1]

        # Main
        atrRange: float = 3.4
        size: int = 50
        k: int = 0
        buy: int = 0
        sell: int = 0

        ATR = ((hisBars[1].high - hisBars[1].low) +
                (hisBars[2].high - hisBars[2].low) +
                (hisBars[3].high - hisBars[3].low) +
                (hisBars[4].high - hisBars[4].low) +
                (hisBars[5].high - hisBars[5].low)) / 5

        currentLongRange = hisBars[1].close - hisBars[0].low
        currentShortRange = hisBars[0].high - hisBars[1].close

        while(k < size):
            k += 1
            signalCandleClose3 = hisBars[k*2+1].close
            signalCandleOpen3 = hisBars[k*3].open
            bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
            smallCandleRange3 = abs(hisBars[k*3+1].close - hisBars[k*4].open)
            endCandleRange3 = abs(hisBars[1].close - hisBars[k].open)

            if (bigCandleRange3 > smallCandleRange3 * 4):
                if (signalCandleClose3 > signalCandleOpen3
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange3
                    and endCandleRange3 < bigCandleRange3*0.5
                        and currentLongRange < ATR/atrRange):
                    if (hisBars[1].close < hisBars[1].open):
                        if (hisBars[1].high - hisBars[1].close
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose3 < signalCandleOpen3
                    and abs(hisBars[k+1].close-hisBars[k*2].open) < bigCandleRange3
                    and endCandleRange3 < bigCandleRange3*0.5
                        and currentShortRange < ATR/atrRange):
                    if (hisBars[1].close > hisBars[1].open):
                        if (hisBars[1].close - hisBars[1].low
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            sell += 1
                    else:
                        sell += 1

            signalCandleClose6 = hisBars[k*5+1].close
            signalCandleOpen6 = hisBars[k*6].open
            bigCandleRange6 = abs(signalCandleClose6 - signalCandleOpen6)
            smallCandleRange6 = abs(hisBars[k*6+1].close - hisBars[k*7].open)
            endCandleRange6 = abs(hisBars[1].close - hisBars[k].open)

            if (bigCandleRange6 > smallCandleRange6 * 4):
                if (signalCandleClose6 > signalCandleOpen6
                    and abs(hisBars[k*4+1].close - hisBars[k*5].open) < bigCandleRange6
                    and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange6
                    and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange6
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange6
                    and endCandleRange6 < bigCandleRange6*0.5
                        and currentLongRange < ATR/atrRange):
                    if (hisBars[1].close < hisBars[1].open):
                        if (hisBars[1].high - hisBars[1].close
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose6 < signalCandleOpen6
                    and abs(hisBars[k*4+1].close - hisBars[k*5].open) < bigCandleRange6
                    and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange6
                    and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange6
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange6
                    and endCandleRange6 < bigCandleRange6*0.5
                        and currentShortRange < ATR/atrRange):
                    if (hisBars[1].close > hisBars[1].open):
                        if (hisBars[1].close - hisBars[1].low
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            sell += 1
                    else:
                        sell += 1

            signalCandleClose5 = hisBars[k*4+1].close
            signalCandleOpen5 = hisBars[k*5].open
            bigCandleRange5 = abs(signalCandleClose5 - signalCandleOpen5)
            smallCandleRange5 = abs(hisBars[k*5+1].close - hisBars[k*6].open)
            endCandleRange5 = abs(hisBars[1].close - hisBars[k].open)

            if (bigCandleRange5 > smallCandleRange5 * 4):
                if (signalCandleClose5 > signalCandleOpen5
                    and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange5
                    and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange5
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange5
                    and endCandleRange5 < bigCandleRange5*0.5
                        and currentLongRange < ATR/atrRange):
                    if (hisBars[1].close < hisBars[1].open):
                        if (hisBars[1].high - hisBars[1].close
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose5 < signalCandleOpen5
                    and abs(hisBars[k*3+1].close - hisBars[k*4].open) < bigCandleRange5
                    and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange5
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange5
                    and endCandleRange5 < bigCandleRange5*0.5
                        and currentShortRange < ATR/atrRange):
                    if (hisBars[1].close > hisBars[1].open):
                        if (hisBars[1].close - hisBars[1].low
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            sell += 1
                    else:
                        sell += 1

            signalCandleClose4 = hisBars[k*3+1].close
            signalCandleOpen4 = hisBars[k*4].open
            bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
            smallCandleRange4 = abs(hisBars[k*4+1].close - hisBars[k*5].open)
            endCandleRange4 = abs(hisBars[1].close - hisBars[k].open)

            if (bigCandleRange4 > smallCandleRange4 * 4):
                if (signalCandleClose4 > signalCandleOpen4
                    and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange4
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange4
                    and endCandleRange4 < bigCandleRange4*0.5
                        and currentLongRange < ATR/atrRange):
                    if (hisBars[1].close < hisBars[1].open):
                        if (hisBars[1].high - hisBars[1].close
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose4 < signalCandleOpen4
                    and abs(hisBars[k*2+1].close - hisBars[k*3].open) < bigCandleRange4
                    and abs(hisBars[k+1].close - hisBars[k*2].open) < bigCandleRange4
                    and endCandleRange4 < bigCandleRange4*0.5
                        and currentShortRange < ATR/atrRange):
                    if (hisBars[1].close > hisBars[1].open):
                        if (hisBars[1].close - hisBars[1].low
                                > (hisBars[1].high - hisBars[1].low)*0.13):
                            sell += 1
                    else:
                        sell += 1

            # --- 4btp
            if (hisBars[k*4+1].close < hisBars[k*5].open
                and hisBars[k*3+1].close < hisBars[k*4].open
                and hisBars[k*2+1].close > hisBars[k*3].open
                and hisBars[2].close > hisBars[k*2].open
                and hisBars[1].volume > hisBars[2].volume
                and hisBars[1].close < hisBars[2].close
                    and currentLongRange < ATR/atrRange):
                buy += 1

            if (hisBars[k*4+1].close > hisBars[k*5].open
                and hisBars[k*3+1].close > hisBars[k*4].open
                and hisBars[k*2+1].close < hisBars[k*3].open
                and hisBars[2].close < hisBars[k*2].open
                and hisBars[1].volume > hisBars[2].volume
                and hisBars[1].close > hisBars[2].close
                    and currentShortRange < ATR/atrRange):
                sell += 1

            # bias
            bias = (hisBars[1].close-sma25)/sma25

            if(bias < -0.0482831585):
                buy += 1
            if(bias > 0.0482831585):
                sell += 1

            # sma200
            if(hisBars[1].close < hisBars[2].close
                    and hisBars[1].close > sma200):
                buy += 1
            if(hisBars[1].close > hisBars[2].close
                    and hisBars[1].close < sma200):
                sell += 1
            
            # 8btp
            if(k<46):
                if (hisBars[k*7+1].close < hisBars[k*8].open
                    and hisBars[k*6+1].close < hisBars[k*7].open
                    and hisBars[k*5+1].close < hisBars[k*6].open
                    and hisBars[k*4+1].close < hisBars[k*5].open
                    and hisBars[k*3+1].close > hisBars[k*4].open
                    and hisBars[k*2+1].close > hisBars[k*3].open
                    and hisBars[k+1].close > hisBars[k*2].open
                    and hisBars[1].close < hisBars[k].close
                    and currentLongRange < ATR/atrRange):
                    buy += 1

                if (hisBars[k*7+1].close > hisBars[k*8].open
                    and hisBars[k*6+1].close < hisBars[k*7].open
                    and hisBars[k*5+1].close < hisBars[k*6].open
                    and hisBars[k*4+1].close < hisBars[k*5].open
                    and hisBars[k*3+1].close > hisBars[k*4].open
                    and hisBars[k*2+1].close > hisBars[k*3].open
                    and hisBars[k+1].close > hisBars[k*2].open
                    and hisBars[1].close < hisBars[k].close
                    and currentShortRange < ATR/atrRange):
                    sell += 1

        # print(ATR)
        # print(currentLongRange)
        # print(currentShortRange)

        if((buy > 0 or sell > 0) and buy != sell):
            ticker = ib.reqMktDepth(contract)
            ib.sleep(3)
            ask = ticker.domAsks[0].price
            bid = ticker.domBids[0].price

            spread = ask-bid
            ib.cancelMktDepth(contract)
            if(buy > sell):
                low1 = hisBars[1].low
                op = ask
                sl= op-(op-low1)*0.93446601941747572815533980582525
                sl = normalizeFloat(sl, ask, bid)
                tp = op + (op-sl) * 2
                tp = normalizeFloat(tp, ask, bid)
                if (spread < (op - sl) * 0.32):
                    print("BuyStop " + symbol
                            + " vol " + str(int(bp*0.00903/(op-sl)))
                            + " op " + str(op)
                            + " sl " + str(sl)
                            + " tp " + str(tp))
            elif(sell > buy):
                high1 = hisBars[1].high
                op = ask+(high1-ask)*0.93446601941747572815533980582525
                sl= bid
                op = normalizeFloat(op, ask, bid)
                tp = op + (op-sl) * 2
                tp = normalizeFloat(tp, ask, bid)
                if (spread < (op - sl) * 0.32):
                    print("cusBuyStop " + symbol
                            + " vol " + str(int(bp*0.00903/(op-sl)))
                            + " op " + str(op)
                            + " sl " + str(sl)
                            + " tp " + str(tp))
    except Exception as e:
        print(e)

# CheckForOpen()

while(ib.sleep(1)):
    hour = ib.reqCurrentTime().hour
    min = ib.reqCurrentTime().minute
    # sec = ib.reqCurrentTime().second
    if(hour == 13 and min == 45):
        CheckForOpen()
