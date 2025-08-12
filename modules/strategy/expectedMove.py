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
from modules.kellyCriterion import GetKellyCriterion

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

import numpy as np

def getExpectRange(npArr, pinVar):
    max_high_movements = []
    max_low_movements = []

    # Loop through the array
    for i in range(1, len(npArr)):
        # Calculate the current bar's body size and its components
        close = npArr[i, 3]
        low = npArr[i, 2]
        high = npArr[i, 1]
        body_size = close - low if close > low else high - close
        
        # Check for bullish pin bar condition
        if high - close > pinVar * body_size:  # Bullish pin bar condition
            entry_price = close  # Entry price is the close of the pin bar
            stop_loss = low  # Set stop loss at the low of the pin bar
            max_movement = 0  # Initialize max movement for this signal
            
            for j in range(i + 1, len(npArr)):
                if npArr[j, 2] < stop_loss:
                    break  # Stop loss hit
                max_movement = max(max_movement, npArr[j, 1] - entry_price)  # Track max high after entry

            if max_movement > 0:
                max_high_movements.append(max_movement)  # Store the max movement for high breakouts

        # Check for bearish pin bar condition
        elif close - low > pinVar * body_size:  # Bearish pin bar condition
            entry_price = close  # Entry price is the close of the pin bar
            stop_loss = high  # Set stop loss at the high of the pin bar
            max_movement = 0  # Initialize max movement for this signal
            
            for j in range(i + 1, len(npArr)):
                if npArr[j, 3] > stop_loss:
                    break  # Stop loss hit
                max_movement = max(max_movement, entry_price - npArr[j, 2])  # Track max low after entry

            if max_movement > 0:
                max_low_movements.append(max_movement)  # Store the max movement for low breakouts

    # Determine the max chance to reach's range
    max_high_reach = max(max_high_movements) if max_high_movements else 0
    max_low_reach = max(max_low_movements) if max_low_movements else 0

    return max_high_reach, max_low_reach

def maxTpChance(npArr, r=2):
    # Initialize lists to track TPs for both long and short positions
    long_take_profit_targets = []
    short_take_profit_targets = []

    # Loop through each bar (starting from the second one)
    for i in range(1, npArr.shape[0]):
        # Long position calculations
        long_low = npArr[i-1, 2]  # Low of the previous bar
        long_close = npArr[i-1, 3]  # Close of the previous bar
        long_high = npArr[i, 1]  # High of the current bar

        # Calculate long stop loss and risk
        long_stop_loss = long_low
        long_r = long_close - long_stop_loss
        long_take_profit_target = long_stop_loss + r * long_r

        # Check if the long take profit target has not been reached
        if long_high < long_take_profit_target:
            if long_take_profit_target not in long_take_profit_targets:
                long_take_profit_targets.append(long_take_profit_target)
        else:
            # Remove the TP target if it has been reached
            if long_take_profit_target in long_take_profit_targets:
                long_take_profit_targets.remove(long_take_profit_target)

        # Short position calculations
        short_high = npArr[i-1, 1]  # High of the previous bar
        short_close = npArr[i-1, 3]  # Close of the previous bar
        short_low = npArr[i, 2]  # Low of the current bar

        # Calculate short stop loss and risk
        short_stop_loss = short_high
        short_r = short_stop_loss - short_close
        short_take_profit_target = short_stop_loss - r * short_r

        # Check if the short take profit target has not been reached
        if short_low > short_take_profit_target:  # Current low should be above the TP target
            if short_take_profit_target not in short_take_profit_targets:
                short_take_profit_targets.append(short_take_profit_target)
        else:
            # Remove the TP target if it has been reached
            if short_take_profit_target in short_take_profit_targets:
                short_take_profit_targets.remove(short_take_profit_target)

    # Calculate minimum difference among long TP targets
    min_diff_long_target = None
    if len(long_take_profit_targets) > 1:
        min_diff = float('inf')
        for tp in long_take_profit_targets:
            # Calculate differences to all other targets
            diffs = [abs(tp - other_tp) for other_tp in long_take_profit_targets if other_tp != tp]
            if diffs:
                current_min_diff = min(diffs)
                if current_min_diff < min_diff:
                    min_diff = current_min_diff
                    min_diff_long_target = tp
    else:
        min_diff_long_target = long_take_profit_targets[0] if long_take_profit_targets else None

    # Calculate minimum difference among short TP targets
    min_diff_short_target = None
    if len(short_take_profit_targets) > 1:
        min_diff = float('inf')
        for tp in short_take_profit_targets:
            # Calculate differences to all other targets
            diffs = [abs(tp - other_tp) for other_tp in short_take_profit_targets if other_tp != tp]
            if diffs:
                current_min_diff = min(diffs)
                if current_min_diff < min_diff:
                    min_diff = current_min_diff
                    min_diff_short_target = tp
    else:
        min_diff_short_target = short_take_profit_targets[0] if short_take_profit_targets else None

    # print(f"Valid Long Take Profit Targets (not hit): {long_take_profit_targets}")
    # print(f"Target with Minimum Difference for Long: {min_diff_long_target}")

    # print(f"Valid Short Take Profit Targets (not hit): {short_take_profit_targets}")
    # print(f"Target with Minimum Difference for Short: {min_diff_short_target}")
    return min_diff_long_target, min_diff_short_target

def ExpectedMove(npArr, tf, tick_val=0.25):
    if len(npArr) < 278 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0

    kellyCriterion = GetKellyCriterion(npArr[:-1][:,3])
    print(kellyCriterion)
    sys.exit()
    
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 1.5
    rrVal = 2
    backtestPeriod = 200
    
    if (
        npArr[-2][2] < npArr[-3][2] and
        npArr[-2][3] > npArr[-3][2]
    ):
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if tp - op > (op - sl) * rr:
            long_tp, short_tp = maxTpChance(npArr[:-2][-backtestPeriod:], rrVal)
            expected_move_high = long_tp - npArr[-2][3]
            expected_move_high = floor_round(expected_move_high, tick_val)
            expected_move_low = npArr[-2][3] - short_tp
            if expected_move_high > expected_move_low:
                if expected_move_high > tick_val * 3 and expected_move_high > maxRangeLong:
                    signal = 1
                    return signal, op, sl, tp
    elif (
        npArr[-2][1] > npArr[-3][1] and
        npArr[-2][3] < npArr[-3][1]
    ):
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if op - tp > (sl - op) * rr:
            long_tp, short_tp = maxTpChance(npArr[:-2][-backtestPeriod:], rrVal)
            expected_move_low = npArr[-2][3] - short_tp
            expected_move_low = floor_round(abs(expected_move_low), tick_val)
            expected_move_high = long_tp - npArr[-2][3]
            if expected_move_low > expected_move_high:
                if expected_move_low > tick_val * 3 and expected_move_low > maxRangeShort:
                    signal = -1
                    return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
