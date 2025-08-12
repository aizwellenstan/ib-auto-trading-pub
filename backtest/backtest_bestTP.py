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
ib.connect('127.0.0.1', 7497, clientId=4)

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
risk = 0.04#0.02*1.170731707317073170731707317073#0.051020408163265306122448979591837
if(day==5): risk*=0.98

df = pd.read_csv (r'./trades.csv', index_col=0)
df.drop
trades = json.loads(df.to_json(orient = 'records'))
total = 0

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

try:
    globalTPLV = 1
    globalTotal = 0
    tplv = 1
    while(tplv<80):
        for trade in trades:
            symbol = trade['symbol']
            backtestTime = trade['time']
            op = trade['op']
            sl = trade['sl']
            # tp = op+(op-sl)*7.2 #2 #4.5 #3.8 #7.2
            # tp = normalizeFloat(tp,op,sl)
            tp = trade['tp']
            tp = op+(op-sl)*tplv
            trade['tp'] = tp
            vol = trade['vol']
            if(vol<5): continue
            backtestTime = dt.strptime(backtestTime, '%Y-%m-%d %H:%M:%S')

            opEndTime = backtestTime+timedelta(hours = 5)

            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM30 = ib.reqHistoricalData(
                contract, endDateTime='', durationStr='60 D',
                barSizeSetting='30 mins', whatToShow='ASK', useRTH=True)

            hisBarsM30 = [data for data in hisBarsM30 if data.date >= backtestTime]

            opendHisBarsM30 = [data for data in hisBarsM30 if data.date <= opEndTime]
            
            net = 0
            win = 0
            loss = 0
            totalNetProfit = 0
            totalNetLoss = 0

            trade['status'] = ''
            for i in opendHisBarsM30:
                if i.high >= op:
                    trade['status'] = i.date
                    break

            trade['result'] = ''
            if trade['status'] != '':
                triggeredTime = trade['status']
                for i in hisBarsM30:
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
            if(total>globalTotal): 
                globalTotal=total
                globalTPLV = tplv
        tplv += 0.1

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
    print("maxtpLV",str(globalTPLV),str(globalTotal))

except Exception as e:
    print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
    print(e)