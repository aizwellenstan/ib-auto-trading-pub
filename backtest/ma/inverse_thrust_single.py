import sys 
mainFolder = '../../'
sys.path.append(mainFolder)
import pandas as pd
import os
from modules.movingAverage import EmaArr, SmaArr
import numpy as np
from modules.riskOfRuin import calcRisk
from ib_insync import *
ib = None
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
            contract, endDateTime='', durationStr='188 D',
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
    df = df[['open','high','low','close','eod']]
    # csvPath = './csv/1m/USD/NVDA.csv'
    # dfLog.to_csv(csvPath)
    npArr = df.to_numpy()
    return npArr

from numba import njit
tpVal = 1.022222222

# @njit
def checkCondition(position, npArr, i, condition, op, sl, tp, totalLoss, totalGain, loss, win):
    inTrade = 0
    if position > 0:
        if condition == 0:
            if npArr[i-1][1] > op + 0.01:
                if npArr[i-1][1] > tp:
                    totalGain += (tp-op)
                    win += 1
                else:
                    condition = 1
                    inTrade = 1
            else: 
                condition = 0
                inTrade = 1
            return inTrade, totalLoss, totalGain, loss, win, op, sl, tp, condition
        elif condition == 1:
            if npArr[i-1][2] < sl:
                totalLoss += (sl-op)
                loss += 1
            elif npArr[i-1][1] > tp: 
                totalGain += (tp-op)
                win += 1
            else:
                inTrade = 1
            return inTrade, totalLoss, totalGain, loss, win, op, sl, tp, condition
    else:
        if condition == 0:
            if npArr[i-1][2] < op - 0.01:
                if npArr[i-1][1] > tp:
                    totalGain += (op-tp)
                    win += 1
                else:
                    condition = 1
                    inTrade = 1
            else: 
                condition = 0
                inTrade = 1
            return inTrade, totalLoss, totalGain, loss, win, op, sl, tp, condition
        elif condition == 1:
            if npArr[i-1][1] > sl:
                totalLoss += (op-sl)
                loss += 1
            elif npArr[i-1][2] < tp: 
                totalGain += (op-tp)
                win += 1
            else:
                inTrade = 1
            return inTrade, totalLoss, totalGain, loss, win, op, sl, tp, condition  

# @njit
def checkOP(npArr, i, bar, trades, pinBarVal):
    longOP = 0
    longSL = 0
    longTP = 0
    shortOP = 0
    shortSL = 0
    shortTP = 0
    highArrAll = np.empty(0)
    lowArrAll = np.empty(0)

    for j in range(1, bar*3+1):
        highArrAll = np.append(highArrAll,npArr[i-j][1])
        lowArrAll = np.append(lowArrAll,npArr[i-j][2])

    highSigArr1 = np.empty(0)
    highSigArr2 = np.empty(0)
    lowSigArr1 = np.empty(0)
    lowSigArr2 = np.empty(0)

    for j in range(1, bar+1):
        lowSigArr1 = np.append(lowSigArr1,npArr[i-j][2])
        lowSigArr2 = np.append(lowSigArr2,npArr[i-j-bar][2])
        highSigArr1 = np.append(highSigArr1,npArr[i-j][1])
        highSigArr2 = np.append(highSigArr2,npArr[i-j-bar][1])

    high1 = highSigArr1.max()
    high2 = highSigArr2.max()
    low1 = lowSigArr1.min()
    low2 = lowSigArr2.min()

    if (
        high1 - npArr[i-1][3] / (high1-low1) > pinBarVal
    ):
        # lowSigArr1 = np.empty(0)
        # lowSigArr2 = np.empty(0)
        
        # for j in range(1, bar+1):
        #     lowSigArr1 = np.append(lowSigArr1,npArr[i-j][2])
        #     lowSigArr2 = np.append(lowSigArr2,npArr[i-j-bar][2])

        trades += 1
        op = highArrAll.max()
        sl = lowArrAll.min()
        tp = op + (op-sl) * tpVal
        longOP = op
        longSL = sl
        longTP = tp
    
    elif (
        npArr[i-1][3] - low1 / (high1-low1) > pinBarVal
    ):
        # highSigArr1 = np.empty(0)
        # highSigArr2 = np.empty(0)
        
        # for j in range(1, bar+1):
        #     highSigArr1 = np.append(highSigArr1,npArr[i-j][1])
        #     highSigArr2 = np.append(highSigArr2,npArr[i-j-bar][1])

        trades += 1
        op = lowArrAll.min()
        sl = highArrAll.max()
        tp = op - (sl-op) * tpVal
        shortOP = op
        shortSL = sl
        shortTP = tp
    return trades, longOP, longSL, longTP, shortOP, shortSL, shortTP

