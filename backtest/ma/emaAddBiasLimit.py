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
    # df = df.tail(1076)
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
    # df = df[['open', 'emaX', 'emaY','eod','sod','high','low','close','ema100','ema500','date']]
    # csvPath = './csv/1m/USD/QQQ.csv'
    df = df[['open','high','low','close','eod','sod','emaX','emaY','ema100','ema500']]
    # df.to_csv(csvPath)
    npArr = df.to_numpy()
    return npArr

from numba import jit
@jit(nopython=True)
def backtest(npArr, addBiasLimit):
    # addBiasLimit = 0.002640450764
    addBias21Limit = 0.00323163526
    tpBiasLimit100 = 0.006781268523
    tpBiasLimit500 = 0.007888697647
    totalGain = 0
    totalLoss = 0
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
        ema500 = npArr[i-1][9]
        isTP = False
        highBias500 = abs(high-ema500)/ema500
        lowBias500 = abs(ema500-low)/ema500
        curTpBias500 = max(highBias500,lowBias500)
    
        if curTpBias500 > tpBiasLimit500:
            isTP = True

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
        ) > 0:
            op = npArr[i][0]
            if len(longTradeOP) > 0:
                for longTrade in longTradeOP:
                    profit = op - longTrade
                    if profit < 0:
                        totalLoss += profit
                    else:
                        totalGain += profit
                longTradeOP = np.empty(0)

        # if (
        #     open0 <= emaX and open0 <= emaY and open0 <= ema500 and
        #     close >= emaX and close >= emaY and close >= ema500
        # ):
        #     op = npArr[i][0]
        #     longTradeOP = np.append(longTradeOP,op)
        # elif (
        #     open0 >= emaX and open0 >= emaY and open0 >= ema500 and
        #     close <= emaX and close <= emaY and close <= ema500
        # ):
        #     op = npArr[i][0]
        #     shortTradeOP = np.append(shortTradeOP,op)

        bias = abs(close-ema500)/ema500
        bias21 = abs(close-emaY)/emaY
        if (
            # (
            #     close1 < emaY and close > emaY and
            #     close1 < emaX and close > emaX and 
            #     bias > addBiasLimit and bias21 < addBias21Limit
            # ) 
            # or
            # (
            #     open0 < emaY and close > emaY and
            #     open0 < emaX and close > emaX and 
            #     bias > addBiasLimit and bias21 < addBias21Limit
            # ) or
            (
                # low < emaY and close > emaY and
                low < emaX and close > emaX and bias > addBiasLimit
            ) 
            and
            close < ema500
        ):
            op = npArr[i][0]
            longTradeOP = np.append(longTradeOP,op)
        elif (
            # (
            #     close1 > emaY and close < emaY and
            #     close1 > emaX and close < emaX and 
            #     bias > addBiasLimit and bias21 < addBias21Limit
            # ) 
            # or
            # (
            #     open0 > emaY and close < emaY and
            #     open0 > emaX and close < emaX and 
            #     bias > addBiasLimit and bias21 < addBias21Limit
            # ) or
            (
                # high > emaY and close < emaY and
                high > emaX and close < emaX and bias > addBiasLimit
            ) 
            and
            close > ema500
        ):
            op = npArr[i][0]
            shortTradeOP = np.append(shortTradeOP,op)

        # if emaX > emaY:
        #     if close > emaY and (close < emaX or open0 < emaX) and bias > addBiasLimit and not isTP:
        #         op = npArr[i][0]
        #         longTradeOP = np.append(longTradeOP,op)
        # else:
        #     if close < emaY and (close > emaX or open0 > emaX) and bias > addBiasLimit and not isTP:
        #         op = npArr[i][0]
        #         shortTradeOP = np.append(shortTradeOP,op)

        # # # TP
        # highBias100 = abs(npArr[i-1][5]-npArr[i-1][8])/npArr[i-1][8]
        # lowBias100 = abs(npArr[i-1][8]-npArr[i-1][6])/npArr[i-1][8]
        # curTpBias100 = max(highBias100,lowBias100)
        # # highBias500 = abs(npArr[i-1][5]-npArr[i-1][8])/npArr[i-1][8]
        # # lowBias500 = abs(npArr[i-1][8]-npArr[i-1][6])/npArr[i-1][8]
        # # curTpBias500 = max(highBias500,lowBias500)
        # if (
        #     curTpBias100 > tpBiasLimit100
        # ):
        #     op = npArr[i][0]
        #     if len(shortTradeOP) > 0:
        #         for shotrTrade in shortTradeOP:
        #             profit = shotrTrade - op
        #             if profit < 0:
        #                 totalLoss += profit
        #             else:
        #                 totalGain += profit
        #         shortTradeOP = np.empty(0)
        #     if len(longTradeOP) > 0:
        #         for longTrade in longTradeOP:
        #             profit = op - longTrade
        #             if profit < 0:
        #                 totalLoss += profit
        #             else:
        #                 totalGain += profit
        #         longTradeOP = np.empty(0)
        # if (
        #     npArr[i-1][7] < npArr[i-1][2]
        # ):
        #     op = npArr[i][0]
        #     if len(shortTradeOP) > 0:
        #         for shotrTrade in shortTradeOP:
        #             profit = shotrTrade - op
        #             if profit < 0:
        #                 totalLoss += profit
        #             else:
        #                 totalGain += profit
        #         shortTradeOP = np.empty(0)
        # elif (
        #     npArr[i-1][7] > npArr[i-1][2]
        # ):
        #     op = npArr[i][0]
        #     if len(longTradeOP) > 0:
        #         for longTrade in longTradeOP:
        #             profit = op - longTrade
        #             if profit < 0:
        #                 totalLoss += profit
        #             else:
        #                 totalGain += profit
        #         longTradeOP = np.empty(0)
        # if (
        #     npArr[i-1][1] > npArr[i-1][2] * 1.0005 and
        #     npArr[i-1][7] < npArr[i-1][1]
        # ):
        #     op = npArr[i][0]
        #     longTradeOP = np.append(longTradeOP,op)
        # elif (
        #     npArr[i-1][1] < npArr[i-1][2] * 0.9995 and
        #     npArr[i-1][7] > npArr[i-1][1]
        # ):
        #     op = npArr[i][0]
        #     shortTradeOP = np.append(shortTradeOP,op)
    totalLoss -= 1
    return totalGain, totalLoss

