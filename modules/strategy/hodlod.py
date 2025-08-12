import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr, EmaArr
from modules.entropy import Entropy
from modules.strategy.sweep import GetSweep

def get_hod_lod(npArr):
    period = 278
    interdayPeriod = 24
    npArr = npArr[-period:]
    maxVolIdx = np.argmax(npArr[:,4][-interdayPeriod:])
    sample = npArr[0:maxVolIdx-210]
    hod = np.max(sample[:,1])
    lod = np.min(sample[:,2])
    return hod, lod

def Hodlod(npArr, tf, tick_val=0.25):
    if len(npArr) < 278 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0

    hod, lod = get_hod_lod(npArr[:-1])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 4
    target = 45
    # longTp = hod + tick_val * target
    # shortTp = lod - tick_val * target
    if (
        npArr[-3][2] < lod and
        npArr[-2][1] > lod
    ):
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if tp - op > (op - sl) * rr:
            signal = 1
            return signal, op, sl, tp
    elif (
        npArr[-3][1] > hod and
        npArr[-2][2] < hod
    ):
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if op - tp > (sl - op) * rr:
            signal = -1
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
