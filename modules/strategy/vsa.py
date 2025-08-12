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
        sl = np.min(npArr[-5:][:,2]) - tick_val
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-5:][:,1]) + tick_val
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def VolumeImbalance(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    # volSma = SmaArr(npArr[:,4][:-1], 30)
    if (
        npArr[-4][3] > npArr[-4][0] and
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-3][4] > npArr[-4][4] and
        npArr[-2][4] < npArr[-3][4]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][3] - npArr[-2][0] < (npArr[-3][0]-npArr[-3][3])*0.5 and
    #     npArr[-2][4] < npArr[-5][4] and
    #     npArr[-2][4] < npArr[-4][4] and
    #     npArr[-2][4] < npArr[-3][4]
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     if op == sl: return 0, npArr[-1][0], 0, 0
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def NoSupplyBar(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    # volSma = SmaArr(npArr[:,4][:-1], 30)
    if (
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][0] - npArr[-2][3] < (npArr[-3][3]-npArr[-3][0])*0.5 and
        npArr[-2][4] < npArr[-5][4] and
        npArr[-2][4] < npArr[-4][4] and
        npArr[-2][4] < npArr[-3][4]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][3] - npArr[-2][0] < (npArr[-3][0]-npArr[-3][3])*0.5 and
    #     npArr[-2][4] < npArr[-5][4] and
    #     npArr[-2][4] < npArr[-4][4] and
    #     npArr[-2][4] < npArr[-3][4]
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     if op == sl: return 0, npArr[-1][0], 0, 0
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def PseudoInverseDownThrust(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    # volSma = SmaArr(npArr[:,4][:-1], 30)
    if (
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][1] - min(npArr[-2][3],npArr[-2][0]) > (npArr[-2][1] - npArr[-2][2]) * 0.84 and
        npArr[-2][0] - npArr[-2][3] < (npArr[-3][3]-npArr[-3][0]) * 0.3 and
        npArr[-2][4] < npArr[-6][4] and
        npArr[-2][4] < npArr[-5][4] and
        npArr[-2][4] < npArr[-4][4] and
        npArr[-2][4] < npArr[-3][4]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SellingClimax(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    volSma = SmaArr(npArr[:,4][:-1], 30)
    if (
        npArr[-2][3] < npArr[-2][0] and
        npArr[-2][0] - npArr[-2][3] > abs(npArr[-5][3]-npArr[-5][0]) and
        npArr[-2][0] - npArr[-2][3] > abs(npArr[-4][3]-npArr[-4][0]) and
        npArr[-2][0] - npArr[-2][3] > abs(npArr[-3][3]-npArr[-3][0]) and
        npArr[-2][4] > volSma[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][2] > npArr[-3][2] and
    #     npArr[-3][1] - npArr[-2][3] > atr * 3
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def DownThrust(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    volSma = SmaArr(npArr[:,4][:-1], 30)
    if (
        (npArr[-2][1] - npArr[-2][2]) > 0 and
        (min(npArr[-2][0],npArr[-2][3]) - npArr[-2][2]) /
        (npArr[-2][1] - npArr[-2][2]) >= 0.45 and
        npArr[-2][4] > volSma[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][2] > npArr[-3][2] and
    #     npArr[-3][1] - npArr[-2][3] > atr * 3
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def BearishEffortBearishResult(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    signal = 0
    if (
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-2][4] < npArr[-3][4] and
        npArr[-2][0] - npArr[-2][3] >
        (npArr[-3][0] - npArr[-3][3]) * 3
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][2] > npArr[-3][2] and
    #     npArr[-3][1] - npArr[-2][3] > atr * 3
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
