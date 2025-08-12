import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr
from modules.permutationEntropy import permutation_entropy
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 1.72340425532
    # if tf in ['20 mins']: TP_VAL = 4
    # elif tf in ['30 mins']: TP_VAL = 2
    # elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-2:][:,2])
        sl = floor_round(sl, tick_val)
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-2:][:,1])
        sl = ceil_round(sl, tick_val)
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def GetOPSLTPLts(npArr, signal, tick_val):
    # TP_VAL = 3
    TP_VAL = 19
    # TP_VAL = 13
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[:-1][-1:][:,2])
        sl = op - tick_val * 1
        sl = floor_round(sl, tick_val)
        tp = op + tick_val * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[:-1][-1:][:,1])
        sl = op + tick_val * 1
        sl = ceil_round(sl, tick_val)
        tp = op - tick_val * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

# def GetMovesToSweep(op, targets, reverse=False, tick_val=0.25):
#     targets.sort(reverse=reverse)
#     maxRR = 0
#     maxRange = 0
#     c = 0
#     for t in targets:
#         if t - op <= tick_val * 11: continue
#         c += 1
#         rr = c / abs(t - op)
#         if rr > maxRR:
#             maxRR = rr
#             maxRange = abs(t - op)
#     return maxRR, maxRange

# def GetSweep(npArr, period=30, tick_val=0.25):
#     unSweepHigh = {}
#     unSweepLow = {}
#     for i in range(0, period):
#         high = npArr[-2-period+i][1]
#         low = npArr[-2-period+i][2]
#         unSweepHigh[high] = 1
#         unSweepLow[low] = 1
#         for periousHigh in list(unSweepHigh.keys()):
#             if high > periousHigh:
#                 unSweepHigh.pop(periousHigh)
#         for periousLow in list(unSweepLow.keys()):
#             if low < periousLow:
#                 unSweepLow.pop(periousLow)
#     op = npArr[-2][3]
#     maxRRLong, maxRangeLong = GetMovesToSweep(op, list(unSweepHigh.keys()), False, tick_val)
#     maxRRShort, maxRangeShort = GetMovesToSweep(op, list(unSweepHigh.keys()), True, tick_val)
#     return op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort

def ThreeBarReversal(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    # period = 80
    # # period = 100
    # longTpHigh = 0
    # longTpLow = 0
    # longMaxTick = 0
    # shortTpHigh = 0
    # shortTpLow = 0
    # shortMaxTick = 0
    # for i in range(0, period):
    #     high = npArr[-2-period+i][1]
    #     low = npArr[-2-period+i][2]
    #     tick = npArr[-2-period+i][5]
    #     if tick > longMaxTick:
    #         longMaxTick = tick
    #         if high > npArr[-2][3]:
    #             longTpHigh = high
    #         if low > npArr[-2][3]:
    #             longTpLow = low
    #     if tick > shortMaxTick:
    #         shortMaxTick = tick
    #         if high < npArr[-2][3]:
    #             shortTpHigh = high
    #         if low < npArr[-2][3]:
    #             shortTpLow = low
    if (
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][1] > npArr[-3][1] and
        npArr[-2][3] < npArr[-3][1] and
        npArr[-2][5] < npArr[-3][5] * 0.8 and
        npArr[-2][4] / npArr[-2][5] < npArr[-3][4] / npArr[-3][5]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        return signal, op, sl, tp
    elif (
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][2] < npArr[-3][2] and
        npArr[-2][3] > npArr[-3][2] and
        npArr[-2][5] < npArr[-3][5] * 0.8 and
        npArr[-2][4] / npArr[-2][5] < npArr[-3][4] / npArr[-3][5]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OriThreeBarReversal(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.4
    if (
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] > npArr[-2][0]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif(
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def HpThreeBarReversal(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.4
    if (
        npArr[-4][3] < npArr[-5][0] and
        npArr[-4][2] > npArr[-5][2] and
        npArr[-2][3] < npArr[-2][0]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif(
        npArr[-4][3] > npArr[-5][0] and
        npArr[-4][1] < npArr[-5][1] and
        npArr[-2][3] > npArr[-2][0]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def Pin(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    # period = 80
    # # period = 100
    # longTpHigh = 0
    # longTpLow = 0
    # longMaxTick = 0
    # shortTpHigh = 0
    # shortTpLow = 0
    # shortMaxTick = 0
    # for i in range(0, period):
    #     high = npArr[-2-period+i][1]
    #     low = npArr[-2-period+i][2]
    #     tick = npArr[-2-period+i][5]
    #     if tick > longMaxTick:
    #         longMaxTick = tick
    #         if high > npArr[-2][3]:
    #             longTpHigh = high
    #         if low > npArr[-2][3]:
    #             longTpLow = low
    #     if tick > shortMaxTick:
    #         shortMaxTick = tick
    #         if high < npArr[-2][3]:
    #             shortTpHigh = high
    #         if low < npArr[-2][3]:
    #             shortTpLow = low
    rr = 1
    if (
        npArr[-3][1] - npArr[-3][3] > 
        (npArr[-3][1] - npArr[-3][2]) * 0.6 and
        npArr[-2][1] - npArr[-2][3] > 
        (npArr[-2][1] - npArr[-2][2]) * 0.6 and
        npArr[-2][5] > npArr[-3][5] * 1.2 and
        npArr[-2][4] / npArr[-2][5] > npArr[-3][4] / npArr[-3][5]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-3][3] - npArr[-3][2] > 
        (npArr[-3][1] - npArr[-3][2]) * 0.6 and
        npArr[-2][3] - npArr[-2][2] > 
        (npArr[-2][1] - npArr[-2][2]) * 0.6 and
        npArr[-2][5] > npArr[-3][5] * 1.2 and
        npArr[-2][4] / npArr[-2][5] > npArr[-3][4] / npArr[-3][5]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def ThreeBarReversalLts(npArr, tick_val=0.25):
    if len(npArr) < 100:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if (
        npArr[-4][3] < npArr[-7][0] and
        npArr[-4][3] < npArr[-4][0] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] > npArr[-3][1] and
        npArr[-3][2] < npArr[-4][2] and
        npArr[-2][2] > npArr[-3][2]
    ):
        signal = 1
        op, sl, tp = GetOPSLTPLts(npArr, signal, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
