import pandas as pd
import json
import math
from datetime import datetime as dt, timedelta
import sys

mainFolder = '../../..'
sys.path.append(mainFolder)
from modules.aiztradingview import GetProfit,GetProfitWithADR,GetScannerWithAttribute,GetDRMore,GetREITMore,GetAssetDebt,GetStockDR
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

df = pd.read_csv (r'%s/backtest/csv/trades/live/0820.csv'%(mainFolder))
df.drop
trades = json.loads(df.to_json(orient = 'records'))

# fillterDf = pd.read_csv (r'../csv/livetradersSym.csv', index_col=0)
# fillterDf.drop
# filter_symbols = json.loads(fillterDf.to_json(orient = 'records'))
# filter_sym_list = []
# for i in filter_symbols:
#     filter_sym_list.append(i['symbol'])

filterSymList = GetStockDR()
drSymList = GetDRMore()
reitSymList = GetREITMore()
assetDebtList = GetAssetDebt()

preMarketDataArr = []
marketDataArr = []
downloadPreMarketData = False
downloadMarketData = False
if not downloadPreMarketData:
    output = open('%s/backtest/pickle/pro/compressed/preMarket/live_0820.p'%(mainFolder), "rb")
    gc.disable()
    preMarketDataArr = pickle.load(output)
    output.close()
    gc.enable()
    print("load PreMarketData finished")

if not downloadMarketData:
    output = open('%s/backtest/pickle/pro/compressed/market/live_0820.p'%(mainFolder), "rb")
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

adrList = GetProfitWithADR()
# scanner = GetScannerWithAttribute()
# print(scanner)

# attributeValList = []
# for s in scanner:
#     if s['attribute'] not in attributeValList:
#         attributeValList.append(s['attribute'])
# print(attributeValList)

def checkForOpen():
    assetDebtValList = []
    total_current_assets = 0
    total_assets = 0
    total_debt = 1
    total_liabilities_fy = 0
    total_liabilities_fq = 0
    marketcap = 0
    price_sales_ratio = 1
    sales = 0
    for s in assetDebtList:
        total_current_assets = s['total_current_assets']
        total_assets = s['total_assets']
        net_debt = s['net_debt']
        total_debt = s['total_debt']
        total_liabilities_fy = s['total_liabilities_fy']
        total_liabilities_fq = s['total_liabilities_fq']
        marketcap = s['marketcap']
        price_sales_ratio = s['price_sales_ratio']
        if net_debt == 0: net_debt = 1
        if total_debt == 0: total_debt = 1
        # if total_liabilities_fq == 0: total_liabilities_fq = 1
        assetDebtValList.append(total_current_assets/total_debt)

    assetDebtValList.sort()
    print(assetDebtValList)

    maxProfit = 0
    maxPreTpRange = 0
    maxAttributeLimit = 0
    idx = 0
    while idx < len(assetDebtValList):
        total = 0
        maxfee = 0
        net = 0
        win = 0
        loss = 0
        totalNetProfit = 0
        totalNetLoss = 0
        attributeLimit = assetDebtValList[idx]
        for trade in trades:
            fee = 2
            sym = trade['銘柄コード']
            time = trade['日時']
            vol = trade['数量']
            op = trade['約定価格']
            profit = trade['実現損益']

            total_current_assets = 0
            total_assets = 0
            total_debt = 1
            total_liabilities_fy = 0
            total_liabilities_fq = 0
            marketcap = 0
            price_sales_ratio = 1
            sales = 0
            for s in assetDebtList:
                if s['s'] == sym:
                    total_current_assets = s['total_current_assets']
                    total_assets = s['total_assets']
                    net_debt = s['net_debt']
                    total_debt = s['total_debt']
                    total_liabilities_fy = s['total_liabilities_fy']
                    total_liabilities_fq = s['total_liabilities_fq']
                    marketcap = s['marketcap']
                    price_sales_ratio = s['price_sales_ratio']
                    if total_debt == 0: total_debt = 1
                    sales = marketcap/price_sales_ratio
                    break
            # print(sym,total_current_assets,total_debt)
            if sym in filterSymList:
                if net_debt == 0: net_debt = 1
                if total_debt == 0: total_debt = 1
                # if total_liabilities_fq == 0: total_liabilities_fq = 1
                assetDebtVal = total_current_assets/total_debt
                if assetDebtVal < attributeLimit: continue

            if op == None: continue
            if vol < 0: continue
            if (
                sym not in filterSymList and
                sym not in drSymList and
                sym not in reitSymList
            ): continue
            if op < 7.74: continue
                
            date = time.split(',')[0]
            
            timeD = dt.strptime(str(date), '%Y-%m-%d')
            marketOpenTime = timeD + timedelta(hours = 22) + timedelta(minutes = 30)
            
            if downloadPreMarketData:
                contract = Stock(sym, 'SMART', 'USD')
                preMaxHigh, preMinLow = getPreMarketRange(contract,marketOpenTime)
            else:
                for d in preMarketDataArr:
                    if d['s'] == sym and d['time'] == marketOpenTime:
                        preMaxHigh = d['preMaxHigh']
                        preMinLow = d['preMinLow']
                        break

            if preMaxHigh - preMinLow < 0.01: continue

            op = normalizeFloat(preMaxHigh + 0.01 * 10, 0.01)

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

            sl = normalizeFloat(op - adrRange * 0.04, 0.01)
            if op - sl < 0.01: continue

            tp = op + adrRange * 1.99 #op + (op-sl) * tpVal
            if preMaxHigh - preMinLow > 0.58:
                tp = op + (preMaxHigh - preMinLow) * 1.14516129032
            tp = normalizeFloat(tp, 0.01)

            riskPerTrade = total_cash * risk
            vol = int(riskPerTrade / (op - sl))
            
            volLimit = 7
            if op >= 14: volLimit = 4
            if not (
                (op >= 3)
                and op < total_cash*0.83657741748/volLimit
                and vol >= volLimit
            ): continue

            volMax = int(total_cash/(op*1.003032140691))
            if vol > volMax: vol = volMax

                # print("vol",vol)

            eod = True

            eodTime = marketOpenTime+timedelta(minutes=90+300)
            dataM1 = []
            if downloadMarketData:
                contract = Stock(sym, 'SMART', 'USD')
                dataM1 = getMarketRange(contract, eodTime)
            else:
                for d in marketDataArr:
                    if d['s'] == sym:
                        dataM1 = d['dataM1']
                        if dataM1[0].date == marketOpenTime:
                            break

            if(len(dataM1) < 6): continue

                # print(dataM1[0].date, dataM1[-1].date)

            exitTime = marketOpenTime+timedelta(minutes=315)
            cancelTime = marketOpenTime+timedelta(minutes=90)
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
            maxAttributeLimit = attributeLimit
        print("maxProfit", maxProfit)
        print("maxAttributeLimit", maxAttributeLimit)
        idx += 1

    if downloadPreMarketData:
        pickle.dump(preMarketDataArr, open("../pickle/pro/compressed/preMarket/live_0820.p", "wb"),protocol=-1)
        print("pickle dump finished")

    if downloadMarketData:
        pickle.dump(marketDataArr, open("../pickle/pro/compressed/market/live_0820.p", "wb"),protocol=-1)
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