def backtest(npArr, bar, pinBarVal):
    totalGain = 0
    totalLoss = 0
    win = 0
    loss = 0
    trades = 0
    longTrades = []
    shortTrades = []
    for i in range(2, len(npArr)):
        eod = npArr[i][4]

        if eod > 0:
            eodPrice = npArr[i][0]
            if len(longTrades) > 0:
                for op, sl, tp, condition in longTrades:
                    if condition == 1:
                        profit = eodPrice - op
                        if profit < 0:
                            totalLoss += profit
                            loss += 1
                        else:
                            totalGain += profit
                            win += 1
                longTrades = []
            if len(shortTrades) > 0:
                for op, sl, tp, condition in shortTrades:
                    if condition == 1:
                        profit = op - eodPrice
                        if profit < 0:
                            totalLoss += profit
                            loss += 1
                        else:
                            totalGain += profit
                            win += 1
                shortTrades = []
            continue

        if len(longTrades) > 0:
            newLongTrades = []
            for op, sl, tp, condition in longTrades:
                inTrade, totalLoss, totalGain, loss, win, op, sl, tp, condition = checkCondition(1, npArr, i, condition, op, sl, tp, totalLoss, totalGain, loss, win)
                if inTrade > 0:
                    newLongTrades.append((op, sl, tp, condition))
            longTrades = newLongTrades

        if len(shortTrades) > 0:
            newShortTrades = []
            for op, sl, tp, condition in shortTrades:
                inTrade, totalLoss, totalGain, loss, win, op, sl, tp, condition = checkCondition(-1, npArr, i, condition, op, sl, tp, totalLoss, totalGain, loss, win)
                if inTrade > 0:
                    newShortTrades.append((op, sl, tp, condition))
            shortTrades = newShortTrades

        # if len(longTrades) > 0:
        #     newLongTrades = []
        #     for op, sl, tp, condition in longTrades:
        #         if condition == 0:
        #             if npArr[i-1][1] > op + 0.01:
        #                 if npArr[i-1][1] > tp:
        #                     totalGain += (tp-op)
        #                     win += 1
        #                 else:
        #                     condition = 1
        #                     newLongTrades.append((op, sl, tp, condition))
        #         if condition == 1:
        #             if npArr[i-1][2] < sl + 0.01:
        #                 totalLoss += (sl-op)
        #                 loss += 1
        #             elif npArr[i-1][1] > tp: 
        #                 totalGain += (tp-op)
        #                 win += 1
        #             else:
        #                 newLongTrades.append((op, sl, tp, condition))
        #     longTrades = newLongTrades

        # if len(shortTrades) > 0:
        #     newShortTrades = []
        #     for op, sl, tp, condition in shortTrades:
        #         if condition == 0:
        #             if npArr[i-1][2] < op:
        #                 if npArr[i-1][2] < tp:
        #                     totalGain += (op-tp)
        #                     win += 1
        #                 else:
        #                     condition = 1
        #                     newShortTrades.append((op, sl, tp, condition))
        #         if condition == 1:
        #             if npArr[i-1][1] > sl:
        #                 totalLoss += (op-sl)
        #                 loss += 1
        #             elif npArr[i-1][2] < tp: 
        #                 totalGain += (op-tp)
        #                 win += 1
        #             else:
        #                 newShortTrades.append((op, sl, tp, condition))
        #     shortTrades = newShortTrades
        
        trades,longOP,longSL,longTP,shortOP,shortSL,shortTP = checkOP(npArr, i, bar,trades, pinBarVal)
        if longOP > 0:
            longTrades.append((longOP,longSL,longTP,0))
        elif shortOP > 0:
            shortTrades.append((shortOP,shortSL,shortTP,0))
        # if (
        #     npArr[i-bar*3][3] < npArr[i-bar*3-1][0] and
        #     npArr[i-bar*2][3] > npArr[i-bar*2-1][0] and
        #     npArr[i-bar][3] > npArr[i-bar-1][0]
        # ):
        #     lowSigArr1 = np.empty(0)
        #     lowSigArr2 = np.empty(0)
            
        #     for j in range(1, bar+1):
        #         lowSigArr1 = np.append(lowSigArr1,npArr[i-j][2])
        #         lowSigArr2 = np.append(lowSigArr2,npArr[i-j-bar][2])

        #     if lowSigArr1.min() > lowSigArr2.min():
        #         trades += 1
        #         highArr = np.array(
        #             [npArr[i-bar*3][1], npArr[i-bar*2][1], npArr[i-bar][1]]
        #         )
        #         lowArr = np.array(
        #             [npArr[i-bar*3][2], npArr[i-bar*2][2], npArr[i-bar][2]]
        #         )
        #         op = highArr.max()
        #         sl = lowArr.min()
        #         tp = op + (op-sl) * tpVal
        #         longTrades.append((op,sl,tp,0))
        
        # elif (
        #     npArr[i-bar*3][3] > npArr[i-bar*3-1][0] and
        #     npArr[i-bar*2][3] < npArr[i-bar*2-1][0] and
        #     npArr[i-bar][3] < npArr[i-bar-1][0]
        # ):
        #     highSigArr1 = np.empty(0)
        #     highSigArr2 = np.empty(0)
            
        #     for j in range(1, bar+1):
        #         highSigArr1 = np.append(highSigArr1,npArr[i-j][1])
        #         highSigArr2 = np.append(highSigArr2,npArr[i-j-bar][1])

        #     if highSigArr1.max() < highSigArr2.max():
        #         trades += 1
        #         highArr = np.array(
        #             [npArr[i-bar*3][1], npArr[i-bar*2][1], npArr[i-bar][1]]
        #         )
        #         lowArr = np.array(
        #             [npArr[i-bar*3][2], npArr[i-bar*2][2], npArr[i-bar][2]]
        #         )
        #         op = lowArr.min()
        #         sl = highArr.max()
        #         tp = op - (sl-op) * tpVal
        #         shortTrades.append((op,sl,tp,0))

    totalLoss -= 1
    wr = 0
    if win+loss > 0:
        wr = win/(win+loss)
    else: wr = 0
    # print(wr)
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
    bestBar = 0
    maxProfitPerTrade = 0
    minRiskOfRuin = 9999
    maxPinBarVal = 1
    hour = 4
    minute = 44
    hour = 22
    minute = 57
    # while hour <= 4 or hour >= 22:
    #     if hour == 22 and minute < 32: break
    #     if hour == 0 and minute == 0: 
    #         hour = 23
    #         minute = 60
    #     if minute > 0:
    #         minute -= 1
    #     else:
    #         hour -= 1
    #         minute = 59
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
    npArr = cleanData(df)

    bar = 1
    bar = 5
    # while bar < 31:
    pinBarVal = 1
    # while pinBarVal > 0.05:
    totalGain, totalLoss, trades, wr = backtest(npArr, bar, pinBarVal)
    capital = totalGain+totalLoss
    print(capital)
    rr = totalGain/-totalLoss
    if rr > 1:
        riskOfRuin = calcRisk(rr,wr,100)
        if trades > 0 and capital > 2:
            profitPerTrade = capital/trades
            if riskOfRuin < minRiskOfRuin:
                if profitPerTrade > maxProfitPerTrade:
                    bestHour = hour
                    bestMinute = minute
                    maxCapital = capital
                    maxProfitPerTrade = profitPerTrade
                    if rr < capital:
                        maxRR = rr
                    bestTpVal = tpVal
                    if riskOfRuin > 0:
                        minRiskOfRuin = riskOfRuin
                    bestBar = bar
                    maxPinBarVal = pinBarVal
                    print(capital)
        # pinBarVal -= 0.05
                    # if rr > maxRR:
                    #     bestHour = hour
                    #     bestMinute = minute
                    #     maxCapital = capital
                    #     maxProfitPerTrade = profitPerTrade
                    #     if rr < capital:
                    #         maxRR = rr
                    #     bestTpVal = tpVal
                    #     if riskOfRuin > 0:
                    #         minRiskOfRuin = riskOfRuin
                    #     bestBar = bar
                    #     print(capital)
            # bar += 1
    print(f"maxCapital {maxCapital} maxRR {maxRR} maxProfitPerTrade {maxProfitPerTrade} bestTpVal {bestTpVal} bestTime {bestHour}:{bestMinute} minRiskOfRuin {minRiskOfRuin} bestBar {bestBar} maxPinBarVal {maxPinBarVal}")
    return 0

GetBestMA('QQQ')