import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import pandas as pd
import os
from modules.movingAverage import EmaArr, SmaArr
import numpy as np
from modules.riskOfRuin import calcRisk
from ib_insync import *
def GetDf(symbol, currency):
    csvPath = f"../csv/1m/{currency}/{symbol}.csv"
    updateData = False
    if os.path.exists(csvPath) and not updateData:
        df = pd.read_csv(csvPath)
    else:
        global ib
        if ib is None:
            ib = IB()
            # IB Gateway
            # ib.connect('127.0.0.1', 4002, clientId=1)
            # TWS
            ib.connect('127.0.0.1', 7497, clientId=4)
            contract = Stock(symbol, 'SMART', 'USD')
            """timeframes
            1 secs, 5 secs, 10 secs, 15 secs, 30 secs, 1 min, 2 mins, 3 mins, 5 mins, 10 mins, 15 mins, 20 mins, 
            30 mins, 1 hour, 2 hours, 3 hours, 4 hours, 8 hours, 1 day, 1W, 1M
            """
            data = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='20 D',
            barSizeSetting='10 mins', whatToShow='ASK', useRTH=False)
            df = pd.DataFrame(data)
            df = df[['date','open','high','low','close']]
            df.to_csv(csvPath)
        else:
            df = pd.read_csv(csvPath)
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
    # dfLog = df[['open','high','low','close','eod','sod','ema500','date','Weekday']]
    df = df[['open','high','low','close','eod','sod']]
    # csvPath = './csv/1m/USD/NVDA.csv'
    # dfLog.to_csv(csvPath)
    npArr = df.to_numpy()
    return npArr

from numba import jit
# @jit(nopython=True)
def backtest(npArr, tpVal):
    # tpVal = 2
    addBiasLimit = 0.0026
    tpBiasLimit500 = 0.01694
    barVal = 0.251
    # gap = 0
    totalGain = 0
    totalLoss = 0
    win = 0
    loss = 0
    trades = 0
    longTradeOP = np.empty(0)
    shortTradeOP = np.empty(0)
    longTrades = []
    shortTrades = []
    for i in range(2, len(npArr)):
        open0 = npArr[i-1][0]
        high = npArr[i-1][1]
        low = npArr[i-1][2]
        close1 = npArr[i-2][3]
        close = npArr[i-1][3]
        eod = npArr[i][4]
        sod = npArr[i][5]

        longTP = False
        shortTP = False

        # if hour == 4 and minute == 59:
        #     previousClose = npArr[i][3]

        if eod > 0:
            eodPrice = npArr[i][0]
            if len(longTradeOP) > 0:
                for op, sl, tp, condition in longTrades:
                    profit = eodPrice - op
                    if profit < 0:
                        totalLoss += profit
                        loss += 1
                    else:
                        totalGain += profit
                        win += 1
                longTradeOP = np.empty(0)
            if len(shortTradeOP) > 0:
                for op, sl, tp, condition in shortTrades:
                    profit = op - eodPrice
                    if profit < 0:
                        totalLoss += profit
                        loss += 1
                    else:
                        totalGain += profit
                        win += 1
                shortTradeOP = np.empty(0)
            continue

        # op = npArr[i][0]
        # if highBias500 > tpBiasLimit500:
        #     if len(longTradeOP) > 0:
        #         for longTrade in longTradeOP:
        #             profit = op - longTrade
        #             if profit < 0:
        #                 totalLoss += profit
        #                 loss += 1
        #             else:
        #                 totalGain += profit
        #                 win += 1
        #         longTradeOP = np.empty(0)
        #     longTP = True
        # elif lowBias500 < -tpBiasLimit500:
        #     if len(shortTradeOP) > 0:
        #         for shotrTrade in shortTradeOP:
        #             profit = shotrTrade - op
        #             if profit < 0:
        #                 totalLoss += profit
        #                 loss += 1
        #             else:
        #                 totalGain += profit
        #                 win += 1
        #         shortTradeOP = np.empty(0)
        #     shortTP = True

        if len(longTrades) > 0:
            newLongTrades = []
            for op, sl, tp, condition in longTrades:
                if condition == 0:
                    if npArr[i-1][1] > op + 0.01:
                        if npArr[i-1][1] > tp:
                            totalGain += (tp-op)
                            win += 1
                        else:
                            condition = 1
                            newLongTrades.append((op, sl, tp, condition))
                if condition == 1:
                    if npArr[i-1][2] < sl + 0.01:
                        totalLoss += (sl-op)
                        loss += 1
                    elif npArr[i-1][1] > tp: 
                        totalGain += (tp-op)
                        win += 1
            longTrades = newLongTrades

        if len(shortTrades) > 0:
            newShortTrades = []
            for op, sl, tp, condition in shortTrades:
                if condition == 0:
                    if npArr[i-1][2] < op:
                        if npArr[i-1][2] < tp:
                            totalGain += (op-tp)
                            win += 1
                        else:
                            condition = 1
                            newShortTrades.append((op, sl, tp, condition))
                if condition == 1:
                    if npArr[i-1][1] > sl:
                        totalLoss += (op-sl)
                        loss += 1
                    elif npArr[i-1][2] < tp: 
                        totalGain += (op-tp)
                        win += 1
            shortTrades = newShortTrades

        # if (
        #     (close1 < emaY and close > emaY) or
        #     (open0 < emaY and close > emaY)
        # ):
        #     if len(shortTradeOP) > 0:
        #         for shotrTrade in shortTradeOP:
        #             profit = shotrTrade - op
        #             if profit < 0:
        #                 totalLoss += profit
        #             else:
        #                 totalGain += profit
        #         shortTradeOP = np.empty(0)

        # if (
        #     (close1 > emaY and close < emaY) or
        #     (open0 > emaY and close < emaY)
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
            
        # bias = abs(close-ema500)/ema500

        # if sod > 0:
        #     gap =  npArr[i][0] / previousClose

        bar = 8

        if (
            npArr[i-bar*3][3] < npArr[i-bar*3-1][0] and
            npArr[i-bar*2][3] > npArr[i-bar*2-1][0] and
            npArr[i-bar][3] > npArr[i-bar-1][0]
            # npArr[i-1][2] > npArr[i-2][2]
        ):
            op = npArr[i][0]
            longTradeOP = np.append(longTradeOP,op)
            trades += 1
            highArr = np.array(
                [npArr[i-bar*3][1], npArr[i-bar*2][1], npArr[i-bar][1]]
            )
            lowArr = np.array(
                [npArr[i-bar*3][2], npArr[i-bar*2][2], npArr[i-bar][2]]
            )
            op = highArr.max()
            sl = lowArr.min()
            tp = op + (op-sl) * tpVal
            longTrades.append((op,sl,tp,0))
            
        if (
            npArr[i-bar*3][3] > npArr[i-bar*3-1][0] and
            npArr[i-bar*2][3] < npArr[i-bar*2-1][0] and
            npArr[i-bar][3] < npArr[i-bar-1][0]
            # npArr[i-1][1] < npArr[i-2][1]
        ):
            op = npArr[i][0]
            shortTradeOP = np.append(shortTradeOP,op)
            trades += 1
            highArr = np.array(
                [npArr[i-bar*3][1], npArr[i-bar*2][1], npArr[i-bar][1]]
            )
            lowArr = np.array(
                [npArr[i-bar*3][2], npArr[i-bar*2][2], npArr[i-bar][2]]
            )
            op = lowArr.min()
            sl = highArr.max()
            tp = op - (sl-op) * tpVal
            shortTrades.append((op,sl,tp,0))

    totalLoss -= 1
    if win+loss > 0:
        wr = win/(win+loss)
    else wr = 0
    print(wr)
    return totalGain, totalLoss, trades, wr

