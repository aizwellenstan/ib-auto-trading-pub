import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr, EmaArr
from modules.vwap import Vwap
from modules.strategy.sweep import GetSweep
from modules.trade.utils import floor_round, ceil_round

def getExpectRangeBko(npArr, period=20):
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

def get_signal(npArr, maxRangeLong, maxRangeShort, tick_val=0.25):
    signal = 0
    # breakout
    atrPeriod = 100
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][:,1][-2:]) - np.min(npArr[:-1][:,2][-2:]) > atr * 3:
        if (
            npArr[-2][2] < npArr[-3][2] and
            npArr[-2][3] > npArr[-3][1]
        ):  signal += 1
        elif (
            npArr[-2][1] > npArr[-3][1] and
            npArr[-2][3] < npArr[-3][2]
        ):  signal -= 1

    # hpOpeningRange
    if npArr[-3][4] > npArr[-4][4] * 4:
        high = npArr[-3][1]
        low = npArr[-3][2]
        if (
            npArr[-2][3] > high
        ):  signal += 1
        elif (
            npArr[-2][3] < low
        ): signal -= 1

    # hp
    ema = EmaArr(npArr[:-1][:,3][-9:], 8)
    if (
        npArr[-2][3] > ema[-1] and
        npArr[-2][1] > npArr[-3][1]
    ):  signal += 1
    elif (
        npArr[-2][3] < ema[-1] and
        npArr[-2][2] < npArr[-3][2]
    ):  signal -= 1

    if (
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] > npArr[-3][1]
    ):  signal += 1
    elif (
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] < npArr[-3][2]
    ):  signal -= 1

    # 4btp
    if (
        npArr[-5][3] < npArr[-5][0] and
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] > npArr[-2][0]
    ): signal += 1
    elif (
        npArr[-5][3] > npArr[-5][0] and
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0]
    ): signal -= 1

    if (
        npArr[-2][1] > npArr[-3][1] - tick_val * 7 and
        npArr[-2][1] < npArr[-3][1] - tick_val * 3
    ): signal += 1
    elif (
        npArr[-2][2] < npArr[-3][2] + tick_val * 7 and
        npArr[-2][2] > npArr[-3][2] + tick_val * 3
    ): signal -= 1

    if (
        npArr[-2][2] < npArr[-3][2] - tick_val * 2 and
        npArr[-2][2] > npArr[-3][2] - tick_val * 5
    ): signal += 1
    elif (
        npArr[-2][1] > npArr[-3][1] + tick_val * 2 and
        npArr[-2][1] < npArr[-3][1] + tick_val * 5
    ): signal -= 1

    if signal != 0:
        period = 5
        hh = np.max(npArr[-15:][:-3][:,1][-period:])
        ll = np.min(npArr[-15:][:-3][:,2][-period:])
        op = npArr[-2][3]
        if (
            npArr[-2][3] > hh and
            npArr[-2][2] > npArr[-3][2]
        ):
            tp = op + maxRangeLong
            sl = npArr[-2][2]
            if tp - op > (op - sl) * 1.6:
                expectMoveHigh, expectMoveLow = getExpectRangeBko(npArr[-15:][:-2], period)
                if expectMoveHigh > tick_val * 3 and expectMoveHigh > maxRangeLong:
                    signal += 1
        elif (
            npArr[-2][3] < ll and
            npArr[-2][1] < npArr[-3][1]
        ):
            tp = op - maxRangeShort
            sl = npArr[-2][1]
            if op - tp > (sl - op) * 1.6:
                expectMoveHigh, expectMoveLow = getExpectRangeBko(npArr[-15:][:-2], period)
                if expectMoveLow > tick_val * 3 and expectMoveLow < maxRangeShort:
                    signal -= 1

    if (
        npArr[-5][3] < npArr[-5][0] and
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0]
    ): 
        signal += 1
        if signal < 0: signal = 0
    elif (
        npArr[-5][3] > npArr[-5][0] and
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] > npArr[-2][0]
    ): 
        signal -= 1
        if signal > 0: signal = 0

    if signal != 0:
        open = 0
        close = 0
        for i in range(2, 19):
            if (
                abs(npArr[-i][3]-npArr[-i][0]) >
                abs(npArr[-i-1][3]-npArr[-i-1][0]) * 5
            ):  
                open = npArr[-i][0]
                close = npArr[-i][3]
                break
        if open > close:
            if signal < 0:
                if (
                    npArr[-2][0] < open and
                    npArr[-2][3] > close
                ): signal = 0
        if open < close:
            if signal > 0:
                if (
                    npArr[-2][0] > open and
                    npArr[-2][3] < close
                ): signal = 0

    return signal

def Combine(npArr, tf, tick_val=0.25):
    if (
        len(npArr) < 212 or npArr[-2][4] < 1 or 
        npArr[-2][5] < 1 or npArr[-3][5] < 1
    ):  return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 210, tick_val)
    p_signal = get_signal(npArr, maxRangeLong, maxRangeShort, tick_val)
    rrVal = 1.2
    rrMin = 2.6 # 1.6
    if abs(p_signal) >= 3: rrMin = 0.4
    IS_LONG = False
    IS_SHORT = False
    if not abs(p_signal) >= 3:
        if npArr[-2][5] < npArr[-3][5]:
            return 0, npArr[-1][0], 0, 0
        if maxRRLong > maxRRShort: IS_LONG = True
        elif maxRRShort > maxRRLong: IS_SHORT = True
    else:
        IS_LONG = True
        IS_SHORT = True
    if p_signal > 0 and IS_LONG:
        signal = 1
        tp = op + maxRangeLong + tick_val * 2
        sl = npArr[-2][2]
        slRange = op - sl
        if slRange > tick_val * 2:
            slippage = tick_val * 2
            rr = (tp - op - slippage) / (slRange + slippage)
            if rr > rrMin:
                if slRange > tick_val * 6:
                    sl += tick_val * 4
                elif slRange > tick_val * 5:
                    sl += tick_val * 3
                elif slRange > tick_val * 4:
                    sl += tick_val * 2
                elif slRange > tick_val * 3:
                    sl += tick_val
                if p_signal == 1:
                    sl = floor_round(op-(op-sl)/4, tick_val)
                if rr < rrVal:
                    tp = ceil_round(op + (op - sl) * rrVal, tick_val)
                if op - sl > tick_val * 2:
                    return signal, op, sl, tp
    elif p_signal < 0 and IS_SHORT:
        signal = -1
        tp = op - maxRangeShort - tick_val * 2
        sl = npArr[-2][1]
        slRange = sl - op
        if slRange > tick_val * 2:
            slippage = tick_val * 2
            rr = (op - tp - slippage) / (slRange + slippage)
            if rr > rrMin:
                if slRange > tick_val * 6:
                    sl += tick_val * 4
                elif slRange > tick_val * 5:
                    sl += tick_val * 3
                elif slRange > tick_val * 4:
                    sl -= tick_val * 2
                elif slRange > tick_val * 3:
                    sl -= tick_val
                if p_signal == -1:
                    sl = ceil_round(op+(sl-op)/4, tick_val)
                if rr < rrVal:
                    tp = floor_round(op - (sl - op) * rrVal, tick_val)
                if sl - op > tick_val * 2:
                    return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
