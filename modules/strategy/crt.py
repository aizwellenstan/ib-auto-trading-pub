import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.movingAverage import SmaArr
from modules.permutationEntropy import permutation_entropy

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

def FadeCrt(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    macd = MacdHistorical(np.array(npArr[:,3]).astype(float))
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
        sma = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-4][3] > npArr[-4][0] and
            npArr[-3][1] < npArr[-4][1] and
            npArr[-3][2] > npArr[-4][2] and
            npArr[-2][1] > npArr[-4][1] and
            npArr[-2][3] < sma[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            npArr[-4][3] < npArr[-4][0] and
            npArr[-3][2] > npArr[-4][2] and
            npArr[-3][1] < npArr[-4][1] and
            npArr[-2][2] < npArr[-4][2] and
            npArr[-2][3] > sma[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0