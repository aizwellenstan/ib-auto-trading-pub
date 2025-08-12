import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.rsi import GetRsi
from modules.permutationEntropy import permutation_entropy
from modules.movingAverage import SmaArr, EmaArr
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 1.5
    # if tf in ['20 mins']: TP_VAL = 4
    # if tf in ['15 mins']: TP_VAL = 1.5
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
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Pad the RSI array to match the length of the input
    rsi = np.concatenate([np.full(window-1, np.nan), rsi])
    return rsi

def calculate_cci(high_p, low_p, close_p, n1=20):
    typical_price = (high_p + low_p + close_p) / 3
    moving_avg = np.convolve(typical_price, np.ones(n1)/n1, 'valid')
    moving_avg = np.concatenate((np.full(n1-1, np.nan), moving_avg))
    mean_deviation = np.array([np.mean(np.abs(typical_price[max(i-(n1-1), 0):i+1] - np.mean(typical_price[max(i-(n1-1), 0):i+1]))) for i in range(len(typical_price))])
    mean_deviation = mean_deviation[mean_deviation != 0]
    minLen = len(mean_deviation)
    if minLen < 1: return []
    typical_price = typical_price[-minLen:]
    moving_avg = moving_avg[-minLen:]
    cci = (typical_price - moving_avg) / (0.015 * mean_deviation)
    return cci

def Cci(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    period = 2
    cci = calculate_cci(npArr[:-1][:,1][-period-1:],npArr[:-1][:,2][-period-1:],npArr[:-1][:,3][-period-1:],period)
    if len(cci) < 1: return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        cci[-1] > 90
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 2:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        cci[-1] < 10
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 2:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def FadeCci(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    period = 15
    cci = calculate_cci(npArr[:-1][:,1][-period-1:],npArr[:-1][:,2][-period-1:],npArr[:-1][:,3][-period-1:],period)
    if len(cci) < 1: return 0, npArr[-1][0], 0, 0
    ema = EmaArr(npArr[:-1][:,3][-9:], 7)
    if (
        cci[-1] > 70 and
        cci[-1] < 96 and
        npArr[-2][1] > npArr[-3][1] and
        npArr[-3][3] > ema[-2] and
        npArr[-2][3] > ema[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    elif (
        cci[-1] < 30 and
        cci[-1] > 4 and
        npArr[-2][2] < npArr[-3][2] and
        npArr[-3][3] < ema[-2] and
        npArr[-2][3] < ema[-1]
    ):
        pe = permutation_entropy(npArr[:-1][-212:][:,3])
        sma = SmaArr(pe, 40)
        if pe[-1] > sma[-1]:
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