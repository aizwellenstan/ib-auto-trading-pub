import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 20
    if tf == "15 mins": TP_VAL = 21
    # TP_VAL = 13
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[:-1][-2:][:,2])
        tp = op + tick_val * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[:-1][-2:][:,1])
        tp = op - tick_val * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def FourBarTP(npArr, tf, tick_val=0.25):
    if len(npArr) < 22:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    atrPeriod = 50
    # if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 2:
        signal = 0
        if (
            npArr[-6][3] < npArr[-6][0] and
            npArr[-5][3] < npArr[-5][0] and
            npArr[-4][3] < npArr[-4][0] and
            npArr[-3][3] > npArr[-3][0] and
            npArr[-2][3] > npArr[-2][0] and
            npArr[-2][3] > npArr[-4][0]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            sl = floor_round(op - (op-sl) / 1.6, tick_val)
            # if op - sl > tick_val * 21:
            #     sl += tick_val * 19
            return signal, op, sl, tp
        elif (
            npArr[-6][3] > npArr[-6][0] and
            npArr[-5][3] > npArr[-5][0] and
            npArr[-4][3] > npArr[-4][0] and
            npArr[-3][3] < npArr[-3][0] and
            npArr[-2][3] < npArr[-2][0] and
            npArr[-2][3] < npArr[-4][0]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            sl = ceil_round(op + (sl-op) / 1.6, tick_val)
            # if sl - op > tick_val * 21:
            #     sl -= tick_val * 19
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

# 30 mins
def ThreeBarTP(npArr, tf, tick_val=0.25):
    if len(npArr) < 202 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 200, tick_val)
    rr = 1.1
    period = 8
    if (
        npArr[-3][3] < np.min(npArr[:-3][-period:][:,2]) and
        npArr[-2][3] > npArr[-3][1]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = floor_round(op-(op - npArr[-2][2])/3, tick_val)
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-3][3] > np.max(npArr[:-3][-period:][:,1]) and
        npArr[-2][3] < npArr[-3][2]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = ceil_round(op+(npArr[-2][1] - op)/3, tick_val)
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OriFourBarTP(npArr, tf, tick_val=0.25):
    if len(npArr) < 202 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.5
    if (
        npArr[-2][3] > npArr[-7][3] and
        npArr[-2][3] - npArr[-2][0] >
        npArr[-3][3] - npArr[-3][0]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 5:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-2][3] < npArr[-7][3] and
        npArr[-2][0] - npArr[-2][3] >
        npArr[-3][0] - npArr[-3][3]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 5:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SixBarTP(npArr, tf, tick_val=0.25):
    if len(npArr) < 22:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    atrPeriod = 50
    # if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 2:
        signal = 0
        if (
            # npArr[-7][3] < npArr[-7][0] and
            npArr[-5][3] < npArr[-7][0] and
            # npArr[-4][3] > npArr[-4][0] and
            # npArr[-3][3] > npArr[-3][0] and
            npArr[-3][3] > npArr[-4][0] and
            npArr[-2][3] > npArr[-2][0] and
            npArr[-2][3] > npArr[-6][0]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            # npArr[-7][3] > npArr[-7][0] and
            npArr[-5][3] > npArr[-7][0] and
            # npArr[-4][3] < npArr[-4][0] and
            npArr[-3][3] < npArr[-4][0] and
            npArr[-2][3] < npArr[-2][0] and
            npArr[-2][3] < npArr[-6][0]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def EightBarTP(npArr, tf, tick_val=0.25):
    if len(npArr) < 22:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    atrPeriod = 50
    # if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 2:
        signal = 0
        if (
            npArr[-10][3] < npArr[-10][0] and
            npArr[-8][3] < npArr[-9][0] and
            npArr[-8][3] < npArr[-8][0] and
            # npArr[-7][3] < npArr[-7][0] and
            npArr[-6][3] < npArr[-6][0] and
            npArr[-6][3] < npArr[-7][0] and
            # npArr[-5][3] > npArr[-5][0] and
            npArr[-4][3] > npArr[-5][0] and
            npArr[-2][3] > npArr[-3][0] and
            npArr[-2][3] > npArr[-2][0] and
            npArr[-2][3] > npArr[-6][0]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            npArr[-10][3] > npArr[-10][0] and
            npArr[-8][3] > npArr[-9][0] and
            npArr[-8][3] > npArr[-8][0] and
            # npArr[-7][3] > npArr[-7][0] and
            npArr[-6][3] > npArr[-6][0] and
            npArr[-6][3] > npArr[-7][0] and
            # npArr[-5][3] < npArr[-5][0] and
            npArr[-4][3] < npArr[-5][0] and
            npArr[-2][3] < npArr[-3][0] and
            npArr[-2][3] < npArr[-2][0] and
            npArr[-2][3] < npArr[-6][0]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0