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
    # df = df[['date','open', 'emaX', 'emaY','eod','sod','high','low','close','ema100']]
    # csvPath = f"./csv/1m/USD/QQQ.csv"
    # df.to_csv(csvPath)
    df = df.iloc[idx]
    df = df[['open','emaX','emaY','emaZ','eod','sod','high','low','close','ema100']]
    npArr = df.to_numpy()
    return npArr

from numba import jit
@jit(nopython=True)
def backtest(npArr):
    tpBiasLimit100 = 0.006781268523
    tpBiasLimit500 = 0.007888697647
    totalGain = 0
    totalLoss = 0
    longTradeOP = np.empty(0)
    shortTradeOP = np.empty(0)
    for i in range(2, len(npArr)):
        # if len(longTradeOP) > 0:
        #     keepLongTradeOP = np.empty(0)
        #     op = npArr[i][0]
        #     for longTrade in longTradeOP:
        #         profit = op - longTrade
        #         if profit > -0.22:
        #             keepLongTradeOP = np.append(keepLongTradeOP,op)
        #         else:
        #             capital += profit
        #     longTradeOP = keepLongTradeOP

        # if len(shortTradeOP) > 0:
        #     keepShortTradeOP = np.empty(0)
        #     op = npArr[i][0]
        #     for shotrTrade in shortTradeOP:
        #         profit = shotrTrade - op
        #         if profit > -0.22:
        #             keepShortTradeOP = np.append(keepShortTradeOP,op)
        #         else:
        #             capital += profit
        #     shortTradeOP = keepShortTradeOP
            
        if npArr[i][4] > 0:
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

        # # TP
        highBias100 = abs(npArr[i-1][6]-npArr[i-1][9])/npArr[i-1][9]
        lowBias100 = abs(npArr[i-1][9]-npArr[i-1][7])/npArr[i-1][9]
        curTpBias100 = max(highBias100,lowBias100)
        # highBias500 = abs(npArr[i-1][5]-npArr[i-1][8])/npArr[i-1][8]
        # lowBias500 = abs(npArr[i-1][8]-npArr[i-1][6])/npArr[i-1][8]
        # curTpBias500 = max(highBias500,lowBias500)
        if (
            curTpBias100 > tpBiasLimit100
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
            if len(longTradeOP) > 0:
                for longTrade in longTradeOP:
                    profit = op - longTrade
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                longTradeOP = np.empty(0)

        if (
            npArr[i-1][8] < npArr[i-1][3]
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
            # longTradeOP = np.append(longTradeOP,op)

        elif (
            npArr[i-1][8] > npArr[i-1][3]
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
            # shortTradeOP = np.append(shortTradeOP,op)
        
        if (
            npArr[i-1][1] > npArr[i-1][3] and
            npArr[i-1][8] < npArr[i-1][1] and
            npArr[i-1][8] > npArr[i-1][2]
        ):
            op = npArr[i][0]
            longTradeOP = np.append(longTradeOP,op)
        elif (
            npArr[i-1][1] < npArr[i-1][3] and
            npArr[i-1][8] > npArr[i-1][1] and
            npArr[i-1][8] < npArr[i-1][2]
        ):
            op = npArr[i][0]
            shortTradeOP = np.append(shortTradeOP,op)
        # if npArr[i][4] > 0:
        #     op = npArr[i][0]
        #     if len(longTradeOP) > 0:
        #         if npArr[i-1][1] > npArr[i-1][2]:
        #             longTradeOP = np.append(longTradeOP,op)
        #     if len(shortTradeOP) > 0:
        #         if npArr[i-1][1] < npArr[i-1][2]:
        #             shortTradeOP = np.append(shortTradeOP,op)
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
    bestZ = 0
    x = 2
    smaDict = {}
    emaDict = {}
    ema100 = EmaArr(closeArr, 100)
    # ema500 = EmaArr(closeArr, 500)
    while x < 55:
        y = 3
        while y < 55:
            if y > x:
                z = 4
                while z < 55:
                    if z > x and z > y:
                        if x in emaDict:
                            emaX = emaDict[x]
                        else:
                            emaX = EmaArr(closeArr, x)
                            emaDict[x] = emaX
                        if y in emaDict:
                            emaY = emaDict[y]
                        else:
                            emaY = EmaArr(closeArr, y)
                            emaDict[y] = emaY
                        if z in emaDict:
                            emaZ = emaDict[z]
                        else:
                            emaZ = EmaArr(closeArr, z)
                            emaDict[z] = emaZ
                        df['emaX'] = emaX
                        df['emaY'] = emaY
                        df['emaZ'] = emaZ
                        df['ema100'] = ema100
                        # df['ema500'] = ema500
                        npArr = cleanData(df)
                        totalGain, totalLoss = backtest(npArr)
                        capital = totalGain+totalLoss
                        rr = totalGain/-totalLoss
                        if rr > maxRR:
                            maxCapital = capital
                            maxRR = rr
                            bestX = x
                            bestY = y
                            bestZ = z
                            print(f"maxCapital {maxCapital} bestX {bestX} bestY {bestY} maxRR {maxRR}")
                    z += 1
            y += 1
        x += 1
    print(capital)
    print(f"maxCapital {maxCapital} bestX {bestX} bestY {bestY} bestZ {bestZ} maxRR {maxRR}")
    return bestX, bestY

GetBestMA('QQQ')