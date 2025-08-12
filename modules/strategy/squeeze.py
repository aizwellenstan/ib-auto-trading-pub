import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr, EmaArr
from modules.strategy.sweep import GetSweep
from modules.supertrendV2 import supertrend

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 5
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-4:][:,2])
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-4:][:,1])
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def classify_top_n_bars(npArr, n):
    # Create a mask for bars where close is not equal to open
    mask = npArr[:, 3] != npArr[:, 0]
    
    # Filter the array based on the mask
    filtered_arr = npArr[mask]
    
    # Sort the filtered array by volume in descending order
    sorted_arr = filtered_arr[np.argsort(filtered_arr[:, 4])[::-1]]
    
    # Get the top n rows
    top_n_arr = sorted_arr[:n]
    
    # Check conditions for the top n rows
    if np.all(top_n_arr[:, 3] > top_n_arr[:, 0]):
        return 1
    elif np.all(top_n_arr[:, 3] < top_n_arr[:, 0]):
        return -1
    else:
        return 0

def Supertrend(npArr, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    supertrendDir = supertrend(npArr[:-1][-11:], 10, 3)
    # squeeze_on = squeeze(npArr[:-1][-20:])
    # if squeeze_on:
    if (
        supertrendDir > 0 and
        npArr[-2][1] > npArr[-3][1] and
        npArr[-3][3] > npArr[-3][0]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        supertrendDir < 0 and
        npArr[-2][2] < npArr[-3][2] and
        npArr[-3][3] < npArr[-3][0]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
