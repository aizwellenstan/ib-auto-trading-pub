import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.macd import MacdHistorical
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr
from modules.entropy import Entropy

def GetOPSLTP(npArr, signal, tf, tick_val):
    # TP_VAL = 6.972
    TP_VAL = 1.33
    if tf in ['20 mins']: TP_VAL = 4
    elif tf in ['30 mins']: TP_VAL = 2
    elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-2:][:,2])
        tp = op + (op-sl) * TP_VAL
        # sl = np.min(npArr[-4:][:,2]) - tick_val * 140
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-2:][:,1])
        tp = op - (sl-op) * TP_VAL
        # sl = np.max(npArr[-4:][:,1]) + tick_val * 140
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def FadeRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        sma100 = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] > sma100[-1]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            npArr[-3][3] < sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def MaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        sma100 = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-3][3] < sma100[-2] and
            npArr[-2][3] > sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

# 15 mins 20 mins
def MaCrossHTF(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        sma100 = SmaArr(npArr[:-1][:,3], 100)
        if (
            npArr[-3][3] < sma100[-2] and
            npArr[-2][3] > sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            npArr[-3][3] > sma100[-2] and
            npArr[-2][3] < sma100[-1]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SimpleMaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
        sma10 = SmaArr(npArr[:-1][:,3], 10)
        sma25 = SmaArr(npArr[:-1][:,3], 25)
        if (
            (sma10[-2] < sma25[-2] and
            sma10[-1] > sma25[-1]) or
           (sma10[-1] < sma25[-1] and
            npArr[-2][3] > sma25[-1] and
            npArr[-2][3] > sma10[-1])
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            (sma10[-2] > sma25[-2] and
            sma10[-1] < sma25[-1]) or
            (sma10[-1] > sma25[-1] and
            npArr[-2][3] < sma25[-1] and
            npArr[-2][3] < sma10[-1])
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def OriSimpleMaCross(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['5 mins']: atrPeriod = 7
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 6)
    # if atr > 2: return 0, npArr[-1][0], 0, 0
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
    sma10 = SmaArr(npArr[:-1][:,3], 11)
    sma25 = SmaArr(npArr[:-1][:,3], 25)
    if (
        sma10[-2] < sma25[-2] and
        sma10[-1] > sma25[-1] and not
        (
            npArr[-3][4] > npArr[-4][4] * 2 and
            npArr[-2][4] > npArr[-4][4] * 2
        )
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        sma10[-2] > sma25[-2] and
        sma10[-1] < sma25[-1] and not
        (
            npArr[-3][4] > npArr[-4][4] * 2 and
            npArr[-2][4] > npArr[-4][4] * 2
        )
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SmaFr(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:], 6)
    # if atr > 2: return 0, npArr[-1][0], 0, 0
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    sma100 = SmaArr(npArr[:-1][:,3], 100)
    sma25 = SmaArr(npArr[:-1][:,3], 25)
    sma10 = SmaArr(npArr[:-1][:,3], 10)
    if (
        npArr[-2][3] > sma100[-1] and
        npArr[-2][3] < sma25[-1] and
        npArr[-2][3] < sma10[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    elif (
        npArr[-2][3] < sma100[-1] and
        npArr[-2][3] > sma25[-1] and
        npArr[-2][3] > sma10[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SimpleMaCrossOver(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    sma10 = SmaArr(npArr[:-1][:,3][-11:], 10)
    sma25 = SmaArr(npArr[:-1][:,3][-26:], 25)
    if (
        sma10[-2] < sma25[-2] and
        sma10[-1] > sma25[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        sma10[-2] > sma25[-2] and
        sma10[-1] < sma25[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def SmaSR(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    sma75 = SmaArr(npArr[:-1][:,3][-201:], 200)
    if (
        npArr[-2][2] < sma75[-1] and
        npArr[-2][3] > sma75[-1]
    ):
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        npArr[-2][1] > sma75[-1] and
        npArr[-2][3] < sma75[-1]
    ):
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def calculate_z_score(npArr, period=200):
    # Ensure npArr is a NumPy array
    npArr = np.array(npArr)

    # Extract Open, High, Low, and Close columns
    Open, High, Low, Close = npArr[:, 0], npArr[:, 1], npArr[:, 2], npArr[:, 3]

    # Calculate the rolling standard deviation of the Close prices
    def rolling_std(arr, period):
        return np.convolve(arr, np.ones(period)/period, mode='valid')

    # Calculate True Range (TR)
    def true_range(high, low, prev_close):
        return np.maximum(high - low, np.maximum(np.abs(high - prev_close), np.abs(low - prev_close)))
    
    # Calculate ATR
    def average_true_range(tr, period):
        return np.convolve(tr, np.ones(period)/period, mode='valid')

    # Calculate the standard deviation
    std_close = rolling_std(Close, period)
    
    # Calculate True Range (TR)
    prev_close = np.roll(Close, shift=1)
    prev_close[0] = Close[0]  # Handle the first value which does not have a previous close
    tr = true_range(High, Low, prev_close)
    
    # Calculate ATR
    atr = average_true_range(tr, period)
    
    # Extend std_close and atr to match length for subtraction
    std_close = std_close[:len(atr)]  # Trim std_close to the length of atr
    
    # Calculate the difference between standard deviation and ATR
    diff = std_close - atr
    
    # Calculate the mean and standard deviation of the difference
    diff_mean = np.mean(diff)
    diff_std = np.std(diff)
    
    # Calculate Z-score
    z_score = (diff - diff_mean) / diff_std
    
    return z_score

def Ma50ma200cross(npArr, tf, tick_val=0.25):
    if len(npArr) < 202:
        return 0, npArr[-1][0], 0, 0
    z_score = calculate_z_score(npArr[:-1])
    if z_score[-1] < -0.38:
        sma50 = SmaArr(npArr[:-1][:,3][-51:], 10)
        sma200 = SmaArr(npArr[:-1][:,3][-201:], 25)
        if (
            sma50[-2] < sma200[-2] and
            sma50[-1] > sma200[-1]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            sma50[-2] > sma200[-2] and
            sma50[-1] < sma200[-1]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0