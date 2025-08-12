import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.movingAverage import SmaArr
from modules.atr import ATR
from modules.permutationEntropy import permutation_entropy
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 5
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

def ob_coord(use_max, loc, npArr, i):
    ob_btm = float('inf')
    ob_top = float('-inf')

    for j in range(max(loc + 1, 21), i):
        if use_max:
            if npArr[j, 1] > ob_top and npArr[j][3] < npArr[j][0]:
            # if npArr[j, 3] > ob_top:
                ob_top = npArr[j, 1]
                ob_btm = npArr[j, 2] if ob_top == npArr[j, 1] else ob_btm
        else:
            if npArr[j, 2] < ob_btm and npArr[j][3] > npArr[j][0]:
            # if npArr[j, 3] < ob_btm:
                ob_btm = npArr[j, 2]
                ob_top = npArr[j, 1] if ob_btm == npArr[j, 2] else ob_top

    return ob_btm, ob_top

def ob(npArr, length=50):
    bull_ob_btm = bull_ob_top = bear_ob_btm = bear_ob_top = 0
    top_cross = btm_cross = False
    top_y = btm_y = None
    top_x = btm_x = 0

    os = np.zeros(npArr.shape[0])
    top = np.zeros(npArr.shape[0])
    btm = np.zeros(npArr.shape[0])

    for i in range(length, len(npArr)):
        upper = np.max(npArr[i-length:i, 1])
        lower = np.min(npArr[i-length:i, 2])

        if npArr[i-length-1, 1] > upper:
            os[i-1] = 0
        elif npArr[i-length-1, 2] < lower:
            os[i-1] = 1
        else:
            os[i-1] = os[i-2]

        if os[i-1] == 0 and os[i-2] != 0:
            top[i-1] = npArr[i-length-1, 1]
        if os[i-1] == 1 and os[i-2] != 1:
            btm[i-1] = npArr[i-length-1, 2]

        if top[i-1]:
            top_cross = True
            top_y = top[i-1]
            top_x = i - length - 1
        if btm[i-1]:
            btm_cross = True
            btm_y = btm[i-1]
            btm_x = i - length - 1
        
        if top_cross and npArr[i, 3] > top_y:
            bull_ob_btm, bull_ob_top = ob_coord(False, top_x, npArr, i)
            top_cross = False
        
        if btm_cross and npArr[i, 3] < btm_y:
            bear_ob_btm, bear_ob_top = ob_coord(True, btm_x, npArr, i)
            btm_cross = False

    # Return only the last values
    return bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top

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
    
def ObFiveMin(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # sma = SmaArr(npArr[:,3][:-1], 50)
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-4:][:,1]) - np.min(npArr[-4:][:,2]) > atr * 2:
        bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top = ob(npArr[:-1][-300:])
        if (
            npArr[-2][2] < bull_ob_top and
            npArr[-2][3] > bull_ob_top and
            npArr[-2][3] > npArr[-2][0] and
            npArr[-3][3] < npArr[-3][0]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            if op == sl: return 0, npArr[-1][0], 0, 0
            return signal, op, sl, tp
        elif (
            npArr[-2][1] > bear_ob_btm and
            npArr[-2][3] < bear_ob_btm and
            npArr[-2][3] < npArr[-2][0] and
            npArr[-3][3] > npArr[-3][0]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            if op == sl: return 0, npArr[-1][0], 0, 0
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def Ob(npArr, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top = ob(npArr[:-1][-77:])
    if (
        npArr[-2][3] < bull_ob_top
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-2][3] > bear_ob_btm
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def HpOb(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # sma = SmaArr(npArr[:,3][:-1], 50)
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 2:
    bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top = ob(npArr[:-1][-250:])
    if (
        npArr[-2][2] < bull_ob_top and
        npArr[-2][3] > bull_ob_top and
        npArr[-2][3] < npArr[-2][0]
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, bull_ob_btm, tp
    elif (
        npArr[-2][1] > bear_ob_btm and
        npArr[-2][3] < bull_ob_btm and
        npArr[-2][3] > npArr[-2][0]
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, bear_ob_top, tp
    return 0, npArr[-1][0], 0, 0

def ObRR(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # sma = SmaArr(npArr[:,3][:-1], 50)
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 2:
    bull_ob_btm, bull_ob_top, bear_ob_btm, bear_ob_top = ob(npArr[:-1][-250:])
    if (
        bull_ob_top != 0 and
        bear_ob_btm != 0 and
        npArr[-1][3] < (bull_ob_top + bear_ob_btm) / 2
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, bull_ob_btm, tp
    elif (
        bull_ob_top != 0 and
        bear_ob_btm != 0 and
        npArr[-1][3] > (bull_ob_top + bear_ob_btm) / 2
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, bear_ob_top, tp
    return 0, npArr[-1][0], 0, 0