def GetBestMA(symbol):
    df = GetDf(symbol,'USD')
    df['date'] = pd.to_datetime(df['date'], format="%Y-%m-%d %H:%M:%S")
    df = df.assign(hour=df['date'].dt.hour)
    df = df.assign(minute=df['date'].dt.minute)
    bestHour = 4
    bestMinute = 44
    maxCapital = 0
    maxRR = 0
    bestTpVal = 0
    maxProfitPerTrade = 0
    minRiskOfRuin = 9999
    hour = 4
    minute = 44
    while hour <= 4 or hour >= 22:
        if hour == 22 and minute < 32: break
        if hour == 0 and minute == 0: 
            hour = 23
            minute = 60
        if minute > 0:
            minute -= 1
        else:
            hour -= 1
            minute = 59
        if hour >= 22:
            df = df.assign(eod=np.where((
                ((df['hour']==hour) & (df['minute']>=minute)) |
                ((df['hour']>hour) & (df['hour'] > 22)) |
                ((df['hour']==4) & (df['minute']==45)) |
                ((df['hour']==4) & (df['minute']<60)) |
                ((df['hour']>=5) & (df['hour']<22)) |
                ((df['hour']==22) & (df['minute']<30)) |
                ((df['hour']>=hour+1) & (df['hour']<22)) |
                ((df['hour']>=0) & (df['hour'] <= 5))
            ), 1, 0))
        else:
            df = df.assign(eod=np.where((
                ((df['hour']==hour) & (df['minute']>=minute)) |
                ((df['hour']==4) & (df['minute']==45)) |
                ((df['hour']==4) & (df['minute']<60)) |
                ((df['hour']>=5) & (df['hour']<22)) |
                ((df['hour']==22) & (df['minute']<30)) |
                ((df['hour']>=hour+1) & (df['hour']<22)) |
                ((df['hour']>hour) & (df['hour'] <= 5))
            ), 1, 0))
        # df = df.loc[df['eod'] == 0]
        # df = df.assign(eod=np.where((
        #     ((df['hour']==4) & (df['minute']>=44)) |
        #     ((df['hour']>=0) & (df['hour']<22)) |
        #     ((df['hour']==23) & (df['minute']>59)) |
        #     ((df['hour']==22) & (df['minute']<30))
        # ), 1, 0))
        df = df.assign(sod=np.where(((df['hour']==22) & (df['minute']==30)), 1, 0))
        # df = df.assign(eod=np.where(((df['hour']==23) & (df['minute']==50)), 1, 0))
        closeArr = df['close'].tolist()
        emaDict = {}
        ema500 = EmaArr(closeArr, 500)
        df['ema500'] = ema500
        npArr = cleanData(df)
        tpVal = 1.022222222
        totalGain, totalLoss, trades, wr = backtest(npArr, tpVal)
        capital = totalGain+totalLoss
        rr = totalGain/-totalLoss
        riskOfRuin = calcRisk(rr,wr,100)
        if trades > 0 and capital > 2:
            profitPerTrade = capital/trades
            if profitPerTrade > maxProfitPerTrade:
                bestHour = hour
                bestMinute = minute
                maxCapital = capital
                maxProfitPerTrade = profitPerTrade
                maxRR = rr
                bestTpVal = tpVal
                minRiskOfRuin = riskOfRuin
                print(capital)
        tpVal += 0.01
    print(f"maxCapital {maxCapital} maxRR {maxRR} maxProfitPerTrade {maxProfitPerTrade} bestTpVal {bestTpVal} bestTime {bestHour}:{bestMinute} minRiskOfRuin {minRiskOfRuin}")
    return 0

GetBestMA('QQQ')