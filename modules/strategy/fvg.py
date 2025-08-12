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
        sl = np.min(npArr[:-1][-2:][:,2]) + tick_val * 3
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[:-1][-2:][:,1]) - tick_val * 3
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def GetOPSLTPFvgV(npArr, signal, tf, tick_val):
    TP_VAL = 2.489
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-3:][:,2]) + tick_val * 3
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-3:][:,1]) - tick_val * 3
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def GetOPSLTPFvg(npArr, signal, tf, tick_val, fvgLv):
    TP_VAL = 2.489
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = fvgLv
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = fvgLv
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

# def Fvg(npArr, tf, tick_val=0.25):
#     if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
#         return 0, npArr[-1][0], 0, 0
#     rr = 2.1
#     op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
#     signal = 0
#     length = len(npArr)
#     period = 100
#     if length > period: length = period
#     fvgStartIdx = 0
#     low = npArr[-2][2]
#     for i in range(4, length):
#         if npArr[-i][3] < low:
#             fvgLow = npArr[-i][1]
#             if min(npArr[-i+1:][:,3]) > fvgLow:
#                 fvgStartIdx = i
#                 break
#     if fvgStartIdx != 0:
#         fvgHigh = npArr[-fvgStartIdx+2][2]
#         fvgLow = npArr[-fvgStartIdx][1]
#         if npArr[-fvgStartIdx][1] < fvgHigh:
#             if (
#                 npArr[-2][3] > fvgHigh and
#                 npArr[-2][2] < fvgHigh and
#                 npArr[-2][2] > (fvgHigh + fvgLow) / 2
#             ):
#                 signal = 1
#                 tp = op + maxRangeLong
#                 sl = npArr[-2][2]
#                 if op - sl > tick_val:
#                     slippage = tick_val * 2
#                     if (tp - op - slippage) / (op - sl + slippage) > rr:
#                         return signal, op, sl, tp
#     # fvgStartIdx = 0
#     # high = npArr[-2][1]
#     # for i in range(4, length):
#     #     if npArr[-i][3] > high:
#     #         fvgHigh = npArr[-i][2]
#     #         if max(npArr[-i+1:][:,3]) < fvgHigh:
#     #             fvgStartIdx = i
#     #             break
#     # if fvgStartIdx != 0:
#     #     fvgHigh = npArr[fvgStartIdx][1]
#     #     fvgLow = npArr[fvgStartIdx+2][2]
#     #     if npArr[fvgStartIdx][2] > fvgLow:
#     #         if (
#     #             npArr[-2][3] < fvgLow and
#     #             npArr[-2][1] > fvgLow and
#     #             npArr[-2][1] < (fvgHigh + fvgLow) / 2
#     #         ):
#     #             signal = -1
#     #             op, sl, tp = GetOPSLTPFvg(npArr, signal, tf, tick_val, fvgHigh)
#     #             if op == sl: return 0, npArr[-1][0], 0, 0
#     #             return signal, op, sl, tp
#     # elif (
#     #     npArr[-3][3] < npArr[-3][0] and
#     #     npArr[-2][2] > npArr[-3][2] and
#     #     npArr[-3][1] - npArr[-2][3] > atr * 3
#     # ):
#     #     signal = -1
#     #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
#     #     return signal, op, sl, tp
#     return 0, npArr[-1][0], 0, 0

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

