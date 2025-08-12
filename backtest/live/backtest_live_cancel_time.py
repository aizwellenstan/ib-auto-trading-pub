import pandas as pd
import json
import math
from datetime import datetime as dt, timedelta
import sys
sys.path.append('../../')
from modules.aiztradingview import GetProfit,GetProfitWithADR,GetScannerWithAttribute,GetDRMore,GetREITMore,GetAssetDebt
import pickle
import gc

from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=3)

def normalizeFloat(price, sample1):
    strFloat1 = str(sample1)
    dec = strFloat1[::-1].find('.')
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

total_cash = 0
def update_total_balance(*args):
    global total_cash
    cashDf = pd.DataFrame(ib.accountValues())
    cashDf = cashDf.loc[cashDf['tag'] == 'TotalCashBalance']
    # cashDf = cashDf.loc[cashDf['tag'] == 'NetLiquidation']
    cashDf = cashDf.loc[cashDf['currency'] == 'USD']
    total_cash = float(cashDf['value'])
    print(total_cash)

risk = 0.00613800895 #* 0.5548 * 0.675 * 0.46

def getPreMarketRange(contract, marketOpenTime):
    hisBarsM1 = ib.reqHistoricalData(
        contract, endDateTime=marketOpenTime, durationStr='5400 S',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)

    maxTrys = 0
    while(len(hisBarsM1)<1 and maxTrys<=4):
        print("timeout")
        hisBarsM1 = ib.reqHistoricalData(
            contract, endDateTime=marketOpenTime, durationStr='5400 S',
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

df = pd.read_csv (r'../csv/trades/live/1001.csv')
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
adrList = GetProfitWithADR()

preMarketDataArr = []
marketDataArr = []
downloadPreMarketData = False
downloadMarketData = False
if not downloadPreMarketData:
    output = open("../pickle/pro/compressed/preMarket/live_1001.p", "rb")
    gc.disable()
    preMarketDataArr = pickle.load(output)
    output.close()
    gc.enable()
    print("load PreMarketData finished")

if not downloadMarketData:
    output = open("../pickle/pro/compressed/market/live_1001.p", "rb")
    gc.disable()
    marketDataArr = pickle.load(output)
    output.close()
    gc.enable()
    print("load MarketData finished")

# hisBarsStocksH1arr = []
# output = open("../pickle/pro/compressed/hisBarsStocksH1arr.p", "rb")
# gc.disable()
# hisBarsStocksH1arr = pickle.load(output)
# output.close()
# gc.enable()
# print("load hisBarsStocksH1arr finished")

# scanner = GetScannerWithAttribute()
# print(scanner)

# attributeValList = []
# for s in scanner:
#     if s['attribute'] not in attributeValList:
#         attributeValList.append(s['attribute'])
# print(attributeValList)

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
    eodMin = 2
    while eodMin <= 390:
        total = 0
        maxfee = 0
        net = 0
        win = 0
        loss = 0
        totalNetProfit = 0
        totalNetLoss = 0
        for trade in trades:
            fee = 2
            sym = trade['銘柄コード']
            time = trade['日時']
            vol = trade['数量']
            op = trade['約定価格']
            profit = trade['実現損益']

            if op == None: continue
            if op > 44.89: continue

            if vol < 1: continue
            if (
                sym not in filterSymList and 
                sym not in drSymList and 
                sym not in reitSymList
            ): continue

            if sym == 'SKLZ': continue

            date = time.split(',')[0]
            
            timeD = dt.strptime(str(date), '%Y-%m-%d')
            marketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
            
            preMaxHigh = 0.0 
            preMinLow = 0.0
            if downloadPreMarketData:
                contract = Stock(sym, 'SMART', 'USD')
                preMaxHigh, preMinLow = getPreMarketRange(contract,marketOpenTime)
            else:
                for d in preMarketDataArr:
                    if d['s'] == sym and d['time'] == marketOpenTime:
                        preMaxHigh = d['preMaxHigh']
                        preMinLow = d['preMinLow']
                        break


            # print(preMaxHigh, preMinLow)
            if preMaxHigh - preMinLow < 0.01: continue

            eodTime = marketOpenTime+timedelta(minutes=90+300)
            dataM1 = []
            contract = Stock(sym, 'SMART', 'USD')
            if downloadMarketData:
                dataM1 = getMarketRange(contract, eodTime)
            else:
                for d in marketDataArr:
                    if d['s'] == sym:
                        dataM1 = d['dataM1']
                        if dataM1[0].date == marketOpenTime:
                            break

            if(len(dataM1) < 6): continue

            op = normalizeFloat(preMaxHigh + 0.01 * 16, 0.01)
            # op = normalizeFloat(dataM1[1].high + 0.01, 0.01)

            sl = normalizeFloat(op - 0.03, 0.01)
            # if op > 16.5:
            #     sl = normalizeFloat(op * 0.9930862018, 0.01)
            # if op > 100:
            #     sl = normalizeFloat(op * 0.9977520318, 0.01)

            adrRange = 0
            for s in adrList:
                if s['s'] == sym:
                    adrRange = s['adr']
                    break

            if adrRange == 0: print(sym,adrRange)

            sl = normalizeFloat(op - adrRange * 0.05, 0.01)
            if adrRange > 0.14:
                sl = normalizeFloat(op - adrRange * 0.35, 0.01)

            testGap = True

            if testGap:
                hisBarsD1 = ib.reqHistoricalData(
                contract, endDateTime=marketOpenTime, durationStr='60 D',
                barSizeSetting='1 day', whatToShow='ASK', useRTH=True)
                # print(dataM1[0].date,dataM1[1].date,hisBarsD1[-1].date)

                shift = 1
                gapRange = dataM1[0].open - hisBarsD1[-2+shift].close

                adr = (
                    abs(hisBarsD1[-2+shift].close - hisBarsD1[-3+shift].open) +
                    abs(hisBarsD1[-4+shift].close - hisBarsD1[-5+shift].open) +
                    abs(hisBarsD1[-6+shift].close - hisBarsD1[-7+shift].open) +
                    abs(hisBarsD1[-8+shift].close - hisBarsD1[-9+shift].open) +
                    abs(hisBarsD1[-10+shift].close - hisBarsD1[-11+shift].open)
                ) / 5

                if gapRange/adr > 1.55: continue

                adr = (
                    abs(hisBarsD1[-2+shift].close - hisBarsD1[-4+shift].open) +
                    abs(hisBarsD1[-5+shift].close - hisBarsD1[-7+shift].open) +
                    abs(hisBarsD1[-8+shift].close - hisBarsD1[-10+shift].open) +
                    abs(hisBarsD1[-11+shift].close - hisBarsD1[-13+shift].open) +
                    abs(hisBarsD1[-14+shift].close - hisBarsD1[-16+shift].open)
                ) / 5

                if gapRange/adr > 1.11: continue

                adr = (
                    abs(hisBarsD1[-2+shift].close - hisBarsD1[-5+shift].open) +
                    abs(hisBarsD1[-6+shift].close - hisBarsD1[-9+shift].open) +
                    abs(hisBarsD1[-10+shift].close - hisBarsD1[-13+shift].open) +
                    abs(hisBarsD1[-14+shift].close - hisBarsD1[-17+shift].open) +
                    abs(hisBarsD1[-18+shift].close - hisBarsD1[-21+shift].open)
                ) / 5

                if gapRange/adr > 0.8: continue

                adr = (
                    abs(hisBarsD1[-2+shift].close - hisBarsD1[-6+shift].open) +
                    abs(hisBarsD1[-7+shift].close - hisBarsD1[-11+shift].open) +
                    abs(hisBarsD1[-12+shift].close - hisBarsD1[-16+shift].open) +
                    abs(hisBarsD1[-17+shift].close - hisBarsD1[-21+shift].open) +
                    abs(hisBarsD1[-22+shift].close - hisBarsD1[-26+shift].open)
                ) / 5

                if gapRange/adr > 0.52: continue

                adr = (
                    abs(hisBarsD1[-2+shift].close - hisBarsD1[-8+shift].open) +
                    abs(hisBarsD1[-9+shift].close - hisBarsD1[-15+shift].open) +
                    abs(hisBarsD1[-16+shift].close - hisBarsD1[-22+shift].open) +
                    abs(hisBarsD1[-23+shift].close - hisBarsD1[-29+shift].open) +
                    abs(hisBarsD1[-30+shift].close - hisBarsD1[-36+shift].open)
                ) / 5

                if gapRange/adr > 0.52: continue

                if not (
                    hisBarsD1[-4+shift].close < hisBarsD1[-4+shift].open and
                    hisBarsD1[-3+shift].close < hisBarsD1[-3+shift].open and
                    hisBarsD1[-2+shift].close > hisBarsD1[-2+shift].open
                ):
                    adr = (
                        abs(hisBarsD1[-2+shift].close - hisBarsD1[-11+shift].open) +
                        abs(hisBarsD1[-12+shift].close - hisBarsD1[-21+shift].open) +
                        abs(hisBarsD1[-22+shift].close - hisBarsD1[-31+shift].open) +
                        abs(hisBarsD1[-32+shift].close - hisBarsD1[-41+shift].open) +
                        abs(hisBarsD1[-42+shift].close - hisBarsD1[-51+shift].open)
                    ) / 5

                    if gapRange/adr > 0.41: continue

                if dataM1[0].open/hisBarsD1[-1].close < 1.02:
                # if dataM1[0].open/hisBarsD1[-1].close < 1.003067754:
                    continue
                slByClose = 0
                if (
                    hisBarsD1[-3+shift].close > hisBarsD1[-3+shift].open and
                    hisBarsD1[-2+shift].close > hisBarsD1[-2+shift].open
                ):
                    slByClose = hisBarsD1[-2].close
                if sl < slByClose: sl = slByClose

            if op - sl < 0.01: continue

            tp = op + adrRange * 4.47 #op + (op-sl) * tpVal
            
            if preMaxHigh - preMinLow > 0.58:
                tp = op + (preMaxHigh - preMinLow) * 1.14516129032

            r3 = (
                (hisBarsD1[-4+shift].high-hisBarsD1[-4+shift].close) /
                (hisBarsD1[-4+shift].high-hisBarsD1[-4+shift].low)
            )
            r2 = (
                (hisBarsD1[-3+shift].high-hisBarsD1[-3+shift].close) /
                (hisBarsD1[-3+shift].high-hisBarsD1[-3+shift].low)
            )
            r1 = (
                (hisBarsD1[-2+shift].high-hisBarsD1[-2+shift].close) /
                (hisBarsD1[-2+shift].high-hisBarsD1[-2+shift].low)
            )
            # if gapRange > 1.05:
            #     tp = op + adrRange * 1.36268343815

            if (
                (r3 > 0.98 and r2 > 0.78 and r1 > 0.48) or
                (r3 > 0.61 and r2 > 0.65 and r1 > 0.98)
            ):
                tp = op + adrRange * 0.52241242691
            
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

            moveSLTime = marketOpenTime+timedelta(minutes=39)
            exitTime = marketOpenTime+timedelta(minutes=225)
            # exitTime = marketOpenTime+timedelta(minutes=90+225)
            # cancelMin = eodMin - 1
            # if cancelMin > 90: cancelMin = 90
            cancelTime = marketOpenTime+timedelta(minutes=eodMin)
            # exitTime = marketOpenTime+timedelta(minutes=90)
            # cancelTime = marketOpenTime+timedelta(minutes=30)
            # moveSLTime = marketOpenTime+timedelta(minutes=20)

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
                            # if i.date >= moveSLTime:
                            #     if i.open > op + adrRange * 1.99:
                            #         sl = op + adrRange * 1.99
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
            
            # print(sym,vol,op,sl,net,tpTime)
            # print(sym,tpTime)
            # total += profit
            
            if downloadPreMarketData:
                preMarketDataArr.append(
                    {
                        's': sym,
                        'time': marketOpenTime,
                        'preMaxHigh': preMaxHigh,
                        'preMinLow': preMinLow
                    }
                )

            if downloadMarketData:
                marketDataArr.append(
                    {
                        's': sym,
                        'time': eodTime,
                        'dataM1': dataM1
                    }
                )

        print("total",total)
        print("maxfee",maxfee)
        print(win,loss)
        if total > maxProfit:
            maxProfit = total
            maxEodMin = eodMin
        print("maxProfit", maxProfit)
        print("maxEodMin", maxEodMin)
        eodMin += 1

    if downloadPreMarketData:
        pickle.dump(preMarketDataArr, open("../pickle/pro/compressed/preMarket/live_1001.p", "wb"),protocol=-1)
        print("pickle dump finished")

    if downloadMarketData:
        pickle.dump(marketDataArr, open("../pickle/pro/compressed/market/live_1001.p", "wb"),protocol=-1)
        print("pickle dump finished")

def main():
    update_total_balance()
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