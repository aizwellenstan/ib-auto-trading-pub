import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.rsi import GetRsi
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr

def Atr(data, period):
    close_p, high_p, low_p = data[:, 3], data[:, 1], data[:, 2]
    tr = np.maximum(high_p - low_p, np.maximum(np.abs(high_p - np.roll(close_p, 1)), np.abs(low_p - np.roll(close_p, 1))))
    atr = np.convolve(tr, np.ones(period)/period, 'valid')
    return atr
    # recent_atr = np.convolve(atr, np.ones(1)/1, 'valid')
    # historical_atr = np.convolve(atr, np.ones(10)/10, 'valid')
    # historical_atr = np.concatenate((np.full(9, np.nan), historical_atr))
    
    # volatility_filter = recent_atr > historical_atr

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

def calculate_rsi(close_prices, window=14):
    delta = np.diff(close_prices)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = np.convolve(gain, np.ones((window,))/window, mode='valid')
    avg_loss = np.convolve(loss, np.ones((window,))/window, mode='valid')
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the RSI array to match the length of the input
    rsi = np.concatenate([np.full(window-1, np.nan), rsi])
    return rsi

def AtrVolume(npArr, tf, tick_val=0.25):
    if len(npArr) < 203:
        return 0, npArr[-1][0], 0, 0
    period = 50
    
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    atr = Atr(npArr[:-1], 20)[-period:]
    volume = npArr[:-1][:,4][-len(atr):]
    avgAtrVolume = np.mean(atr/volume)
    gain = npArr[-2][3] / npArr[-2-period][3]
    # rsi = calculate_rsi(npArr[:-1][:,3], 7)
    sma = SmaArr(npArr[:-1][:,3], 50)
    if (
        atr[-1] / volume[-1] < avgAtrVolume and
        gain > 1 and
        npArr[-2][3] > sma[-1]
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        atr[-1] / volume[-1] < avgAtrVolume and
        gain < 1 and
        npArr[-2][3] < sma[-1]
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
