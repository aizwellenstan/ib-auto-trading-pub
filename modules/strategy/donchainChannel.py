import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 3
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-5:][:,2])
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-5:][:,1])
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def DcBreakOut(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    # volSma = SmaArr(npArr[:,4][:-1], 30)
    hh = npArr[:,1][len(npArr)-22:-2]
    if (
        len(hh) > 0 and
        npArr[-2][1] > max(hh)
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # ll = npArr[:,2][len(npArr)-22:-2]
    # if (
    #     len(ll) > 0 and
    #     npArr[-2][2] < min(ll)
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     if op == sl: return 0, npArr[-1][0], 0, 0
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def DcMidReversal(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # signal = 0
    # volSma = SmaArr(npArr[:,4][:-1], 20)
    period = 17
    hhp = np.max(npArr[:-2][-period:][:,1])
    llp = np.min(npArr[:-2][-period:][:,2])
    hh = np.max(npArr[:-1][-period:][:,1])
    ll = np.min(npArr[:-1][-period:][:,2])
    midp = (hhp + llp)/2
    mid = (hh + ll) / 2
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2
    if (
        mid >= midp and
        npArr[-3][2] < mid and
        npArr[-2][1] > npArr[-3][1] and
        npArr[-2][2] > npArr[-3][2]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        mid <= midp and
        npArr[-3][1] > mid and
        npArr[-2][2] < npArr[-3][2] and
        npArr[-2][1] < npArr[-3][1]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0