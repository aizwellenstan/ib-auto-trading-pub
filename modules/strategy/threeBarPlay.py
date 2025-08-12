import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr, EmaArr
from modules.strategy.sweep import GetSweep

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

def ThreeBarPlay(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    if (
        npArr[-3][3] > npArr[-3][0] and
        npArr[-2][1] < npArr[-3][1] and
        npArr[-2][2] > npArr[-3][2] and
        npArr[-2][3] < npArr[-2][0] and
        npArr[-2][5] < npArr[-3][5] * 0.6 and
        npArr[-2][4] / npArr[-2][5] < npArr[-3][4] / npArr[-3][5]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        return signal, op, sl, tp
    elif (
        npArr[-3][3] < npArr[-3][0] and
        npArr[-2][1] < npArr[-3][1] and
        npArr[-2][2] > npArr[-3][2] and
        npArr[-2][3] > npArr[-2][0] and
        npArr[-2][5] < npArr[-3][5] * 0.6 and
        npArr[-2][4] / npArr[-2][5] < npArr[-3][4] / npArr[-3][5]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
    return 0, npArr[-1][0], 0, 0

def HpThreeBarPlay(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['10m']: TP_VAL = 1.03
    # closeArr = npArr[:,3]
    # print(npArr[-1][3], npArr[-2][3], ema9[-1], ema21[-1])
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # sma = SmaArr(npArr[:,3][:-1], 50)
    signal = 0
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        if (
            npArr[-3][3] > npArr[-3][0] and
            npArr[-2][1] < npArr[-3][1] and
            npArr[-2][3] - npArr[-3][2] > atr * 3
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = EmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            sma = EmaArr(pe, 50)
            if pe[-1] < sma[-1]:
                pe = permutation_entropy(npArr[:-1][-212:][:,4])
                # sma = SmaArr(pe, 40)
                # if pe[-1] > sma[-1]:
                sma = EmaArr(pe, 50)
                if pe[-1] > sma[-1]:
                    signal = 1
                    op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                    if op == sl: return 0, npArr[-1][0], 0, 0
                    return signal, op, sl, tp
        elif (
            npArr[-3][3] < npArr[-3][0] and
            npArr[-2][2] > npArr[-3][2] and
            npArr[-3][1] - npArr[-2][3] > atr * 3
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            sma = EmaArr(pe, 50)
            if pe[-1] < sma[-1]:
                pe = permutation_entropy(npArr[:-1][-212:][:,4])
                # sma = SmaArr(pe, 40)
                # if pe[-1] > sma[-1]:
                sma = EmaArr(pe, 50)
                if pe[-1] > sma[-1]:
                    signal = -1
                    op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                    return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def CheckThreeBarPlay(npArr, sma25, sma200):
    atrRange: float = 3.4
    size: int = 50
    # size: int = 1
    k: int = 0
    buy: int = 0
    sell: int = 0

    while k < size:
        k += 1
        print(k)
        if k < 6:
            signalCandleClose3 = npArr[-(k*2+1)][3]
            signalCandleOpen3 = npArr[-k*3][0]
            bigCandleRange3 = abs(signalCandleClose3 - signalCandleOpen3)
            smallCandleRange3 = abs(npArr[-(k*3+1)][3] - npArr[-k*4][0])
            endCandleRange3 = abs(npArr[-1][3] - npArr[-k][0])

            if (bigCandleRange3 > smallCandleRange3 * 4):
                if (signalCandleClose3 > signalCandleOpen3
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange3
                    and endCandleRange3 < bigCandleRange3*0.5):
                    if (npArr[-1][3] < npArr[-1][0]):
                        if (npArr[-1][1] - npArr[-1][3]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose3 < signalCandleOpen3
                    and abs(npArr[-(k+1)][3]-npArr[-k*2][0]) < bigCandleRange3
                    and endCandleRange3 < bigCandleRange3*0.5):
                    if (npArr[-1][3] > npArr[-1][0]):
                        if (npArr[-1][3] - npArr[-1][2]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            sell += 1
                    else:
                        sell += 1
        if k < 4:
            signalCandleClose6 = npArr[-(k*5+1)][3]
            signalCandleOpen6 = npArr[-k*6][0]
            bigCandleRange6 = abs(signalCandleClose6 - signalCandleOpen6)
            smallCandleRange6 = abs(npArr[-(k*6+1)][3] - npArr[-k*7][0])
            endCandleRange6 = abs(npArr[-1][3] - npArr[-k][0])

            if (bigCandleRange6 > smallCandleRange6 * 4):
                if (signalCandleClose6 > signalCandleOpen6
                    and abs(npArr[-(k*4+1)][3] - npArr[-k*5][0]) < bigCandleRange6
                    and abs(npArr[-(k*3+1)][3] - npArr[-k*4][0]) < bigCandleRange6
                    and abs(npArr[-(k*2+1)][3] - npArr[-k*3][0]) < bigCandleRange6
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange6
                    and endCandleRange6 < bigCandleRange6*0.5):
                    if (npArr[-1][3] < npArr[-1][0]):
                        if (npArr[-1][1] - npArr[-1][3]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose6 < signalCandleOpen6
                    and abs(npArr[-(k*4+1)][3] - npArr[-k*5][0]) < bigCandleRange6
                    and abs(npArr[-(k*3+1)][3] - npArr[-k*4][0]) < bigCandleRange6
                    and abs(npArr[-(k*2+1)][3] - npArr[-k*3][0]) < bigCandleRange6
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange6
                    and endCandleRange6 < bigCandleRange6*0.5):
                    if (npArr[-1][3] > npArr[-1][0]):
                        if (npArr[-1][3] - npArr[-1][2]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            sell += 1
                    else:
                        sell += 1

        if k < 4:
            signalCandleClose5 = npArr[-(k*4+1)][3]
            signalCandleOpen5 = npArr[-k*5][0]
            bigCandleRange5 = abs(signalCandleClose5 - signalCandleOpen5)
            smallCandleRange5 = abs(npArr[-(k*5+1)][3] - npArr[-k*6][0])
            endCandleRange5 = abs(npArr[-1][3] - npArr[-k][0])

            if (bigCandleRange5 > smallCandleRange5 * 4):
                if (signalCandleClose5 > signalCandleOpen5
                    and abs(npArr[-(k*3+1)][3] - npArr[-k*4][0]) < bigCandleRange5
                    and abs(npArr[-(k*2+1)][3] - npArr[-k*3][0]) < bigCandleRange5
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange5
                    and endCandleRange5 < bigCandleRange5*0.5):
                    if (npArr[-1][3] < npArr[-1][0]):
                        if (npArr[-1][1] - npArr[-1][3]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose5 < signalCandleOpen5
                    and abs(npArr[-(k*3+1)][3] - npArr[-k*4][0]) < bigCandleRange5
                    and abs(npArr[-(k*2+1)][3] - npArr[-k*3][0]) < bigCandleRange5
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange5
                    and endCandleRange5 < bigCandleRange5*0.5):
                    if (npArr[-1][3] > npArr[-1][0]):
                        if (npArr[-1][3] - npArr[-1][2]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            sell += 1
                    else:
                        sell += 1

        if k < 5:
            signalCandleClose4 = npArr[-(k*3+1)][3]
            signalCandleOpen4 = npArr[-k*4][0]
            bigCandleRange4 = abs(signalCandleClose4 - signalCandleOpen4)
            smallCandleRange4 = abs(npArr[-(k*4+1)][3] - npArr[-k*5][0])
            endCandleRange4 = abs(npArr[-1][3] - npArr[-k][0])

            if (bigCandleRange4 > smallCandleRange4 * 4):
                if (signalCandleClose4 > signalCandleOpen4
                    and abs(npArr[-(k*2+1)][3] - npArr[-k*3][0]) < bigCandleRange4
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange4
                    and endCandleRange4 < bigCandleRange4*0.5):
                    if (npArr[-1][3] < npArr[-1][0]):
                        if (npArr[-1][1] - npArr[-1][3]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            buy += 1
                    else:
                        buy += 1

                if (signalCandleClose4 < signalCandleOpen4
                    and abs(npArr[-(k*2+1)][3] - npArr[-k*3][0]) < bigCandleRange4
                    and abs(npArr[-(k+1)][3] - npArr[-k*2][0]) < bigCandleRange4
                    and endCandleRange4 < bigCandleRange4*0.5):
                    if (npArr[-1][3] > npArr[-1][0]):
                        if (npArr[-1][3] - npArr[-1][2]
                                > (npArr[-1][1] - npArr[-1][2])*0.13):
                            sell += 1
                    else:
                        sell += 1

        # --- 4btp
        if k < 5:
            if (npArr[-(k*4+1)][3] < npArr[-k*5][0]
                and npArr[-(k*3+1)][3] < npArr[-k*4][0]
                and npArr[-(k*2+1)][3] > npArr[-k*3][0]
                and npArr[-2][3] > npArr[-k*2][0]
                and npArr[-1][4] > npArr[-2][4]
                and npArr[-1][3] < npArr[-2][3]):
                buy += 1

            if (npArr[-(k*4+1)][3] > npArr[-k*5][0]
                and npArr[-(k*3+1)][3] > npArr[-k*4][0]
                and npArr[-(k*2+1)][3] < npArr[-k*3][0]
                and npArr[-2][3] < npArr[-k*2][0]
                and npArr[-1][4] > npArr[-2][4]
                and npArr[-1][3] > npArr[-2][3]):
                sell += 1

        # bias
        bias = (npArr[-1][3]-sma25)/sma25

        if(bias < -0.0482831585):
            buy += 1
        if(bias > 0.0482831585):
            sell += 1

        # sma200
        if(npArr[-1][3] < npArr[-2][3]
                and npArr[-1][3] > sma200):
            buy += 1
        if(npArr[-1][3] > npArr[-2][3]
                and npArr[-1][3] < sma200):
            sell += 1
        
        # 8btp
        if k < 3:
            if (npArr[-(k*7+1)][3] < npArr[-k*8][0]
                and npArr[-(k*6+1)][3] < npArr[-k*7][0]
                and npArr[-(k*5+1)][3] < npArr[-k*6][0]
                and npArr[-(k*4+1)][3] < npArr[-k*5][0]
                and npArr[-(k*3+1)][3] > npArr[-k*4][0]
                and npArr[-(k*2+1)][3] > npArr[-k*3][0]
                and npArr[-(k+1)][3] > npArr[-k*2][0]
                and npArr[-1][3] < npArr[-k][3]):
                buy += 1

            if (npArr[-(k*7+1)][3] > npArr[-k*8][0]
                and npArr[-(k*6+1)][3] < npArr[-k*7][0]
                and npArr[-(k*5+1)][3] < npArr[-k*6][0]
                and npArr[-(k*4+1)][3] < npArr[-k*5][0]
                and npArr[-(k*3+1)][3] > npArr[-k*4][0]
                and npArr[-(k*2+1)][3] > npArr[-k*3][0]
                and npArr[-(k+1)][3] > npArr[-k*2][0]
                and npArr[-1][3] < npArr[-k][3]):
                sell += 1

    if((buy > 0 or sell > 0) and buy != sell):
        return True
    return False