def Fvg(npArr, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    rr = 2.5
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    if (
        npArr[-2][2] > npArr[-4][1] and
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
        npArr[-2][1] < npArr[-4][2] and
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

def DoubleFvg(npArr, tf, tick_val=0.25):
    if len(npArr) < 202 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    rr = 2
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    for i in range(3, 5):
        if (
            npArr[-i][3] < npArr[-i][0] and
            npArr[-2][2] > npArr[-4][1]
        ):
            signal = 1
            tp = op + maxRangeLong + tick_val
            sl = npArr[-2][2]
            if op - sl > tick_val * 2:
                slippage = tick_val * 2
                if (tp - op - slippage) / (op - sl + slippage) > rr:
                    return signal, op, sl, tp
        elif (
            npArr[-i][3] > npArr[-i][0] and
            npArr[-2][1] < npArr[-4][2]
        ):
            signal = -1
            tp = op - maxRangeShort - tick_val
            sl = npArr[-2][1]
            if sl - op > tick_val * 2:
                slippage = tick_val * 2
                if (op - tp - slippage) / (sl - op + slippage) > rr:
                    return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def FvgComb(npArr, npArr2, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    if len(npArr2) < 32 or npArr2[-2][5] < 1 or npArr2[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    rr = 2.5
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    if (
        npArr2[-2][2] > npArr2[-4][1] and
        npArr2[-2][1] > npArr2[-3][1]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr2[-2][1] < npArr2[-4][2] and
        npArr2[-2][2] < npArr2[-3][2]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def IFvg(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    topVol = classify_top_n_bars(npArr[:-1][-100:], 2)
    sma = SmaArr(npArr[:,3][:-1], 50)
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        for i in range(5, 12):
            if (
                npArr[-2][3] > sma[-1] and
                # npArr[-14][3] < npArr[-14][0] and
                # npArr[-13][3] < npArr[-13][0] and
                # npArr[-12][3] < npArr[-i][0] and
                np.min(npArr[-i:-4][:,3]) < npArr[-i][0] and
                # npArr[-i][1] < npArr[-i-2][2] and
                # npArr[-4][0] < npArr[-i][0] and
                # npArr[-4][3] > npArr[-i-2][2] and
                # npArr[-4][3] > npArr[-4][0] and
                npArr[-3][3] < npArr[-i][2] and
                # npArr[-3][3] > npArr[-i][1] and
                npArr[-2][2] < npArr[-i][1] and
                npArr[-2][3] > npArr[-i][1] and
                npArr[-2][1] < npArr[-3][1]
            ):
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                if op == sl: return 0, npArr[-1][0], 0, 0
                return signal, op, sl, tp
            if (
                npArr[-2][3] < sma[-1] and
                # npArr[-14][3] > npArr[-14][0] and
                # npArr[-13][3] > npArr[-13][0] and
                # npArr[-12][3] > npArr[-i][0] and
                np.max(npArr[-i:-4][:,3]) > npArr[-i][0] and
                # npArr[-i][2] > npArr[-i-2][1] and
                # npArr[-4][0] > npArr[-i][0] and
                # npArr[-4][3] < npArr[-i-2][1] and
                # npArr[-4][3] < npArr[-4][0] and
                npArr[-3][3] > npArr[-i][1] and
                # npArr[-3][3] < npArr[-i][2] and
                npArr[-2][1] > npArr[-i][2] and
                npArr[-2][3] < npArr[-i][2] and
                npArr[-2][2] > npArr[-3][2]
            ):
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                if op == sl: return 0, npArr[-1][0], 0, 0
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def FvgTurn(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['1 mins', '5 mins']: atrPeriod = 200
    atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if (
        npArr[3][1] > npArr[4][1] and
        npArr[3][2] < npArr[4][2] and
        npArr[2][2] > npArr[4][0] and
        npArr[2][2] < npArr[4][1] and
        npArr[2][3] > npArr[3][1] and
        npArr[3][3] > npArr[5][0] and
        npArr[4][3] < npArr[5][2] and
        npArr[5][3] < npArr[5][0] and
        npArr[-2][3] - npArr[-3][2] > atr * 2
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val, npArr[-2][2])
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    elif (
        npArr[3][2] < npArr[4][2] and
        npArr[3][1] > npArr[4][1] and
        npArr[2][1] < npArr[4][0] and
        npArr[2][1] > npArr[4][2] and
        npArr[2][3] < npArr[3][2] and
        npArr[3][3] < npArr[5][0] and
        npArr[4][3] > npArr[5][1] and
        npArr[5][3] > npArr[5][0] and
        npArr[-2][3] - npArr[-3][2] > atr * 2
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val, npArr[-2][1])
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
        

# def BullFvg():
#     fvgStartIdx = 0
#     low = npArr[-2][2]
#     for i in range(3, len(npArr)):
#         if npArr[-i][3] < low:
#             fvgStartIdx = i
#             break
#     if fvgStartIdx != 0:
#         fvgHigh = npArr[fvgStartIdx+2][2]
#         if npArr[fvgStartIdx][1] < fvgHigh:
#             if npArr[-2][3] > fvgHigh:

    
    