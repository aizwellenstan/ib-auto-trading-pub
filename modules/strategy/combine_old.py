import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr, EmaArr
from modules.vwap import Vwap
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

def Combine(npArr, tf, tick_val=0.25):
    if len(npArr) < 201:
        return 0, npArr[-1][0], 0, 0, ""
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    sType = ""
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        signal = 0
        IS_THREEBARPLAY = False
        # vwapPeriod = 50
        # npArrC = npArr[:-1]
        # npArrC = npArrC[npArrC[:, 4] != 0]
        # vwap = Vwap(npArrC[:,4][-vwapPeriod:],npArrC[:,1][-vwapPeriod:],npArrC[:,2][-vwapPeriod:])
        # ema = EmaArr(npArr[:-1][:,3][-9:], 8)
        if (
            npArr[-3][3] > npArr[-3][0] and
            npArr[-2][1] < npArr[-3][1]
        ): 
            IS_THREEBARPLAY = True
            sType += "THREE BAR PLAY"
        IS_ENGULFING = False
        if (
            npArr[-2][2] < npArr[-4][2] and
            npArr[-2][1] > npArr[-3][1] and
            npArr[-2][2] < npArr[-3][2]
        ): 
            IS_ENGULFING = True
            sType += "ENGULFING"
        if (
            (
                IS_THREEBARPLAY or IS_ENGULFING
            ) and
            npArr[-2][3] - npArr[-3][2] > atr * 3
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                if op == sl: return 0, npArr[-1][0], 0, 0, sType
                return signal, op, sl, tp, sType
    # elif (
    #     npArr[-3][3] < npArr[-3][0] and
    #     npArr[-2][2] > npArr[-3][2] and
    #     npArr[-3][1] - npArr[-2][3] > atr * 3
    # ):
    #     signal = -1
    #     op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
    #     return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0, sType