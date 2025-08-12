import pandas as pd
import json
import math
from datetime import datetime as dt, timedelta
import sys
mainFolder = '../../'
sys.path.append(mainFolder)
from modules.movingAverage import Sma
from modules.aiztradingview import GetProfit,GetADR,GetScannerWithAttribute,GetDRMore,GetREITMore,GetAssetDebt
import pickle
import gc

from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
# ib.connect('127.0.0.1', 7497, clientId=4)

def normalizeFloat(price, sample1):
    strFloat1 = str(sample1)
    dec = strFloat1[::-1].find('.')
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

total_cash = 2061
def update_total_balance(*args):
    global total_cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'TotalCashBalance']
    # cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidation']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    print(total_cash)

risk = 0.00613800895 #* 0.5548 * 0.675 * 0.46

def getPreMarketRange(contract, backtestTime):
    hisBarsM1 = ib.reqHistoricalData(
        contract, endDateTime=backtestTime, durationStr='5400 S',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)

    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=4):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=backtestTime, durationStr='5400 S',
            barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
        maxTrys += 1

    preMaxHigh = 0
    preMinLow = 9999

    for i in hisBarsM1:
        if i.high > preMaxHigh:
            preMaxHigh = i.high
        if i.low < preMinLow:
            preMinLow = i.low
    return preMaxHigh, preMinLow

def getMarketRange(contract, eodTime):
    hisBarsM1 = ib.reqHistoricalData(
        contract, endDateTime=eodTime, durationStr='1 D',
        barSizeSetting='1 min', whatToShow='BID', useRTH=True)

    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=4):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=eodTime, durationStr='1 D',
            barSizeSetting='1 min', whatToShow='BID', useRTH=True)
        maxTrys += 1

    return hisBarsM1

df = pd.read_csv (r'%s/backtest/csv/result/trades_status.csv'%(mainFolder))
df.drop
trades = json.loads(df.to_json(orient = 'records'))

# fillterDf = pd.read_csv (r'../csv/livetradersSym.csv', index_col=0)
# fillterDf.drop
# filter_symbols = json.loads(fillterDf.to_json(orient = 'records'))
# filter_sym_list = []
# for i in filter_symbols:
#     filter_sym_list.append(i['symbol'])

filterSymList = GetProfit()
drSymList = GetDRMore()
reitSymList = GetREITMore()
assetDebtList = GetAssetDebt()
adrDict = GetADR('USD')

preMarketDataArr = []
marketDataArr = []
downloadPreMarketData = False
downloadMarketData = False
if not downloadPreMarketData:
    output = open("%s/backtest/pickle/pro/compressed/preMarket/live.p"%(mainFolder), "rb")
    gc.disable()
    preMarketDataArr = pickle.load(output)
    output.close()
    gc.enable()
    print("load PreMarketData finished")

if not downloadMarketData:
    output = open("%s/backtest/pickle/pro/compressed/market/live.p"%(mainFolder), "rb")
    gc.disable()
    marketDataArr = pickle.load(output)
    output.close()
    gc.enable()
    print("load MarketData finished")

QQQD1arr = []
output = open("%s/backtest/pickle/pro/compressed/QQQ6MD1arr.p"%(mainFolder), "rb")
gc.disable()
QQQD1arr = pickle.load(output)
output.close()
gc.enable()
print("load QQQD1arr finished")

SPYD1arr = []
output = open("%s/backtest/pickle/pro/compressed/SPY6MD1arr.p"%(mainFolder), "rb")
gc.disable()
SPYD1arr = pickle.load(output)
output.close()
gc.enable()
print("load SPYD1arr finished")

VTID1arr = []
output = open("%s/backtest/pickle/pro/compressed/VTI6MD1arr.p"%(mainFolder), "rb")
gc.disable()
VTID1arr = pickle.load(output)
output.close()
gc.enable()
print("load VTID1arr finished")

DIAD1arr = []
output = open("%s/backtest/pickle/pro/compressed/DIA6MD1arr.p"%(mainFolder), "rb")
gc.disable()
DIAD1arr = pickle.load(output)
output.close()
gc.enable()
print("load DIAD1arr finished")

