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
        ib.connect('127.0.0.1', 7497, clientId=4)
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
    df = df[['open', 'EMA','eod','sod','TotSignal']]
    npArr = df.to_numpy()
    return npArr

from numba import jit
@jit(nopython=True)
def backtest(npArr):
    totalGain = 0
    totalLoss = 0
    longTradeOP = np.empty(0)
    shortTradeOP = np.empty(0)
    for i in range(2, len(npArr)):
        if npArr[i][2] > 0:
            op = npArr[i][0]
            if len(longTradeOP) > 0:
                for longTrade in longTradeOP:
                    profit = op - longTrade
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                longTradeOP = np.empty(0)
            if len(shortTradeOP) > 0:
                for shotrTrade in shortTradeOP:
                    profit = shotrTrade - op
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                shortTradeOP = np.empty(0)
            continue
        if (
            npArr[i-2][4] < 0
        ):
            op = npArr[i][0]
            if len(shortTradeOP) > 0:
                for shotrTrade in shortTradeOP:
                    profit = shotrTrade - op
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                shortTradeOP = np.empty(0)
            longTradeOP = np.append(longTradeOP,op)

        elif (
            npArr[i-2][4] > 0
        ):
            op = npArr[i][0]
            if len(longTradeOP) > 0:
                for longTrade in longTradeOP:
                    profit = op - longTrade
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                longTradeOP = np.empty(0)
            shortTradeOP = np.append(shortTradeOP,op)
        # if npArr[i][3] > 0:
        #     op = npArr[i][0]
        #     if longTradeOP == 0:
        #         if npArr[i-1][1] > npArr[i-1][2]:
        #             longTradeOP = op
        #     if shortTradeOP == 0:
        #         if npArr[i-1][1] < npArr[i-1][2]:
        #             shortTradeOP = op
        #     continue
    totalLoss -= 1
    return totalGain, totalLoss

def GetBestMA(symbol):
    df = GetDf(symbol,'USD')
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df = df.assign(hour=df['date'].dt.hour)
    df = df.assign(minute=df['date'].dt.minute)
    df = df.assign(eod=np.where(((df['hour']==4) & (df['minute']>=44)), 1, 0))
    df = df.assign(sod=np.where(((df['hour']==22) & (df['minute']==30)), 1, 0))
    # df = df.assign(eod=np.where(((df['hour']==23) & (df['minute']==50)), 1, 0))
    closeArr = df['close'].tolist()
    maxCapital = 0
    maxRR = 0
    bestX = 0
    bestY = 0
    x = 2
    smaDict = {}
    emaDict = {}
    #47.15 34 76
    #58.39 46 49
    # sma sma 61.93 23 73
    # ema ema 41.14 40 57
    # sma ema 68.68 6 49
    # ema sma 70.23 62 65
    backrollingN = 20
    slopelimit=5e-5
    percentlimit = 0.45
    while x < 73:
        # if x in smaDict:
        #     smaX = smaDict[x]
        # else:
        #     smaX = SmaArr(closeArr, x)
        #     smaDict[x] = smaX
        if x in emaDict:
            emaX = emaDict[x]
        else:
            emaX = EmaArr(closeArr, x)
            emaDict[x] = emaX
        df['EMA'] = emaX
        df['slopeEMA'] = df['EMA'].diff(periods=1)
        df['slopeEMA'] = df['slopeEMA'].rolling(window=backrollingN).mean()

        TotSignal = [0] * len(df)
        for row in range(0, len(df)):
            if df.slopeEMA[row] < -slopelimit and (min(df.open[row], df.close[row])-df.low[row])/(df.high[row]-df.low[row])>percentlimit:
                TotSignal[row]=-1
            if df.slopeEMA[row] > slopelimit and (df.high[row]-max(df.open[row], df.close[row]))/(df.high[row]-df.low[row])>percentlimit:
                TotSignal[row]=1

        df['TotSignal']=TotSignal

        npArr = cleanData(df)
        totalGain, totalLoss = backtest(npArr)
        capital = totalGain+totalLoss
        rr = totalGain/-totalLoss
        if rr > maxRR:
            maxCapital = capital
            maxRR = rr
            bestX = x
            print(f"maxCapital {maxCapital} bestX {bestX} maxRR {maxRR}")
        x += 1
    print(capital)
    print(f"maxCapital {maxCapital} bestX {bestX} maxRR {maxRR}")
    return x

GetBestMA('QQQ')