def GetBestMA(symbol):
    df = GetDf(symbol,'USD')
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df = df.assign(hour=df['date'].dt.hour)
    df = df.assign(minute=df['date'].dt.minute)
    df = df.assign(eod=np.where((
        ((df['hour']==4) & (df['minute']>=44)) |
        ((df['hour']>=5) & (df['hour']<22)) |
        ((df['hour']==22) & (df['minute']<30))
    ), 1, 0))
    df = df.assign(sod=np.where(((df['hour']==22) & (df['minute']==30)), 1, 0))
    # df = df.assign(eod=np.where(((df['hour']==23) & (df['minute']==50)), 1, 0))
    closeArr = df['close'].tolist()
    maxCapital = 0
    maxRR = 0
    bestX = 0
    bestY = 0
    bestAddBiasLimit = 0
    x = 9
    y = 21
    emaDict = {}
    ema100 = EmaArr(closeArr, 100)
    ema500 = EmaArr(closeArr, 500)
    if x not in emaDict:
        emaX = EmaArr(closeArr, x)
        emaDict[x] = emaX
    if y not in emaDict:
        emaY = EmaArr(closeArr, y)
        emaDict[y] = emaY
    df['emaX'] = emaDict[x]
    df['emaY'] = emaDict[y]
    df['ema100'] = ema100
    df['ema500'] = ema500
    df['bias21'] = abs(df['close']-df['emaY'])/df['emaY']
    df['bias100'] = abs(df['close']-df['ema100'])/df['ema100']
    df['bias500'] = abs(df['close']-df['ema500'])/df['ema500']
    npArr = cleanData(df)
    addBiasLimit = 0.000001
    while addBiasLimit <= 0.002640450764:
        totalGain, totalLoss = backtest(npArr,addBiasLimit)
        capital = totalGain+totalLoss
        rr = totalGain/-totalLoss
        if rr > maxRR:
            maxCapital = capital
            maxRR = rr
            bestX = x
            bestY = y
            bestAddBiasLimit = addBiasLimit
        print(capital)
        addBiasLimit += 0.000001
    print(f"maxCapital {maxCapital} bestX {bestX} bestY {bestY} maxRR {maxRR} bestAddBiasLimit {bestAddBiasLimit}")
    return bestX, bestY

GetBestMA('QQQ')