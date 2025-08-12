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
cashDf = cashDf.loc[cashDf['tag'] == 'CashBalance']
cashDf = cashDf.loc[cashDf['currency'] == 'USD']
cash = float(cashDf['value'])
print(cash)
risk = 0.06

trades = []

def normalizeFloat(price, sample1, sample2):
    strFloat1 = str(sample1)
    dec1 = strFloat1[::-1].find('.')
    strFloat2 = str(sample2)
    dec2 = strFloat2[::-1].find('.')
    dec = max(dec1, dec2)
    factor = 10 ** dec
    return math.ceil(price * factor) / factor

def getOP(c,price):
    dps = str(ib.reqContractDetails(c)[0].minTick + 1)[::-1].find('.')
    opPrice = round(price + ib.reqContractDetails(c)[0].minTick * 2,dps)
    return opPrice

def check_open():
    try:
        df = pd.read_csv (r'./backtest_op.csv')
        for index, row in df.iterrows():
            symbol = df['銘柄コード'][index]
            date = dt.strptime(df['日時'][index],'%Y-%m-%d, %H:%M:%S').date()

            contract = Stock(symbol, 'SMART', 'USD')
            hisBarsM1 = ib.reqHistoricalData(
                contract, endDateTime=date, durationStr='1 D',
                barSizeSetting='1 min', whatToShow='BID', useRTH=True)
            hisBarsM1 = hisBarsM1[:len(hisBarsM1)-29]
            hisBarsM1 = hisBarsM1[::-1]
            
            print(date,hisBarsM1[0].date)
            op = hisBarsM1[0].open
            if(op>=6.31):
                CheckForBacktestOpen(symbol,
                                        hisBarsM1[0].open, 
                                        hisBarsM1[1].high, 
                                        hisBarsM1[1].low, 
                                        hisBarsM1[0].date)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

def CheckForBacktestOpen(symbol, op, sample1, sample2, time):
    try:
        bias = 0
        contract = Stock(symbol, 'SMART', 'USD')
        ask = sample1
        bid = sample2
        op = normalizeFloat(getOP(contract, op), ask, bid)
        #sl = op-(op-low1) * 0.19080168327400598318141065947957 #0.30753353973168214654282765737875
        sl, slMin = 0, 0
        if(op > 100):
            slMin = op - 1.167
        elif(op >= 50 and op < 100):
            slMin = op - 0.577
        elif(op >= 10 and op<50):
            slMin = op - 0.347
        elif(op < 10):
            slMin = op - 0.145
        sl = max(slMin, sl)
        sl = normalizeFloat(sl, ask, bid)
        if(op != sl):
            tpVal = 21.86
            tp = op + (op-sl) * tpVal
            tp = normalizeFloat(tp, ask, bid)
            volMax = int(cash*risk/op)
            vol = int(cash*risk/(op-sl))
            if(vol>volMax): vol=volMax
            if(vol>=1):
                spread = 0
                spread = ask-bid
                if (spread < (op - sl) * 0.28
                    # and (op-sl)/sl < 0.023880598
                    ):
                    diff = 0.00063717746183
                    if(abs((op-sl)/sl)<diff or abs(op-sl)<=0.01):
                        print("sl too close")
                    else:
                        trades.append(
                            {
                                'symbol': symbol,
                                'time': time,
                                'vol': vol,
                                'op': op,
                                'sl': sl,
                                'tp': tp,
                                'bias': bias,
                            }
                        )
        else:
            print("ask/bid err ",ask," ",bid)
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)
    print("Open終わりました！,GTHF")

def write_res_file():
    df = pd.DataFrame(trades)
    df.to_csv('./trades.csv')

if __name__=='__main__':
    check_open()
    write_res_file()