from ib_insync import *
import pandas as pd
import math
from typing import NamedTuple
import sys
from logger import log
from datetime import datetime as dt, timedelta
import json

ib = IB()

# IB Gateway
# ib.connect('127.0.0.1', 4002, clientId=1)

# TWS
ib.connect('127.0.0.1', 7497, clientId=5)

cashDf = pd.DataFrame(ib.accountValues())
# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#    print(cashDf)
# cashDf = cashDf.loc[cashDf['tag'] == 'BuyingPower']
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)

day = ib.reqCurrentTime().day
# 0.02*1.170731707317073170731707317073(r/r = 1) 0.05(r/r=2)
risk = 0.06#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

df = pd.read_csv (r'./trades.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))
total = 0

try:
    net = 0
    win = 0
    loss = 0
    totalNetProfit = 0
    totalNetLoss = 0
    for trade in trades:
        symbol = trade['symbol']
        backtestTime = trade['time']
        op = trade['op']
        sl = trade['sl']
        tp = trade['tp']
        vol = trade['vol']
        if(vol<3): continue
        backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

        #opEndTime = backtestTime+timedelta(minutes=330)
        opEndTime = backtestTime+timedelta(minutes=325)
        #opEndTime = backtestTime+timedelta(minutes=125)

        contract = Stock(symbol, 'SMART', 'USD')
        # hisBarsM30 = ib.reqHistoricalData(
        #     contract, endDateTime='', durationStr='60 D',
        #     barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

        # hisBarsM30 = [data for data in hisBarsM30 if data.date >= backtestTime]

        # opendHisBarsM30 = [data for data in hisBarsM30 if data.date <= opEndTime]

        hisBarsM5 = ib.reqHistoricalData(
            contract, endDateTime=opEndTime, durationStr='90 D',
            barSizeSetting='5 mins', whatToShow='ASK', useRTH=True)

        hisBarsM5 = [data for data in hisBarsM5 if data.date >= backtestTime]

        if(len(hisBarsM5) < 6): continue

        opendHisBarsM5 = [data for data in hisBarsM5 if data.date <= opEndTime]

        eodTime = hisBarsM5[-1].date

        print(backtestTime,eodTime)

        trade['status'] = ''
        for i in opendHisBarsM5:
            if i.high >= op:
                trade['status'] = i.date
                break

        trade['result'] = ''
        if trade['status'] != '':
            triggeredTime = trade['status']
            for i in hisBarsM5:
                if i.date >= triggeredTime:
                    if i.date == triggeredTime:
                        if i.high >= trade['tp']:
                            net = (tp-op)*vol - 2
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
                            break
                    else:
                        if i.low <= trade['sl']:
                            net = (sl-op)*vol - 2
                            trade['total'] = net
                            trade['result'] = 'loss'
                            totalNetLoss += net
                            loss += 1
                            total += net
                            break

                        if i.high >= trade['tp']:
                            net = (tp-op)*vol - 2
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
                            break
                        
                        if i.date >= eodTime:
                            print(symbol," eod ",i.date)
                            if(i.open > op):
                                net = (i.open-op)*vol - 2
                                trade['total'] = net
                                if(net > 0):
                                    trade['result'] = 'profit eod'
                                    totalNetProfit += net
                                    win += 1
                                else:
                                    trade['result'] = 'loss eod'
                                    totalNetLoss += net
                                    loss += 1
                                total += net
                            else:
                                net = (i.open-op)*vol - 2
                                trade['total'] = net
                                trade['result'] = 'loss eod'
                                totalNetLoss += net
                                loss += 1
                                total += net
                            break

    df = pd.DataFrame(trades)
    df.to_csv('./trades_status.csv')
    winrate = 0
    if(win+loss>0):
        winrate = win/(win+loss)
    profitfactor =0
    if(abs(totalNetLoss)>0):
        profitfactor = totalNetProfit/abs(totalNetLoss)
    elif(totalNetProfit>0):
        profitfactor = 99.99

    print("total",str(total),
            "wr",winrate*100,"%",
            "profitfactor",str(profitfactor))

except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)