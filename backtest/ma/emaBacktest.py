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
    updateData = False
    if os.path.exists(csvPath) and not updateData:
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
    # df = df.tail(1076)
    df = df.dropna()
    # idx = np.where(((df['hour']>=22)&(df['minute']>=30)) | 
    # (df['hour']>=23) |
    # (df['hour']<=4) |
    # ((df['hour']>=4)&(df['minute']<=44)))
    # ((df['hour']>=23)&(df['minute']<=50)))
    # df = df[['date','open', 'emaX', 'emaY','eod','sod','high','low','close']]
    # csvPath = f"./csv/1m/USD/QQQ.csv"
    # df.to_csv(csvPath)
    # df = df.iloc[idx]
    # df = df[['open', 'emaX', 'emaY','eod','sod','high','low','close','ema500','date']]
    # csvPath = './csv/1m/USD/QQQ.csv'
    df = df[['open','high','low','close','eod','sod','emaX','emaY','ema500']]
    # df.to_csv(csvPath)
    npArr = df.to_numpy()
    return npArr

from numba import jit
@jit(nopython=True)
def backtest(npArr):
    addBiasLimit = 0.0026
    tpBiasLimit500 = 0.01694
    barVal = 0.251
    totalGain = 0
    totalLoss = 0
    trades = 0
    longTradeOP = np.empty(0)
    shortTradeOP = np.empty(0)
    for i in range(2, len(npArr)):
        open0 = npArr[i-1][0]
        high = npArr[i-1][1]
        low = npArr[i-1][2]
        close1 = npArr[i-2][3]
        close = npArr[i-1][3]
        eod = npArr[i][4]
        emaX = npArr[i-1][6]
        emaY = npArr[i-1][7]
        ema500 = npArr[i-1][8]
        highBias500 = (high-ema500)/ema500
        lowBias500 = (ema500-low)/ema500

        longTP = False
        shortTP = False

        if eod > 0:
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

        op = npArr[i][0]
        if highBias500 > tpBiasLimit500:
            if len(longTradeOP) > 0:
                for longTrade in longTradeOP:
                    profit = op - longTrade
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                longTradeOP = np.empty(0)
            longTP = True
        elif lowBias500 < -tpBiasLimit500:
            if len(shortTradeOP) > 0:
                for shotrTrade in shortTradeOP:
                    profit = shotrTrade - op
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                shortTradeOP = np.empty(0)
            shortTP = True

        if (
            (close1 < emaY and close > emaY) or
            (open0 < emaY and close > emaY)
        ):
            if len(shortTradeOP) > 0:
                for shotrTrade in shortTradeOP:
                    profit = shotrTrade - op
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                shortTradeOP = np.empty(0)

        if (
            (close1 > emaY and close < emaY) or
            (open0 > emaY and close < emaY)
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
            
        bias = abs(close-ema500)/ema500
        if not longTP:
            if (
                close > emaY and
                low < emaX and
                (
                    (npArr[i-1][3] - npArr[i-1][0]) > 
                    (npArr[i-1][1] - npArr[i-1][2]) * barVal
                )
            ):
                op = npArr[i][0]
                longTradeOP = np.append(longTradeOP,op)
                trades += 1
        if not shortTP:
            if (
                close < emaY and
                high > emaX and
                (
                    (npArr[i-1][0] - npArr[i-1][3]) > 
                    (npArr[i-1][1] - npArr[i-1][2]) * barVal
                )
            ):
                op = npArr[i][0]
                shortTradeOP = np.append(shortTradeOP,op)
                trades += 1

    totalLoss -= 1
    return totalGain, totalLoss, trades

def GetBestMA(symbol):
    df = GetDf(symbol,'USD')
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df = df.assign(hour=df['date'].dt.hour)
    df = df.assign(minute=df['date'].dt.minute)
    df = df.assign(eod=np.where((
        ((df['hour']==4) & (df['minute']>=44)) |
        ((df['hour']>=1) & (df['hour']<22)) |
        ((df['hour']==0) & (df['minute']>8)) |
        ((df['hour']==22) & (df['minute']<43))
    ), 1, 0))
    df = df.assign(sod=np.where(((df['hour']==22) & (df['minute']==30)), 1, 0))
    # df = df.assign(eod=np.where(((df['hour']==23) & (df['minute']==50)), 1, 0))
    closeArr = df['close'].tolist()
    maxCapital = 0
    maxRR = 0
    bestX = 0
    bestY = 0
    maxProfitPerTrade = 0
    emaDict = {}
    ema500 = EmaArr(closeArr, 500)
    df['ema500'] = ema500
    x = 2
    while x < 48:
        y = x +1
        while y < 48:
            if x not in emaDict:
                emaX = EmaArr(closeArr, x)
                emaDict[x] = emaX
            if y not in emaDict:
                emaY = EmaArr(closeArr, y)
                emaDict[y] = emaY
            df['emaX'] = emaDict[x]
            df['emaY'] = emaDict[y]
            npArr = cleanData(df)
            totalGain, totalLoss, trades = backtest(npArr)
            capital = totalGain+totalLoss
            rr = totalGain/-totalLoss
            if trades > 0:
                profitPerTrade = capital/trades
                if profitPerTrade > maxProfitPerTrade:
                    maxCapital = capital
                    maxProfitPerTrade = profitPerTrade
                    maxRR = rr
                    bestX = x
                    bestY = y
                    print(capital)
            y += 1
        x += 1
    print(f"maxCapital {maxCapital} bestX {bestX} bestY {bestY} maxRR {maxRR} maxProfitPerTrade {maxProfitPerTrade}")
    return bestX, bestY

GetBestMA('QQQ')