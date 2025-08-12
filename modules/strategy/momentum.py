import os;from pathlib import Path
rootPath = Path(os.path.dirname(__file__)).parent.parent
import sys;sys.path.append(os.path.relpath(rootPath, os.path.dirname(__file__)))
from modules.trade.utils import floor_round, ceil_round
import numpy as np
from modules.atr import ATR
from modules.movingAverage import SmaArr, EmaArr
from modules.trend_direction import GetTrend
from modules.permutationEntropy import permutation_entropy
import hurst as hs
from scipy.stats import entropy

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 2
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

class ZeroLagExponentialMovingAverage:
    def __init__(self, prices, period):
        self.prices = prices
        self.period = period
        self.zlema = self.calculate_zlema()

    def ema(self, data):
        k = 2 / (self.period + 1)
        ema_values = [data[0]]  # Start with the first price as the initial EMA
        for price in data[1:]:
            new_ema = (price * k) + (ema_values[-1] * (1 - k))
            ema_values.append(new_ema)
        return ema_values

    def calculate_zlema(self):
        lag = (self.period - 1) // 2
        adjusted_data = [2 * self.prices[i] - self.prices[i - lag] if i >= lag else None for i in range(len(self.prices))]
        return self.ema([x for x in adjusted_data if x is not None])

def calculate_momentum(prices, period=14):
    if len(prices) < period:
        raise ValueError("Price array is shorter than the specified period.")
    
    return prices[period:] - prices[:-period]

def Calculate_Hurst(var_values, window_size, ser_type):

    H, c, data = hs.compute_Hc(var_values, kind=ser_type, simplified=True)
    
    return H

def calculate_entropy(closeArr, base=2):
    value, counts = np.unique(closeArr, return_counts=True)
    return entropy(counts, base=base)

def moving_average(data, window):
    return [np.mean(data[i-window:i]) if i >= window else None for i in range(len(data))]

# Function to calculate standard deviation
def std_dev(data, window):
    return [np.std(data[i-window:i]) if i >= window else None for i in range(len(data))]

# TTM Squeeze calculation
def ttm_squeeze(closes, window=20, num_sd=2):

    # Calculate SMA and Bollinger Bands
    sma = moving_average(closes, window)
    bb_upper = [sma[i] + (std_dev(closes, window)[i] * num_sd) if sma[i] is not None else None for i in range(len(sma))]
    bb_lower = [sma[i] - (std_dev(closes, window)[i] * num_sd) if sma[i] is not None else None for i in range(len(sma))]

    # Calculate Keltner Channels
    kc_ma = moving_average(closes, window)
    atr = [np.mean(closes[i-window:i]) if i >= window else None for i in range(len(closes))]  # Approximation of ATR
    kc_upper = [kc_ma[i] + (atr[i] * 1.5) if kc_ma[i] is not None else None for i in range(len(kc_ma))]
    kc_lower = [kc_ma[i] - (atr[i] * 1.5) if kc_ma[i] is not None else None for i in range(len(kc_ma))]

    # Determine squeeze condition
    squeeze_on = [bb_upper[i] < kc_upper[i] and bb_lower[i] > kc_lower[i] if bb_upper[i] is not None and bb_lower[i] is not None and kc_upper[i] is not None and kc_lower[i] is not None else None for i in range(len(bb_upper))]
    return squeeze_on[-1]

def Momentum(npArr, tf, tick_val=0.25):
    if len(npArr) < 234:
        return 0, npArr[-1][0], 0, 0

    # ttmSqueeze = ttm_squeeze(npArr[:-1][:,3][-21:])
    # if not ttmSqueeze: return 0, npArr[-1][0], 0, 0
    # window_size = 100  # Example window size
    
    

    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 4.5:
        signal = 0
        # sma = SmaArr(npArr[:,3][:-1], 50)
        sma10 = SmaArr(npArr[:-1][:,3][-11:], 10)
        sma25 = SmaArr(npArr[:-1][:,3][-26:], 25)
        # trend = GetTrend(npArr[:-1][:,3][-400:])
        # trendVol = GetTrend(npArr[:-1][:,4][-10:])
        # period = 50
        # zlema = ZeroLagExponentialMovingAverage(npArr[:-1][:,3][-period-10:], period).zlema
        # momentum = calculate_momentum(npArr[:-1][:,3][-16:])
        # if np.any(npArr[:-1][:,4][-100:]): return 0, npArr[-1][0], 0, 0
        H, c, data = hs.compute_Hc(npArr[:-1][:,3][-100:], kind='price', simplified=True)
        # en = calculate_entropy(npArr[:-1][:,3][-109:])
        if (
            # npArr[-3][3] < sma[-2] and
            # npArr[-2][3] > sma[-1] and
            sma10[-1] < sma25[-1] and
            H > 0.5
            # en > 2.6
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = 1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                if op == sl: return 0, npArr[-1][0], 0, 0
                return signal, op, sl, tp
        elif (
            # npArr[-2][3] < sma[-1] and
            sma10[-1] > sma25[-1] and
            H < 0.5
            # en < 2.6
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                signal = -1
                op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                if op == sl: return 0, npArr[-1][0], 0, 0
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
