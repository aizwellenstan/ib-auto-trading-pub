import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.kernelema import kernelema
from modules.atr import ATR
from modules.rsi import GetRsi
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 1.2
    # if tf in ['20 mins']: TP_VAL = 4
    # elif tf in ['30 mins']: TP_VAL = 2
    # elif tf in ['10 mins']: TP_VAL = 5
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

def ExtremeKernel(npArr, tf, tick_val=0.25):
    if len(npArr) < 32 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # maHigh = EmaArr(npArr[:-1][:,1][-4:], 3)
    # maLow = EmaArr(npArr[:-1][:,2][-4:], 3)
    period = 7
    maHigh = kernelema(npArr[:-1][:,1][-period-1:], period)
    maLow = kernelema(npArr[:-1][:,2][-period-1:], period)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        npArr[-2][3] > maHigh
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        npArr[-2][3] < maLow
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def KernelEma(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 4:
    # rsi = calculate_rsi(npArr[:-1][:,3], 7)
    # sma = SmaArr(npArr[:-1][:,3], 50)
        period = 20
        ema = kernelema(npArr[:-1][:,3][-period-1:], period)
        ema2 = kernelema(npArr[:-1][:,3][-period-1:], 50)
        if (
            ema < ema2 and
            npArr[-2][3] > ema and
            npArr[-4][3] > npArr[-4][0] and
            npArr[-3][3] < npArr[-3][0] and
            npArr[-2][3] > npArr[-2][0]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
        elif (
            ema > ema2 and
            npArr[-2][3] < ema and
            npArr[-4][3] < npArr[-4][0] and
            npArr[-3][3] > npArr[-3][0] and
            npArr[-2][3] < npArr[-2][0]
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] > sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def FadeRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        rsi = calculate_rsi(npArr[:-1][:,3][-8:], 7)
        sma = SmaArr(npArr[:-1][:,3], 50)
        if (
            rsi[-1] > 60 and
            rsi[-1] < 90
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            rsi[-1] < 40 and
            rsi[-1] > 10
        ):
            # pe = permutation_entropy(npArr[:-1][-212:][:,3])
            # sma = SmaArr(pe, 40)
            # if pe[-1] < sma[-1]:
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0


def detect_divergences(prices, lookback_left=5, lookback_right=5):
    rsi = calculate_rsi(prices)
    
    # Initialize signal variable
    latest_signal = 0
    
    for i in range(lookback_right, len(prices) - lookback_right):
        price_range = prices[i-lookback_left:i+lookback_right+1]
        rsi_range = rsi[i-lookback_left:i+lookback_right+1]
        
        if (rsi[i-lookback_right] > np.max(rsi_range[:lookback_left]) and
            prices[i-lookback_right] < np.min(price_range[:lookback_left])):
            latest_signal = 1  # Bullish divergence
        
        if (rsi[i-lookback_right] < np.min(rsi_range[:lookback_left]) and
            prices[i-lookback_right] > np.max(price_range[:lookback_left])):
            latest_signal = -1  # Bearish divergence
    
    return latest_signal

def RsiDivergence(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
        # rsi = GetRsi(npArr[:-1][:,3], 7)
        # sma = SmaArr(npArr[:-1][:,3], 50)
    rsi_divergences = detect_divergences(npArr[:-1][:,3][-212:])
    if (
        rsi_divergences > 0
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] > sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        rsi_divergences < 0
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] > sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0