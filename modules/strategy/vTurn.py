import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr, EmaArr
from modules.permutationEntropy import permutation_entropy
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 14
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-3:][:,2])
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-3:][:,1])
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

def VTurn(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0

    
    # if len(pe) > 0:
    #     print(pe)
    #     sys.exit()
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 3:
        signal = 0
        topVol = classify_top_n_bars(npArr[:-1][-100:], 2)
        op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr)
        if (
            topVol > 0 and
            npArr[-2][2] < npArr[-3][2] and
            npArr[-2][5] > npArr[-3][5] * 1.2 and
            npArr[-2][4] / npArr[-2][5] > npArr[-3][4] / npArr[-3][5] * 1.05
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
            topVol < 0 and
            npArr[-2][1] > npArr[-3][1] and
            npArr[-2][5] > npArr[-3][5] * 1.2 and
            npArr[-2][4] / npArr[-2][5] > npArr[-3][4] / npArr[-3][5] * 1.05
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

def Sandwitch(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # sma = SmaArr(npArr[:,3][:-1], 50)
    # topVol = classify_top_n_bars(npArr[:-1][-100:], 2)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr)
    if (
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] > npArr[-2][0] and
        npArr[-2][1] < npArr[-3][0] and
        npArr[-2][2] > npArr[-3][2] and
        npArr[-2][5] < npArr[-3][5] * 0.9
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        return signal, op, sl, tp
    elif (
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-2][2] > npArr[-3][0] and
        npArr[-2][1] < npArr[-3][1] and
        npArr[-2][5] < npArr[-3][5] * 0.9
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
