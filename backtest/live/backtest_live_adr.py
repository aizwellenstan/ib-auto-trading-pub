import pandas as pd
import json
import math
from datetime import datetime as dt, timedelta
import sys
sys.path.append('../../')
from modules.aiztradingview import GetProfit, GetADR
import pickle
import gc

from ib_insync import *

ib = IB()
# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=2)

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

risk = 0.00613800895 * 0.5548 * 0.675 * 0.46 #*0.4 #* 0.05 #0.79 #0.378 #0.06

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

df = pd.read_csv (r'../csv/trades/live/0820.csv')
df.drop
trades = json.loads(df.to_json(orient = 'records'))

# fillterDf = pd.read_csv (r'../csv/livetradersSym.csv', index_col=0)
# fillterDf.drop
# filter_symbols = json.loads(fillterDf.to_json(orient = 'records'))
# filter_sym_list = []
# for i in filter_symbols:
#     filter_sym_list.append(i['symbol'])

filterSymList = GetProfit()

preMarketDataArr = []
downloadPreMarketData = False
if not downloadPreMarketData:
    output = open("../pickle/pro/compressed/preMarket/live_0820.p", "rb")
    gc.disable()
    preMarketDataArr = pickle.load(output)
    output.close()
    gc.enable()
    print("load PreMarketData finished")

hisBarsStocksH1arr = []
output = open("../pickle/pro/compressed/hisBarsStocksH1arr.p", "rb")
gc.disable()
hisBarsStocksH1arr = pickle.load(output)
output.close()
gc.enable()
print("load hisBarsStocksH1arr finished")

def checkForOpen():
    maxProfit = 0
    maxAdrVal = 0
    adrVal = 1.1
    while adrVal <= 2:
        filterSymList = GetADR(adrVal)
        total = 0
        for trade in trades:
            net = 0
            win = 0
            loss = 0
            totalNetProfit = 0
            totalNetLoss = 0
            fee = 2
            sym = trade['銘柄コード']
            time = trade['日時']
            vol = trade['数量']
            op = trade['約定価格']
            profit = trade['実現損益']

            if op == None: continue
            if vol < 0: continue

            if sym not in filterSymList: continue
            if op < 3: continue
            
            date = time.split(',')[0]
            
            timeD = dt.strptime(str(date), '%Y-%m-%d')
            marketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)

            # print(marketOpenTime)
            
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

            op = normalizeFloat(preMaxHigh + 0.01 * 7, 0.01)
            sl = normalizeFloat(op - 0.14, 0.01)
            if op > 16.5:
                sl = normalizeFloat(op * 0.9930862018, 0.01)
            if op > 100:
                sl = normalizeFloat(op * 0.9977520318, 0.01)

            # adrVal = 29#2.42
            tp = op + (op-sl) * 20.07
            tp = normalizeFloat(tp, 0.01)

            vol = int(total_cash * risk / (op - sl))

            volLimit = 7
            if op >= 14: volLimit = 4
            if not (
                (op >= 3)
                and op < total_cash*0.83657741748/volLimit
                and vol >= volLimit
            ): continue

            eod = False
            dataH1 = []
            for hisBarsStockH1 in hisBarsStocksH1arr:
                if sym == hisBarsStockH1['s']:
                    dataH1 = hisBarsStockH1['d']
                    break
            if(len(dataH1) < 6): continue

            testhisBarsH1 = list(filter(lambda x:x.date >= marketOpenTime,dataH1))
            trade['status'] = ''
            
            for i in testhisBarsH1:
                if i.high >= op:
                    trade['status'] = i.date
                    break

            triggeredTime = ''
            tpTime = ''
            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                endTime = triggeredTime+timedelta(minutes=90+240)
                for i in testhisBarsH1:
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
                                if i.date == endTime:
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

        if downloadPreMarketData:
            pickle.dump(preMarketDataArr, open("../pickle/pro/compressed/preMarket/live_0820.p", "wb"),protocol=-1)
            print("pickle dump finished")

        print(total)
        if total > maxProfit:
            maxProfit = total
            maxAdrVal = adrVal
        print("maxProfit",maxProfit)
        print("maxAdrVal",maxAdrVal)
        adrVal += 0.01

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