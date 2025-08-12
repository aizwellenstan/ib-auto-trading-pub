import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import pandas as pd
import os
from modules.movingAverage import EmaArr, SmaArr
import numpy as np
from ib_insync import *
def GetDf(symbol, currency):
    csvPath = f"../csv/1m/{currency}/{symbol}.csv"
    if os.path.exists(csvPath):
        df = pd.read_csv(csvPath)
    else:
        ib = IB()
        # IB Gateway
        # ib.connect('127.0.0.1', 4002, clientId=1)
        # TWS
        ib.connect('127.0.0.1', 7497, clientId=3)
        contract = Stock(symbol, 'SMART', 'USD')
        data = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='20 D',
        barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
        df = pd.DataFrame(data)
        df = df[['date','open','high','low','close']]
        df.to_csv(csvPath)
    return df

def cleanData(df):
    df = df.tail(1076)
    df = df.dropna()
    idx = np.where(((df['hour']>=22)&(df['minute']>=30)) | 
    (df['hour']>=23) |
    (df['hour']<=4) |
    ((df['hour']>=4)&(df['minute']<=44)))
    # ((df['hour']>=23)&(df['minute']<=50)))
    df = df.iloc[idx]
    df = df[['open', 'high', 'low', 'close' ,'eod']]
    npArr = df.to_numpy()
    return npArr

from numba import jit
@jit(nopython=True)
def backtest(npArr, pinBarVal):
    capital = 0
    longTradeOP = 0
    shortTradeOP = 0
    for i in range(2, len(npArr)):
        if npArr[i][4] > 0:
            op = npArr[i][0]
            if longTradeOP > 0:
                profit = op - longTradeOP
                capital += profit
                longTradeOP = 0
            if shortTradeOP > 0:
                profit = shortTradeOP - op
                capital += profit
                shortTradeOP = 0
            continue
        if (
            # npArr[i-1][1]-npArr[i-1][2] > 0 and
            # (
            #     npArr[i-1][1]-npArr[i-1][3]
            # ) / 
            # (
            #     npArr[i-1][1]-npArr[i-1][2]
            # ) > pinBarVal and
            npArr[i-1][3] < npArr[i-1][0]
            # npArr[i-1][1]-npArr[i-1][2] > 0 and
            # (
            #     npArr[i-1][3]-npArr[i-1][2]
            # ) / 
            # (
            #     npArr[i-1][1]-npArr[i-1][2]
            # ) > pinBarVal
        ):
            op = npArr[i][0]
            if shortTradeOP > 0:
                profit = shortTradeOP - op
                capital += profit
                shortTradeOP = 0
            longTradeOP = op

        elif (
            # npArr[i-1][1]-npArr[i-1][2] > 0 and
            # (
            #     npArr[i-1][3]-npArr[i-1][2]
            # ) / 
            # (
            #     npArr[i-1][1]-npArr[i-1][2]
            # ) > pinBarVal and
            npArr[i-1][3] > npArr[i-1][0]
            # npArr[i-1][1]-npArr[i-1][2] > 0 and
            # (
            #     npArr[i-1][1]-npArr[i-1][3]
            # ) / 
            # (
            #     npArr[i-1][1]-npArr[i-1][2]
            # ) > pinBarVal
        ):
            op = npArr[i][0]
            if longTradeOP > 0:
                profit = op - longTradeOP
                capital += profit
                longTradeOP = 0
            shortTradeOP = op
    return capital

def main():
    # df = GetDf('SPY','USD')
    df = GetDf('QQQ','USD')
    # df = GetDf('DIA','USD')
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df = df.assign(hour=df['date'].dt.hour)
    df = df.assign(minute=df['date'].dt.minute)
    df = df.assign(eod=np.where(((df['hour']==4) & (df['minute']==44)), 1, 0))
    # df = df.assign(eod=np.where(((df['hour']==23) & (df['minute']==50)), 1, 0))
    # closeArr = df['close'].tolist()
    maxCapital = 0
    bestPinBarVal = 0
    #47.15 34 76
    #58.39 46 49
    # sma sma 61.93 23 73
    # ema ema 41.14 40 57
    # sma ema 68.68 6 49
    # ema sma 70.23 62 65
    npArr = cleanData(df)
    pinBarVal = 0.01
    while pinBarVal < 1:
        capital = backtest(npArr, pinBarVal)
        if capital > maxCapital:
            maxCapital = capital
            bestPinBarVal = pinBarVal
            print(f"maxCapital {maxCapital} bestPinBarVal {bestPinBarVal}")
        pinBarVal += 0.01
    print(capital)
    print(f"maxCapital {maxCapital} bestPinBarVal {bestPinBarVal}")

main()

# def GetData(symbol):
#     contract = Stock(symbol, 'SMART', 'USD')
#     data = ib.reqHistoricalData(
#         contract, endDateTime='', durationStr='20 D',
#         barSizeSetting='1 min', whatToShow='ASK', useRTH=False)
#     df = pd.DataFrame(data)
#     closeArr = []
#     for d in data:
#         closeArr.append(d.close)
#     ema9 = ema(closeArr, 9)
#     ema21 = ema(closeArr, 21)
#     ema100 = ema(closeArr, 100)
#     ema500 = ema(closeArr, 500)
#     df['ema9'] = ema9
#     df['ema21'] = ema21
#     df['ema100'] = ema100
#     df['ema500'] = ema500
#     df = df[['open','high','low','close','ema9','ema21','ema100','ema500']]
#     npArr = df.to_numpy()
    
#     return npArr

# GetData('SPY')


# from modules.data import GetNpData
# import datetime as dt
# from modules.expir import GetExpir
# from modules.discord import Alert
# from modules.optionChain import GetSPXCustomBullPutCreaditSpread, GetSPXBullPutCreaditSpread

# today = dt.datetime.today()
# weekday = today.weekday()

# def BacktestSpread(npArr, currency='USD'):
#     spxPrice, combination = GetSPXBullPutCreaditSpread(5)

#     maxCapital = 0
#     bestCreaditSpread = {}
#     for comb in combination:
#         print(comb)
#         expir = comb['Expir']
#         daysLeft = GetExpir(expir)
#         spreadRange = spxPrice - comb['SellStrike']
#         capital = 0
#         for i in range(
#             1, len(npArr)-daysLeft
#         ):
#             if not npArr[i][4] == weekday: continue
#             if npArr[i+daysLeft][3] < npArr[i][0] - spreadRange: capital -= comb['loss']
#             else: capital += comb['profit']
#         if capital > maxCapital:
#             maxCapital = capital
#             bestCreaditSpread = comb
#     print(f"maxCapital {maxCapital}")
#     print(f"bestCreaditSpread {bestCreaditSpread}")

#     message = f"BullPutCreaditSpread {bestCreaditSpread} \n"
#     message += f"maxCapital {maxCapital}"
#     Alert(message)

# def main(currency='USD'):
#     symbol = '^GSPC'
#     npArr = GetNpData(symbol, currency)
#     BacktestSpread(npArr,currency)

# main()