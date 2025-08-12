import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 5
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

def ResistanceToSupport(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    # volSma = SmaArr(npArr[:,4][:-1], 30)
    if (
        npArr[-3][2] < npArr[-5][1] and
        npArr[-4][3] > npArr[-4][0] and
        npArr[-5][2] < npArr[-6][2] and
        npArr[-4][2] > npArr[-5][2] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-4][1] > npArr[-5][1] and
        npArr[-3][1] < npArr[-4][1] and
        npArr[-3][3] < npArr[-3][0]
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
