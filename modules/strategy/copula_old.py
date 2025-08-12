import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from model.cvine_copula_nq import GetPosition
from modules.movingAverage import SmaArr
from modules.permutationEntropy import permutation_entropy
from modules.vwap import Vwap
import pandas as pd

def GetOPSLTP(npArr, signal, tf, tick_val):
    # TP_VAL = 1.333333333
    TP_VAL = 3
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[:-1][-2:][:,2])
        # sl = np.min(npArr[-2:][:,2])
        sl = floor_round(sl, tick_val)
        tp = op + (op-sl) * TP_VAL
        # sl = np.min(npArr[-4:][:,2]) - tick_val * 140
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[:-1][-2:][:,1])
        # sl = np.max(npArr[-2:][:,1])
        sl = ceil_round(sl, tick_val)
        tp = op - (sl-op) * TP_VAL
        # sl = np.max(npArr[-4:][:,1]) + tick_val * 140
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def getMaxVolumeRange(npArr):
    low = 0
    high = 0
    maxVolume = 0
    direction = 0
    volume = 0
    rVol = 0
    for i in range(0, len(npArr)):
        if npArr[i][4] > maxVolume:
            maxVolume = npArr[i][4]
            low = npArr[i][2]
            high = npArr[i][1]
            if abs(npArr[i][3]-npArr[i][0]) > (npArr[i][1]-npArr[i][2]) * 0.2:
                direction = -1
                if npArr[i][3] > npArr[i][0]:
                    direction = 1
            volume = npArr[i][4]
            if volume > 0:
                rVol = abs(npArr[i][3] - npArr[i][0]) / npArr[i][4]
    return low, high, direction, volume, rVol

def Copula(npArr, npArrTQQQ, npArrQQQ, npArrXLK, npArrOEF, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][4] < 1:
        return 0, npArr[-1][0], 0, 0

    # Create a DataFrame
    returns = pd.DataFrame({
        'TQQQ': npArrTQQQ[:-1][:,3],
        'QQQ': npArrQQQ[:-1][:,3],
        'XLK': npArrXLK[:-1][:,3],
        'OEF': npArrOEF[:-1][:,3]
    })
    returns = returns.pct_change().fillna(0)

    position = GetPosition(returns[-400:])
    print(position)
    if (
        position > 0
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        position < 0
    ):
        print("SHORT")
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OpeningRange(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    if npArr[-3][4] < npArr[-4][4] * 6: return 0, npArr[-1][0], 0, 0
    high = npArr[-3][1]
    low = npArr[-3][2]
    if (
        npArr[-2][3] > high
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        npArr[-2][3] < low
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OpeningRangeReverse(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    low, high, direction, volume, rVol = getMaxVolumeRange(npArr[:-1][-23:])
    if (
        npArr[-2][2] < high and
        npArr[-2][3] > high and
        npArr[-2][1] > npArr[-3][1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        npArr[-2][1] > low and
        npArr[-2][3] < low and
        npArr[-2][2] < npArr[-3][2]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def BigVolmeVTurn(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    signal = 0
    if (
        npArr[-2][4] < npArr[-3][4] and
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][3] > npArr[-3][1] and
        npArr[-2][4] > max(npArr[:,4][-20:-3])
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    # e
    #                     signal = -1
    #                     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #                     return signal, npArr[-i][2], sl, tp
    return 0, npArr[-1][0], 0, 0

def ReverseIrb(npArr, tf, tick_val=0.25):
    if len(npArr) < 21:
        return 0, npArr[-1][0], 0, 0
    signal = 0
    # for i in range(3, 11):
    # if (
    #     (
    #         min(npArr[-3][0], npArr[-3][3]) - npArr[-3][2]
    #     ) / (npArr[-3][1] - npArr[-3][2]) >= 0.45
    # ):
    #     if npArr[-2][1] > npArr[-3][1]:
    #         signal = 1
    #         op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #         return signal, op, sl, tp
    for i in range(3, 6):
        if (
            (
                min(npArr[-i][0], npArr[-i][3]) - npArr[-i][2]
            ) / (npArr[-i][1] - npArr[-i][2]) >= 0.45
        ):
            if npArr[-2][1] > npArr[-i][1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    # for i in range(3, 12):
    #     if (
    #         (
    #             npArr[-i][1] - max(npArr[-i][0], npArr[-i][3])
    #         ) / (npArr[-i][1] - npArr[-i][2]) >= 0.45
    #     ):
    #         if npArr[-2][1] > npArr[-i][1]:
    #             signal = -1
    #             op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #             return signal, op, sl, tp
    # elif (
    #     npArr[-5][3] > npArr[-5][0] and
    #     npArr[-4][3] > npArr[-4][0] and
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][3] < npArr[-2][0]
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0