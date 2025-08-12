import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr
from modules.bollingerBands import GetBollingerBands
from modules.rsi import GetRsi

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 1.1
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

def BollingerTrend(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 15
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    # sma = SmaArr(npArr[:-1][:,3], 100)
    upper, lower = GetBollingerBands(npArr[:-1][:,3][-31:], 20, 2)
    # rsi = GetRsi(npArr[:-1][:,3][-14:])
    # sma100 = SmaArr(npArr[:-1][:,3], 100)
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 2:
        bb_width_threshold = 0.0015
        bbwidth = (upper[-1] - lower[-1]) / ((upper[-1] + lower[-1])/2)
        if bbwidth > bb_width_threshold:
            if (
                npArr[-4][3] < upper[-1] and
                npArr[-3][3] < upper[-1] and
                npArr[-2][3] > upper[-1] and
                npArr[-2][1] > npArr[-3][1]
            ):
                # pe = permutation_entropy(npArr[:-1][-212:][:,3])
                # sma = SmaArr(pe, 40)
                # if pe[-1] < sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
            elif (
                npArr[-4][3] > lower[-1] and
                npArr[-3][3] > lower[-1] and
                npArr[-2][3] < lower[-1] and
                npArr[-2][2] < npArr[-3][2]
            ):
                # pe = permutation_entropy(npArr[:-1][-212:][:,3])
                # sma = SmaArr(pe, 40)
                # if pe[-1] < sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def BollingerBands(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 15
    if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    sma = SmaArr(npArr[:-1][:,3], 100)
    upper, lower = GetBollingerBands(npArr[:-1][:,3][-31:], 30, 1.5)
    rsi = GetRsi(npArr[:-1][:,3][-14:])
    # sma100 = SmaArr(npArr[:-1][:,3], 100)
    bb_width_threshold = 0.0015
    if (
        npArr[-3][3] < lower[-2] and
        rsi[-2] < 30 and
        rsi[-2] > 15 and
        npArr[-2][3] > npArr[-3][1] and
        npArr[-2][3] < sma[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] < sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    elif (
        npArr[-3][3] > upper[-2] and
        rsi[-2] > 70 and
        rsi[-2] < 85 and
        npArr[-2][3] < npArr[-3][2] and
        npArr[-2][3] > sma[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] < sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
