import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr, EmaArr
from modules.entropy import Entropy
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 6.972
    # TP_VAL = 1.33
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-2:][:,2])
        tp = op + (op-sl) * TP_VAL
        # sl = np.min(npArr[-4:][:,2]) - tick_val * 140
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-2:][:,1])
        tp = op - (sl-op) * TP_VAL
        # sl = np.max(npArr[-4:][:,1]) + tick_val * 140
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def ReverseIrb(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    ema20 = EmaArr(npArr[:-1][:,3][-20:], 20)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2
    if (
        npArr[-2][2] > ema20[-1] and
        min(npArr[-2][0], npArr[-2][3]) - npArr[-2][2] >
        (npArr[-2][1] - npArr[-2][2]) * 0.45 and
        npArr[-2][5] < npArr[-3][5]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-2][1] < ema20[-1] and
        npArr[-2][1] -  max(npArr[-2][0], npArr[-2][3])>
        (npArr[-2][1] - npArr[-2][2]) * 0.45 and
        npArr[-2][5] < npArr[-3][5]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def Irb(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    ema20 = EmaArr(npArr[:-1][:,3][-20:], 20)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2
    periodEnd = 14
    if (
        npArr[-2][5] > npArr[-3][5] and
        npArr[-2][4] / npArr[-2][5] > npArr[-3][4] / npArr[-3][5]
    ):
        if (
            npArr[-2][2] > ema20[-1] and 
            not (npArr[-2][3] > np.max(npArr[:-2][-13:][:,1]))
        ):
            for i in range(3, periodEnd):
                if npArr[-i][1] - npArr[-i][2] > 0:
                    if (
                        (
                            npArr[-i][1] - 
                            max(npArr[-i][0], npArr[-i][3])
                        ) / (npArr[-i][1] - npArr[-i][2]) >= 0.45
                    ):
                        if npArr[-2][1] > npArr[-i][1]:
                            signal = 1
                            tp = op + maxRangeLong
                            sl = npArr[-2][2]
                            if op - sl > tick_val * 2:
                                slippage = tick_val * 2
                                if (tp - op - slippage) / (op - sl + slippage) > rr:
                                    return signal, op, sl, tp
        if (
            npArr[-2][1] < ema20[-1] and 
            not (npArr[-2][3] < np.min(npArr[:-2][-13:][:,2]))
        ):
            for i in range(3, periodEnd):
                if npArr[-i][1] - npArr[-i][2] > 0:
                    if (
                        (
                            min(npArr[-i][0], npArr[-i][3]) - npArr[-i][2]
                        ) / (npArr[-i][1] - npArr[-i][2]) >= 0.45
                    ):
                        if npArr[-2][2] < npArr[-i][2]:
                            signal = -1
                            tp = op - maxRangeShort
                            sl = npArr[-2][1]
                            if sl - op > tick_val * 2:
                                slippage = tick_val * 2
                                if (op - tp - slippage) / (sl - op + slippage) > rr:
                                    return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def getExpectRange(npArr, period=20):
    max_high_movements = []
    max_low_movements = []

    # Loop through the array
    for i in range(period, len(npArr)):
        # Calculate the highest high and lowest low of the period
        high_period = np.max(npArr[i - period:i, 1])  # High column
        low_period = np.min(npArr[i - period:i, 2])   # Low column

        # Check for breakout above high (Long signal)
        if npArr[i, 3] > high_period:  # If current close is above period high
            entry_price = npArr[i, 3]  # Entry price is the close of the breakout candle
            stop_loss = npArr[i, 2]  # Set stop loss at the low of the breakout candle
            max_movement = 0  # Initialize max movement for this signal
            highest_after_entry = entry_price  # Start from the entry price
            
            for j in range(i + 1, len(npArr)):
                if npArr[j, 3] < stop_loss:
                    break  # Stop loss hit
                highest_after_entry = max(highest_after_entry, npArr[j, 1])  # Track max high after entry
                movement = highest_after_entry - entry_price  # Calculate difference
                max_movement = max(max_movement, movement)  # Track max movement

            if max_movement > 0:
                max_high_movements.append(max_movement)  # Store the max movement for high breakouts

        # Check for breakout below low (Short signal)
        elif npArr[i, 3] < low_period:  # If current close is below period low
            entry_price = npArr[i, 3]  # Entry price is the close of the breakout candle
            stop_loss = npArr[i, 1]  # Set stop loss at the high of the breakout candle
            max_movement = 0  # Initialize max movement for this signal
            lowest_after_entry = entry_price  # Start from the entry price
            
            for j in range(i + 1, len(npArr)):
                if npArr[j, 3] > stop_loss:
                    break  # Stop loss hit
                lowest_after_entry = min(lowest_after_entry, npArr[j, 2])  # Track min low after entry
                movement = entry_price - lowest_after_entry  # Calculate difference
                max_movement = max(max_movement, movement)  # Track max movement

            if max_movement > 0:
                max_low_movements.append(max_movement)  # Store the max movement for low breakouts

    # Determine the max chance to reach's range
    max_high_reach = max(max_high_movements) if max_high_movements else 0
    max_low_reach = max(max_low_movements) if max_low_movements else 0

    return max_high_reach, max_low_reach

def RangeBreak(npArr, tf, tick_val=0.25):
    if len(npArr) < 278 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    # rr = 2
    # period = 89
    op = npArr[-2][3]
    # sample = npArr[:-2]
    # maxVolIdx = np.argmax(sample[:,4])
    # sample = sample[maxVolIdx-89:maxVolIdx][-period:]
    # if len(sample) < 1: return 0, npArr[-1][0], 0, 0
    # for period in (4, ,)
    rr = 1.6
    period = 5
    npArr = npArr[-15:]
    hh = np.max(npArr[:-3][:,1][-period:])
    ll = np.min(npArr[:-3][:,2][-period:])
    if (
        npArr[-2][3] > hh and
        npArr[-2][2] > npArr[-3][2]
    ):
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if tp - op > (op - sl) * rr:
            expectMoveHigh, expectMoveLow = getExpectRange(npArr[:-2], period)
            if expectMoveHigh > tick_val * 3 and expectMoveHigh > maxRangeLong:
                expectMoveHigh -= tick_val
                signal = 1
                return signal, op, sl, tp
    elif (
        npArr[-2][3] < ll and
        npArr[-2][1] < npArr[-3][1]
    ):
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if op - tp > (sl - op) * rr:
            expectMoveHigh, expectMoveLow = getExpectRange(npArr[:-2], period)
            if expectMoveLow > tick_val * 3 and expectMoveLow < maxRangeShort:
                expectMoveLow -= tick_val
                signal = -1
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def FourBarTurn(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2
    if (
        # npArr[-2][1] < npArr[-6][2] and
        npArr[-2][1] > npArr[-5][2] and
        npArr[-4][2] < npArr[-5][2] and
        npArr[-3][2] < npArr[-4][2]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif(
        # npArr[-2][2] > npArr[-6][1] and
        npArr[-2][2] < npArr[-5][1] and
        npArr[-4][1] > npArr[-5][1] and
        npArr[-3][1] > npArr[-4][1]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def LiquidityGrab(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr[:-5], 30, tick_val)
    shortTp = op - maxRangeShort
    longTp = op + maxRangeLong
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2
    if (
        npArr[-3][3] < shortTp and
        npArr[-4][3] < npArr[-4][0] and
        # npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] > npArr[-2][0] and
        npArr[-2][1] >= npArr[-4][2]
        
        # npArr[-3][3] < np.min(npArr[:-4][-13:][:,2]) and
        # npArr[-3][4] > npArr[-5][4] and
        # npArr[-3][4] > npArr[-4][4] and
        # npArr[-3][0] - npArr[-3][3] > 
        # (
        #     abs(npArr[-5][3] - npArr[-5][0]) +
        #     abs(npArr[-4][3] - npArr[-4][0])
        # ) and
        # npArr[-2][2] < npArr[-3][2] and
        # npArr[-2][3] > npArr[-2][0]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    if (
        npArr[-3][3] > longTp and
        npArr[-4][3] > npArr[-4][0] and
        # npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-2][2] >= npArr[-4][1]
        # npArr[-3][3] > np.max(npArr[:-4][-13:][:,1]) and
        # npArr[-3][4] > npArr[-5][4] and
        # npArr[-3][4] > npArr[-4][4] and
        # npArr[-3][3] - npArr[-3][0] > 
        # (
        #     abs(npArr[-5][3] - npArr[-5][0]) +
        #     abs(npArr[-4][3] - npArr[-4][0])
        # ) and
        # npArr[-2][1] > npArr[-3][1] and
        # npArr[-2][3] < npArr[-2][0]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

# def Signal(df, trade=0):
#     try:
#         closeArr = []
#         dfClose = df.loc[:, 'close']
#         for close in dfClose:
#             closeArr.append(close)
#         ema9 = Ema(closeArr, 9)
#         ema21 = Ema(closeArr, 21)
#         ema100 = Ema(closeArr, 100)
#         ema500 = Ema(closeArr, 500)
#         df['ema9'] = ema9
#         df['ema21'] = ema21
#         df['ema100'] = ema100
#         df['ema500'] = ema500
#         df = df[['open','high','low','close','ema9','ema21','ema100','ema500']]
#         npArr = df.to_numpy()

#         close1 = npArr[-2][3]
#         open0 = npArr[-1][0]
#         high = npArr[-1][1]
#         low = npArr[-1][2]
#         close = npArr[-1][3]
#         ema9 = npArr[-1][4]
#         ema21 = npArr[-1][5]
#         ema100 = npArr[-1][6]
#         ema500 = npArr[-1][7]

#         # signal
#         # 1 buy
#         # -1 sell
#         # -2 sl
#         # 2 tp
#         signal = 0

#         isTP = False
#         if trade > 0:
#             bias100 = (high-ema100)/ema100
#             if bias100 > tpBiasLimit100:
#                 signal = 2
#                 return signal
#             bias500 = (high-ema500)/ema500
#             if bias500 > tpBiasLimit500:
#                 signal = 2
#                 return signal
#         elif trade < 0:
#             bias100 = (low-ema100)/ema100
#             if bias100 < - tpBiasLimit100:
#                 signal = 2
#                 return signal
#             bias500 = (low-ema500)/ema500
#             if bias500 < - tpBiasLimit500:
#                 signal = 2
#                 return signal

#         if (
#             (close1 < ema21 and close > ema21) or
#             (close1 > ema21 and close < ema21) or
#             (open0 < ema21 and close > ema21) or
#             (open0 > ema21 and close < ema21)
#         ):
#             signal = -2
#             return signal

#         bias = abs(close-ema500)/ema500
#         if (
#             (
#                 close1 < ema21 and close > ema21 and
#                 close1 < ema9 and close > ema9 and bias > addBiasLimit
#             ) or
#             (
#                 open0 < ema21 and close > ema21 and
#                 open0 < ema9 and close > ema9 and bias > addBiasLimit
#             ) and
#             close < ema500
#         ):
#             signal = 1
#             return signal
#         elif (
#             (
#                 close1 > ema21 and close < ema21 and
#                 close1 > ema9 and close < ema9
#             ) or
#             (
#                 open0 > ema21 and close < ema21 and
#                 open0 > ema9 and close < ema9
#             ) and
#             close > ema500
#         ):
#             signal = -1
#             return signal

#         print(f"isTP {isTP}")
#         if ema9 > ema21:
#             if close > ema21 and (close < ema9 or open0 < ema9) and bias > addBiasLimit:
#                 signal = 1
#                 return signal
#         else:
#             if close < ema21 and (close > ema9 or open0 > ema9) and bias > addBiasLimit:
#                 signal = -1
#                 return signal
        
#         return 0

def EmaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # if len(npArr) < 501 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
    #     return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
    ema9 = EmaArr(npArr[:-1][-10:][:,3], 6)
    ema21 = EmaArr(npArr[:-1][-22:][:,3], 21)
    # ema500 = EmaArr(npArr[:-1][-501:][:,3], 500)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 5, tick_val)
    rr = 2
    # addBiasLimit = 0.002640450764
    # bias = abs(npArr[-2][3]-ema500[-1])/ema500[-1]
    if (
        npArr[-3][3] < ema9[-2] and
        npArr[-2][3] > ema9[-1]

        # ema9[-1] < ema21[-1] and
        # npArr[-2][3] < ema21[-1] and
        # npArr[-2][3] > ema9[-1]
    ):
        signal = 1
        tp = op + maxRangeLong
        # sl = npArr[-2][2]
        sl = floor_round((npArr[-2][2] + op) / 2, tick_val)
        slippage = tick_val * 2
        if (tp - op - slippage) / (op - sl + slippage) > rr:
            if op - sl < tick_val * 2:
                sl = op - tick_val * 2
            return signal, op, sl, tp
    elif (
        npArr[-3][3] > ema9[-2] and
        npArr[-2][3] < ema9[-1]

        # ema9[-1] > ema21[-1] and
        # npArr[-2][3] > ema21[-1] and
        # npArr[-2][3] < ema9[-1]
    ):
        signal = -1
        tp = op - maxRangeShort
        # sl = npArr[-2][1]
        sl = ceil_round((npArr[-2][2] + op) / 2, tick_val)
        slippage = tick_val * 2
        if (op - tp - slippage) / (sl - op + slippage) > rr:
            if sl - op < tick_val * 2:
                sl = op + tick_val * 2
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SmaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    sma10 = SmaArr(npArr[:-1][-11:][:,3], 10)
    sma25 = SmaArr(npArr[:-1][-26:][:,3], 25)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        sma10[-1] > sma25[-1] and
        npArr[-2][1] > npArr[-3][1]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        sma10[-1] < sma25[-1] and
        npArr[-2][2] < npArr[-3][2]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def Ma(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        sma100 = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] > sma100[-1]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            npArr[-3][3] < sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def ExtremeHighLow(npArr, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    period = 3
    rr = 2.1
    maHigh = EmaArr(npArr[:-1][:,1][-period-1:], period)
    maLow = EmaArr(npArr[:-1][:,2][-period-1:], period)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    crange = npArr[-2][1] - npArr[-2][2]
    if (
        npArr[-2][3] > maHigh[-1] and
        (npArr[-2][1] - npArr[-2][3]) / crange < 0.55
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-2][3] < maLow[-1] and
        (npArr[-2][3] - npArr[-2][2]) / crange < 0.55
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def DynamicExtremeHighLow(npArr, tf, tick_val=0.25):
    if len(npArr) < 289 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    period = 3
    for i in range(3, 80):
        if npArr[-i][5] > npArr[-i-1][5] * 6: 
            period = i
            break
    rr = 2.5
    maHigh = EmaArr(npArr[:-1][:,1][-period-1:], period)
    maLow = EmaArr(npArr[:-1][:,2][-period-1:], period)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, period, tick_val)
    crange = npArr[-2][1] - npArr[-2][2]
    if (
        npArr[-2][3] > maHigh[-1] and
        (npArr[-2][1] - npArr[-2][3]) / crange < 0.55
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-2][3] < maLow[-1] and
        (npArr[-2][3] - npArr[-2][2]) / crange < 0.55
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

# 15 mins 20 mins
def MaCrossHTF(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        sma100 = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-3][3] < sma100[-2] and
            npArr[-2][3] > sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SimpleMaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
        sma10 = SmaArr(npArr[:-1][:,3], 10)
        sma25 = SmaArr(npArr[:-1][:,3], 25)
        op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr)
        if (
            (sma10[-2] < sma25[-2] and
            sma10[-1] > sma25[-1]) or
           (sma10[-1] < sma25[-1] and
            npArr[-2][3] > sma25[-1] and
            npArr[-2][3] > sma10[-1])
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = 1
            # op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            tp = op + maxRangeLong
            sl = npArr[-2][2]
            return signal, op, sl, tp
        elif (
            (sma10[-2] > sma25[-2] and
            sma10[-1] < sma25[-1]) or
            (sma10[-1] > sma25[-1] and
            npArr[-2][3] < sma25[-1] and
            npArr[-2][3] < sma10[-1])
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = -1
            # op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            tp = op - maxRangeShort
            sl = npArr[-2][1]
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OriSimpleMaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['5 mins']: atrPeriod = 7
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 6)
    # if atr > 2: return 0, npArr[-1][0], 0, 0
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
    sma10 = SmaArr(npArr[:-1][:,3], 11)
    sma25 = SmaArr(npArr[:-1][:,3], 25)
    if (
        sma10[-2] < sma25[-2] and
        sma10[-1] > sma25[-1] and not
        (
            npArr[-3][4] > npArr[-4][4] * 2 and
            npArr[-2][4] > npArr[-4][4] * 2
        )
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        sma10[-2] > sma25[-2] and
        sma10[-1] < sma25[-1] and not
        (
            npArr[-3][4] > npArr[-4][4] * 2 and
            npArr[-2][4] > npArr[-4][4] * 2
        )
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SmaFr(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 6)
    # if atr > 2: return 0, npArr[-1][0], 0, 0
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    sma100 = SmaArr(npArr[:-1][:,3], 100)
    sma25 = SmaArr(npArr[:-1][:,3], 25)
    sma10 = SmaArr(npArr[:-1][:,3], 10)
    if (
        npArr[-2][3] > sma100[-1] and
        npArr[-2][3] < sma25[-1] and
        npArr[-2][3] < sma10[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    elif (
        npArr[-2][3] < sma100[-1] and
        npArr[-2][3] > sma25[-1] and
        npArr[-2][3] > sma10[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SimpleMaCrossOver(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    sma10 = SmaArr(npArr[:-1][:,3][-11:], 10)
    sma25 = SmaArr(npArr[:-1][:,3][-26:], 25)
    if (
        sma10[-2] < sma25[-2] and
        sma10[-1] > sma25[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        sma10[-2] > sma25[-2] and
        sma10[-1] < sma25[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SmaSR(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    sma75 = SmaArr(npArr[:-1][:,3][-201:], 200)
    if (
        npArr[-2][2] < sma75[-1] and
        npArr[-2][3] > sma75[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        npArr[-2][1] > sma75[-1] and
        npArr[-2][3] < sma75[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def calculate_z_score(npArr, period=200):
    # Ensure npArr is a NumPy array
    npArr = np.array(npArr)

    # Extract Open, High, Low, and Close columns
    Open, High, Low, Close = npArr[:, 0], npArr[:, 1], npArr[:, 2], npArr[:, 3]

    # Calculate the rolling standard deviation of the Close prices
    def rolling_std(arr, period):
        return np.convolve(arr, np.ones(period)/period, mode='valid')

    # Calculate True Range (TR)
    def true_range(high, low, prev_close):
        return np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    
    # Calculate ATR
    def average_true_range(tr, period):
        return np.convolve(tr, np.ones(period)/period, mode='valid')

    # Calculate the standard deviation
    std_close = rolling_std(Close, period)
    
    # Calculate True Range (TR)
    prev_close = np.roll(Close, shift=1)
    prev_close[0] = Close[0]  # Handle the first value which does not have a previous close
    tr = true_range(High, Low, prev_close)
    
    # Calculate ATR
    atr = average_true_range(tr, period)
    
    # Extend std_close and atr to match length for subtraction
    std_close = std_close[:len(atr)]  # Trim std_close to the length of atr
    
    # Calculate the difference between standard deviation and ATR
    diff = std_close - atr
    
    # Calculate the mean and standard deviation of the difference
    diff_mean = np.mean(diff)
    diff_std = np.std(diff)
    
    # Calculate Z-score
    z_score = (diff - diff_mean) / diff_std
    
    return z_score

def Ma50ma200cross(npArr, tf, tick_val=0.25):
    if len(npArr) < 202:
        return 0, npArr[-1][0], 0, 0
    z_score = calculate_z_score(npArr[:-1])
    if z_score[-1] < -0.38:
        sma50 = SmaArr(npArr[:-1][:,3][-51:], 10)
        sma200 = SmaArr(npArr[:-1][:,3][-201:], 25)
        if (
            sma50[-2] < sma200[-2] and
            sma50[-1] > sma200[-1]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            sma50[-2] > sma200[-2] and
            sma50[-1] < sma200[-1]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0