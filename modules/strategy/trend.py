import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr, EmaArr
from modules.trend_direction import GetTrend
from modules.permutationEntropy import permutation_entropy

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 5
    # if tf in ['20 mins']: TP_VAL = 4
    # elif tf in ['30 mins']: TP_VAL = 2
    # elif tf in ['10 mins']: TP_VAL = 5
    if signal > 0:
        op = npArr[-1][0]
        sl = np.min(npArr[-2:][:,2])
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = np.max(npArr[-2:][:,1])
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def calculate_rsi(close_prices, window=14):
    delta = np.diff(close_prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = np.convolve(gain, np.ones((window,))/window, mode='valid')
    avg_loss = np.convolve(loss, np.ones((window,))/window, mode='valid')
    if not np.all(avg_loss): return []

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the RSI array to match the length of the input
    rsi = np.concatenate([np.full(window-1, np.nan), rsi])
    return rsi

def Trend(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    signal = 0
    sma = SmaArr(npArr[:,3][:-1], 50)
    trend = GetTrend(npArr[:-1][:,3][-400:])
    trendVol = GetTrend(npArr[:-1][:,4][-10:])
    if (
        npArr[-2][3] > sma[-1] and
        trend < 0 and
        trendVol > 0
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    elif (
        npArr[-2][3] < sma[-1] and
        trend > 0 and
        trendVol > 0
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        if op == sl: return 0, npArr[-1][0], 0, 0
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