IWMD1arr = []
output = open("%s/backtest/pickle/pro/compressed/IWM6MD1arr.p"%(mainFolder), "rb")
gc.disable()
IWMD1arr = pickle.load(output)
output.close()
gc.enable()
print("load IWMD1arr finished")

hisBarsStocksD1arr = []
# output = open("./pickle/pro/compressed/hisBarsStocksRFD1arr.p", "rb")
output = open("%s/backtest/pickle/pro/compressed/hisBarsStocks6MD1Dict.p"%(mainFolder), "rb")
gc.disable()
dataD1Dict = pickle.load(output)
output.close()
gc.enable()
print("load hisBarsStocksD1arr finished")

def checkForOpen():
    maxProfit = 0
    maxPreTpRange = 0
    maxEodMin = 0
    # maxAttribute = 0
    # idx = 0
    # while idx < len(attributeValList):
    # attributeLimit = attributeValList[idx]
    # preTpRange = 0.01
    # while preTpRange <= 6:
    total = 0
    maxfee = 0
    net = 0
    win = 0
    loss = 0
    totalNetProfit = 0
    totalNetLoss = 0
    for trade in trades:
        fee = 2
        symbol = trade['symbol']
        time = trade['time']
        vol = trade['vol']
        op = trade['op']

        if op == None: continue
        if op > 44.89: continue

        if vol < 1: continue
        if (
            symbol not in filterSymList and 
            symbol not in drSymList and 
            symbol not in reitSymList
        ): continue

        if symbol == 'SKLZ': continue
        if symbol == 'MRO': continue
        if symbol == 'KGC': continue

        date = time.split(',')[0]
        
        timeD = dt.strptime(str(date), '%Y-%m-%d')
        backtestTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
        
        preMaxHigh = 0.0 
        preMinLow = 0.0
        if downloadPreMarketData:
            contract = Stock(symbol, 'SMART', 'USD')
            preMaxHigh, preMinLow = getPreMarketRange(contract,backtestTime)
        else:
            for d in preMarketDataArr:
                if d['s'] == symbol and d['time'] == backtestTime:
                    preMaxHigh = d['preMaxHigh']
                    preMinLow = d['preMinLow']
                    break


        # print(preMaxHigh, preMinLow)
        if preMaxHigh - preMinLow < 0.01: continue

        eodTime = backtestTime+timedelta(minutes=90+300)
        dataM1 = []
        contract = Stock(symbol, 'SMART', 'USD')
        if downloadMarketData:
            dataM1 = getMarketRange(contract, eodTime)
        else:
            for d in marketDataArr:
                if d['s'] == symbol:
                    dataM1 = d['dataM1']
                    if dataM1[0].date == backtestTime:
                        break

        if(len(dataM1) < 6): continue

        op = normalizeFloat(preMaxHigh + 0.01 * 16, 0.01)
        # op = normalizeFloat(dataM1[1].high + 0.01, 0.01)

        sl = normalizeFloat(op - 0.03, 0.01)
        # if op > 16.5:
        #     sl = normalizeFloat(op * 0.9930862018, 0.01)
        # if op > 100:
        #     sl = normalizeFloat(op * 0.9977520318, 0.01)

        adrRange = adrDict[symbol]

        if adrRange == 0: print(symbol,adrRange)

        sl = normalizeFloat(op - adrRange * 0.05, 0.01)
        if adrRange > 0.14:
            sl = normalizeFloat(op - adrRange * 0.35, 0.01)
        if adrRange > 0.61:
            sl = normalizeFloat(op - adrRange * 0.48498845154, 0.01)
        # if adrRange > 1.26:
        #     sl = normalizeFloat(op - adrRange * 0.54731808349, 0.01)

        testGap = True

        if testGap:
            hisBarsD1 = []
            if downloadMarketData:
                hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=backtestTime, durationStr='60 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                hisBarsD1.pop()
            else:
                dataD1 = dataD1Dict[symbol]

                if(len(dataD1) < 16):continue
                hisBarsD1 = list(filter(lambda x:x.date <= backtestTime.date(),dataD1))
            
            hisBarsD1 = hisBarsD1[::-1]

            if hisBarsD1[0].open < hisBarsD1[1].close * 1.02: continue
            gapRange = hisBarsD1[0].open - hisBarsD1[1].close

            if not (
                (
                    hisBarsD1[2].close > hisBarsD1[2].open * 0.9917144678138942 and
                    hisBarsD1[1].close > hisBarsD1[1].open * 0.9980928162746343
                ) or
                (
                    hisBarsD1[1].low < hisBarsD1[2].low and
                    hisBarsD1[1].high > hisBarsD1[2].high
                )
            ):
                adr = (
                    abs(hisBarsD1[1].close - hisBarsD1[3].open) +
                    abs(hisBarsD1[4].close - hisBarsD1[6].open) +
                    abs(hisBarsD1[7].close - hisBarsD1[9].open) +
                    abs(hisBarsD1[10].close - hisBarsD1[12].open) +
                    abs(hisBarsD1[13].close - hisBarsD1[15].open)
                ) / 5
                
                if gapRange/adr > 2.82: continue

            if not (
                (
                    hisBarsD1[3].close < hisBarsD1[3].open and
                    hisBarsD1[2].close < hisBarsD1[2].open and
                    hisBarsD1[1].close > hisBarsD1[1].open
                ) or
                hisBarsD1[1].close < hisBarsD1[1].open or
                hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673
            ):
                adr = (
                    abs(hisBarsD1[1].close - hisBarsD1[10].open) +
                    abs(hisBarsD1[11].close - hisBarsD1[20].open) +
                    abs(hisBarsD1[21].close - hisBarsD1[30].open) +
                    abs(hisBarsD1[31].close - hisBarsD1[40].open) +
                    abs(hisBarsD1[41].close - hisBarsD1[50].open)
                ) / 5

                if gapRange/adr > 0.41: continue

            if len(hisBarsD1) > 101:
                if not (
                    (
                        hisBarsD1[2].close < hisBarsD1[2].open and
                        hisBarsD1[1].close < hisBarsD1[1].open
                    ) or
                    hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673 or
                    (
                        hisBarsD1[3].close >= hisBarsD1[3].open and
                        hisBarsD1[2].close > hisBarsD1[2].open and
                        hisBarsD1[1].close > hisBarsD1[1].open * 0.993355481727574
                    ) or
                    (
                        hisBarsD1[1].high / hisBarsD1[2].high > 0.99440037330844 and
                        hisBarsD1[1].low < hisBarsD1[2].low
                    )
                ):
                    adr = (
                        abs(hisBarsD1[1].close - hisBarsD1[20].open) +
                        abs(hisBarsD1[21].close - hisBarsD1[40].open) +
                        abs(hisBarsD1[41].close - hisBarsD1[60].open) +
                        abs(hisBarsD1[61].close - hisBarsD1[80].open) +
                        abs(hisBarsD1[81].close - hisBarsD1[100].open)
                    ) / 5

                    if gapRange/adr > 0.34: continue

            hisBarsQQQD1 = list(filter(lambda x:x.date <= backtestTime.date(),QQQD1arr))
            hisBarsSPYD1 = list(filter(lambda x:x.date <= backtestTime.date(),SPYD1arr))
            hisBarsVTID1 = list(filter(lambda x:x.date <= backtestTime.date(),VTID1arr))
            hisBarsDIAD1 = list(filter(lambda x:x.date <= backtestTime.date(),DIAD1arr))
            hisBarsIWMD1 = list(filter(lambda x:x.date <= backtestTime.date(),IWMD1arr))
            # hisBarsXLFD1 = list(filter(lambda x:x.date <= backtestTime.date(),XLFD1arr))
            # hisBarsTLTD1 = list(filter(lambda x:x.date <= backtestTime.date(),TLTD1arr))
            # hisBarsIEFD1 = list(filter(lambda x:x.date <= backtestTime.date(),IEFD1arr))

            hisBarsQQQD1 = hisBarsQQQD1[::-1]
            hisBarsSPYD1 = hisBarsSPYD1[::-1]
            hisBarsVTID1 = hisBarsVTID1[::-1]
            hisBarsDIAD1 = hisBarsDIAD1[::-1]
            hisBarsIWMD1 = hisBarsIWMD1[::-1]
            # hisBarsXLFD1 = hisBarsXLFD1[::-1]
            # hisBarsTLTD1 = hisBarsTLTD1[::-1]
            # hisBarsIEFD1 = hisBarsIEFD1[::-1]

            buy = 0
            opEndTime = ''

            slByClose = hisBarsD1[1].close

            if sl < slByClose: sl = slByClose

            # if (
            #     hisBarsD1[0].open > hisBarsD1[1].close * 1.115132275
            # ): continue

            # Warrior Trading
            # if hisBarsD1[1].close > hisBarsD1[1].open: continue

            # Red Bar improved
            # if hisBarsD1[1].close-hisBarsD1[1].low > 0:
            #     if not (
            #         (hisBarsD1[1].high-hisBarsD1[1].close) /
            #         (hisBarsD1[1].close-hisBarsD1[1].low) > 0.37
            #     ): continue
            maxHigh = hisBarsD1[1].high
            for i in range(2,3):
                if hisBarsD1[i].high > maxHigh:
                    maxHigh = hisBarsD1[i].high

            minLow = hisBarsD1[1].low
            for i in range(2,3):
                if hisBarsD1[i].low < minLow:
                    minLow = hisBarsD1[i].low

            if hisBarsD1[1].close-minLow > 0:
                if not (
                    (maxHigh-hisBarsD1[1].close) /
                    (hisBarsD1[1].close-minLow) > 0.03
                ): continue

            hisBarsD1avgPriceArr = []
            hisBarsD1closeArr = []
            for d in hisBarsD1:
                avgPrice = (d.high+d.low) / 2
                hisBarsD1avgPriceArr.append(avgPrice)
                hisBarsD1closeArr.append(d.close)

            if not hisBarsD1[1].close <= hisBarsD1[1].open:
                smaD1 = Sma(hisBarsD1avgPriceArr[1:29], 28)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < -0.17: continue

            # Warrior Trading
            # smaD1 = Sma(hisBarsD1closeArr[1:21], 20)
            # bias = (hisBarsD1[1].close-smaD1)/smaD1
            # if bias < 0: continue

            # if (
            #     hisBarsD1[0].open < hisBarsD1[15].high and
            #     hisBarsD1[0].open > hisBarsD1[15].close and
            #     hisBarsD1[0].open < hisBarsD1[14].high and
            #     hisBarsD1[0].open > hisBarsD1[14].close and
            #     hisBarsD1[0].open < hisBarsD1[10].high and
            #     hisBarsD1[0].open > hisBarsD1[10].close and
            #     hisBarsD1[0].open < hisBarsD1[9].high and
            #     hisBarsD1[0].open > hisBarsD1[9].close
            # ): continue

            # if (
            #     hisBarsD1[1].low > hisBarsD1[5].low and
            #     hisBarsD1[1].close < hisBarsD1[5].high and
            #     hisBarsD1[1].low > hisBarsD1[4].low and
            #     hisBarsD1[1].close < hisBarsD1[4].high and
            #     hisBarsD1[1].low > hisBarsD1[2].low and
            #     hisBarsD1[1].close < hisBarsD1[2].high
            # ): continue

            gapRange = hisBarsD1[0].open/hisBarsD1[1].high
            qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].high
            # spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].high
            # vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].high
            # diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].high
            iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].high
            # xlfGapRange = hisBarsXLFD1[0].open/hisBarsXLFD1[1].high
            # tltGapRange = hisBarsTLTD1[0].open/hisBarsTLTD1[1].high
            # iefGapRange = hisBarsIEFD1[0].open/hisBarsIEFD1[1].high
            
            if (
                gapRange < qqqGapRange * 0.937 or
                gapRange < iwmGapRange * 0.937
            ): continue

            gapRange = hisBarsD1[0].open/hisBarsD1[1].close
            qqqGapRange = hisBarsQQQD1[0].open/hisBarsQQQD1[1].close
            spyGapRange = hisBarsSPYD1[0].open/hisBarsSPYD1[1].close
            vtiGapRange = hisBarsVTID1[0].open/hisBarsVTID1[1].close
            diaGapRange = hisBarsDIAD1[0].open/hisBarsDIAD1[1].close
            iwmGapRange = hisBarsIWMD1[0].open/hisBarsIWMD1[1].close
            # xlfGapRange = hisBarsXLFD1[0].open/hisBarsXLFD1[1].close
            # tltGapRange = hisBarsTLTD1[0].open/hisBarsTLTD1[1].high
            # iefGapRange = hisBarsIEFD1[0].open/hisBarsIEFD1[1].high
            
            if (
                gapRange < qqqGapRange * 1.013 or
                gapRange < spyGapRange * 1.013 or
                gapRange < vtiGapRange * 1.013 or
                gapRange < diaGapRange * 1.013 or
                gapRange < iwmGapRange * 1.013
            ): continue

            if  hisBarsD1[1].close / hisBarsD1[1].open > 0.926610644257703:
                if hisBarsD1[1].close / hisBarsD1[3].open > 1.06: continue

            if not (
                (
                    hisBarsD1[2].close < hisBarsD1[2].open and
                    hisBarsD1[1].close > hisBarsD1[1].open
                ) or
                (
                    hisBarsD1[4].close < hisBarsD1[4].open and
                    hisBarsD1[3].close > hisBarsD1[3].open and
                    hisBarsD1[2].close > hisBarsD1[2].open and
                    hisBarsD1[1].close < hisBarsD1[1].open
                ) or
                hisBarsD1[1].close / hisBarsD1[1].low > 1.1180648619673 or
                (
                    hisBarsD1[2].close > hisBarsD1[2].open and
                    hisBarsD1[1].close > hisBarsD1[1].open
                )
            ):
                if hisBarsD1[1].close / hisBarsD1[5].open > 1.18: continue

            if not hisBarsD1[1].close > hisBarsD1[1].open * 0.993355481727574:
                smaD1 = Sma(hisBarsD1closeArr[1:51], 50)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                # if bias > -0.05: continue
                if bias > 0.55: continue

            if not (
                hisBarsD1[2].close > hisBarsD1[2].open and
                hisBarsD1[1].close < hisBarsD1[1].open
            ):
                smaD1 = Sma(hisBarsD1closeArr[1:9], 8)
                bias = (hisBarsD1[1].close-smaD1)/smaD1
                if bias < -0.09: continue

            smaD1 = Sma(hisBarsD1closeArr[1:26], 25)
            bias = (hisBarsD1[1].close-smaD1)/smaD1
            if bias < -0.2: continue

            smaD1 = Sma(hisBarsD1closeArr[1:101], 100)
            bias = (hisBarsD1[1].close-smaD1)/smaD1
            if bias < -0.54: continue

        if op - sl < 0.01: continue

        tp = op + adrRange * 4.47 #op + (op-sl) * tpVal
        
        if preMaxHigh - preMinLow > 0.58:
            tp = op + (preMaxHigh - preMinLow) * 1.14516129032

        r3 = (
            (hisBarsD1[3].high-hisBarsD1[3].close) /
            (hisBarsD1[3].high-hisBarsD1[3].low)
        )
        r2 = (
            (hisBarsD1[2].high-hisBarsD1[2].close) /
            (hisBarsD1[2].high-hisBarsD1[2].low)
        )
        r1 = (
            (hisBarsD1[1].high-hisBarsD1[1].close) /
            (hisBarsD1[1].high-hisBarsD1[1].low)
        )

        if (
            (r3 > 0.98 and r2 > 0.78 and r1 > 0.48) or
            (r3 > 0.61 and r2 > 0.65 and r1 > 0.98)
        ):
            tp = op + adrRange * 0.52241242691

        if hisBarsD1[0].open > hisBarsD1[1].high:
            tp = op + adrRange * 1.88149055444

        if adrRange>0.83 and gapRange > 1.026095060577819:
            tp = op + adrRange * 0.71849526685
        if gapRange > 1.0320855614973262:
            tp = op + adrRange * 0.44915782906
        
        if adrRange > 2:
            tp = op + adrRange * 1.25
        tp = normalizeFloat(tp, 0.01)

        riskPerTrade = total_cash * risk
        vol = int(riskPerTrade / (op - sl))
        
        volLimit = 5
        # volLimit = 4
        # volLimit = 8
        # if op >= 14: volLimit = 4
        # volLimit = 10

        # if op >= 14: volLimit = 4

        if not (
            # (op >= 3)
            op < total_cash*0.83657741748/volLimit
            and vol >= volLimit
        ): continue

        volMax = int(total_cash/(op*1.003032140691))
        if vol > volMax: vol = volMax
        if vol < volLimit: continue

            # print("vol",vol)

        eod = True

            # print(dataM1[0].date, dataM1[-1].date)

        moveSLTime = backtestTime+timedelta(minutes=19)
        cancelTime = backtestTime+timedelta(minutes=16)
        exitTime = backtestTime+timedelta(minutes=155)

        trade['status'] = ''
        
        for i in dataM1:
            if i.date >= cancelTime: continue
            if i.high >= op:
                trade['status'] = i.date
                break

        triggeredTime = ''
        tpTime = ''
        trade['result'] = ''
        if trade['status'] != '':
            triggeredTime = trade['status']
            # print(triggeredTime, eodTime)
            endTime = exitTime
            for i in dataM1:
                if i.date >= triggeredTime:
                    if i.date == triggeredTime:
                        if i.high >= tp:
                            net = (tp-op)*vol - fee
                            trade['total'] = net
                            if(net > 0):
                                trade['result'] = 'profit'
                                totalNetProfit += net
                                win += 1
                            else:
                                trade['result'] = 'loss'
                                totalNetLoss += net
                                loss += 1
                            total += net
                            tpTime = i.date - triggeredTime
                            break
                    else:
                        # print(i.date,moveSLTime)
                        # if i.date == moveSLTime:
                        #     sl = i.low - 0.01
                        #     print("moveSL",sl)
                        if i.low <= sl:
                            net = (sl-op)*vol - fee
                            trade['total'] = net
                            trade['result'] = 'loss'
                            totalNetLoss += net
                            loss += 1
                            total += net
                            break

                        if i.high >= tp:
                            net = (tp-op)*vol - fee
                            trade['total'] = net
                            if(net > 0):
                                trade['result'] = 'profit'
                                totalNetProfit += net
                                win += 1
                            else:
                                trade['result'] = 'loss'
                                totalNetLoss += net
                                loss += 1
                            total += net
                            tpTime = i.date - triggeredTime
                            break
                        
                        if eod:
                            # print(i.date,endTime)
                            if i.date >= endTime:
                                # print(endTime)
                                if(i.open > op):
                                    net = (i.open-op)*vol - fee
                                    trade['total'] = net
                                    if(net > 0):
                                        trade['result'] = 'profit close'
                                        totalNetProfit += net
                                        win += 1
                                        tpTime = i.date
                                    else:
                                        trade['result'] = 'loss close'
                                        totalNetLoss += net
                                        loss += 1
                                    total += net
                                else:
                                    net = (i.open-op)*vol - fee
                                    trade['total'] = net
                                    trade['result'] = 'loss close'
                                    totalNetLoss += net
                                    loss += 1
                                    total += net
                                break
        
        # print(symbol,vol,op,sl,net,tpTime)
        # print(symbol,tpTime)
        # total += profit
        
        if downloadPreMarketData:
            preMarketDataArr.append(
                {
                    's': symbol,
                    'time': backtestTime,
                    'preMaxHigh': preMaxHigh,
                    'preMinLow': preMinLow
                }
            )

        if downloadMarketData:
            marketDataArr.append(
                {
                    's': symbol,
                    'time': eodTime,
                    'dataM1': dataM1
                }
            )

    print("total",total)
    print("maxfee",maxfee)
    print(win,loss)
    if total > maxProfit:
        maxProfit = total
    print("maxProfit", maxProfit)

    if downloadPreMarketData:
        pickle.dump(preMarketDataArr, open("../pickle/pro/compressed/preMarket/live_1001.p", "wb"),protocol=-1)
        print("pickle dump finished")

    if downloadMarketData:
        pickle.dump(marketDataArr, open("../pickle/pro/compressed/market/live_1001.p", "wb"),protocol=-1)
        print("pickle dump finished")

def main():
    # update_total_balance()
    checkForOpen()

if __name__ == '__main__':
    main()
    # import cProfile
    # cProfile.run('main()','output.dat')

    # import pstats
    # from pstats import SortKey

    # with open("output_time.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("time").print_stats()
    
    # with open("output_calls.txt", "w") as f:
    #     p = pstats.Stats("output.dat", stream=f)
    #     p.sort_stats("calls").print_stats()