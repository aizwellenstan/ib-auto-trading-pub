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
import pandas as pd
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from modules.kernelema import kernelema
from modules.trend_direction import GetTrend
from modules.vwap import Vwap
from modules.strategy.sweep import GetSweep

def GetOPSLTP(npArr, signal, tf, tick_val):
    TP_VAL = 3.5
    if signal > 0:
        op = npArr[-1][0]
        sl = npArr[-2][2]
        tp = op + (op-sl) * TP_VAL
        tp = floor_round(tp, tick_val)
    else:
        op = npArr[-1][0]
        sl = npArr[-2][1]
        tp = op - (sl-op) * TP_VAL
        tp = ceil_round(tp, tick_val)
    return op, sl, tp

def rescale(src, old_min, old_max, new_min, new_max):
    return new_min + (new_max - new_min) * (src - old_min) / max(old_max - old_min, 1e-10)

def calculate_n_rsi(close_p, n1=14):
    delta = np.diff(close_p, prepend=close_p[0])
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.convolve(gain, np.ones(n1)/n1, 'valid')
    avg_loss = np.convolve(loss, np.ones(n1)/n1, 'valid')
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = np.concatenate((np.full(n1-1, np.nan), rsi))
    # return rsi
    return rescale(rsi, 0, 100, 0, 1)

def remove_nan(x):
    return x[~np.isnan(x)]

def normalize(src, min_val, max_val):
    historic_min = 10e10
    historic_max = -10e10
    historic_min = min(historic_min, np.nanmin(src))
    historic_max = max(historic_max, np.nanmax(src))
    return min_val + (max_val - min_val) * (src - historic_min) / max(historic_max - historic_min, 1e-10)

def calculate_n_wt(close_p, n1=10, n2=11):
    ema1 = calculate_ema(close_p, n1)
    ema2 = calculate_ema(np.abs(close_p - ema1), n1)
    ci = (close_p - ema1) / (0.015 * ema2)
    wt1 = calculate_ema(ci, n2)  # tci
    wt2 = np.convolve(wt1, np.ones(4)/4, mode='valid')
    wt2 = np.concatenate((np.full(3, np.nan), wt2))
    return normalize(wt1 - wt2, 0, 1)

def calculate_n_cci(high_p, low_p, close_p, n1=20):
    typical_price = (high_p + low_p + close_p) / 3
    moving_avg = np.convolve(typical_price, np.ones(n1)/n1, 'valid')
    moving_avg = np.concatenate((np.full(n1-1, np.nan), moving_avg))
    mean_deviation = np.array([np.mean(np.abs(typical_price[max(i-(n1-1), 0):i+1] - np.mean(typical_price[max(i-(n1-1), 0):i+1]))) for i in range(len(typical_price))])
    mean_deviation = mean_deviation[mean_deviation != 0]
    minLen = len(mean_deviation)
    typical_price = typical_price[-minLen:]
    moving_avg = moving_avg[-minLen:]
    cci = (typical_price - moving_avg) / (0.015 * mean_deviation)
    return cci
    # return normalize(cci, 0, 1)

def calculate_n_adx(high_p, low_p, close_p, n1=14):
    tr = np.maximum(high_p - low_p, np.maximum(np.abs(high_p - np.roll(close_p, 1)), np.abs(low_p - np.roll(close_p, 1))))
    dm_plus = np.where((high_p - np.roll(high_p, 1)) > (np.roll(low_p, 1) - low_p), np.maximum(high_p - np.roll(high_p, 1), 0), 0)
    dm_minus = np.where((np.roll(low_p, 1) - low_p) > (high_p - np.roll(high_p, 1)), np.maximum(np.roll(low_p, 1) - low_p, 0), 0)
    
    tr = np.convolve(tr, np.ones(n1), 'valid')
    dm_plus = np.convolve(dm_plus, np.ones(n1), 'valid')
    dm_minus = np.convolve(dm_minus, np.ones(n1), 'valid')
    
    di_plus = 100 * dm_plus / tr
    di_minus = 100 * dm_minus / tr
    dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus)
    adx = np.convolve(dx, np.ones(n1)/n1, 'valid')
    return adx
    # return normalize(adx, 0, 1)

# Calculate technical indicators using only numpy
def calculate_technical_indicators(data):
    open_p, high_p, low_p, close_p, volatility_filter, regime_filter = data.T
    
    # Calculate RSI
    # delta = np.diff(close_p, prepend=close_p[0])
    # gain = np.where(delta > 0, delta, 0)
    # loss = np.where(delta < 0, -delta, 0)
    # avg_gain = np.convolve(gain, np.ones(14)/14, 'valid')
    # avg_loss = np.convolve(loss, np.ones(14)/14, 'valid')
    # rs = avg_gain / avg_loss
    # rsi = 100 - (100 / (1 + rs))
    # rsi = np.concatenate((np.full(13, np.nan), rsi))
    rsi = calculate_n_rsi(close_p)
    
    # Calculate Williams %R
    # high_max = np.array([np.max(high_p[max(i-13, 0):i+1]) for i in range(len(high_p))])
    # low_min = np.array([np.min(low_p[max(i-13, 0):i+1]) for i in range(len(low_p))])
    # wt = -100 * (high_max - close_p) / (high_max - low_min)
    
    cci = calculate_n_cci(high_p, low_p, close_p)
    
    # adx = calculate_n_adx(high_p, low_p, close_p)
    ema = EmaArr(close_p[-132:], 9)
    ema12 = EmaArr(close_p[-132:], 15)
    
    # Remove NaNs and align indicators
    rsi = remove_nan(rsi)
    # wt = remove_nan(wt)
    # adx = remove_nan(adx)
    cci = remove_nan(cci)
    # minLen = len(adx)
    minLen = min(len(rsi), len(cci), 124)
    rsi = rsi[-minLen:]
    # wt = wt[-minLen:]
    cci = cci[-minLen:]
    ema = ema[-minLen:]
    ema12 = ema12[-minLen:]
    data = data[-minLen:]
    
    # indicators = np.column_stack((rsi, wt, cci, adx))
    indicators = np.column_stack((rsi, cci, ema, ema12))
    return np.concatenate((data, indicators), axis=1)

# Apply filters using numpy
def apply_filters(data):
    close_p, high_p, low_p = data[:, 3], data[:, 1], data[:, 2]
    
    # Calculate ATR
    tr = np.maximum(high_p - low_p, np.maximum(np.abs(high_p - np.roll(close_p, 1)), np.abs(low_p - np.roll(close_p, 1))))
    atr = np.convolve(tr, np.ones(14)/14, 'valid')
    atr = np.concatenate((np.full(13, np.nan), atr))
    
    recent_atr = np.convolve(atr, np.ones(1)/1, 'valid')
    historical_atr = np.convolve(atr, np.ones(10)/10, 'valid')
    historical_atr = np.concatenate((np.full(9, np.nan), historical_atr))
    
    volatility_filter = recent_atr > historical_atr
    regime_filter = np.abs(np.diff(close_p, prepend=close_p[0])) / (high_p - low_p) >= 0.1
    filters = np.column_stack((volatility_filter, regime_filter))
    return np.concatenate((data, filters), axis=1)

# Prepare the data for machine learning using numpy
def prepare_ml_data(data):
    valid_data = data[~np.isnan(data).any(axis=1)]
    X = valid_data[:, 6:10]  # RSI, WT, CCI, ADX
    y = np.roll(valid_data[:, 3], -1) > valid_data[:, 3]  # 1 for long, 0 for short
    return X, y.astype(int)

def get_lorentzian_distance(x, y, sigma=1.0):
    return np.sum(np.log1p(np.abs(x - y) / sigma))

# Train machine learning model
def train_ml_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    # model = KNeighborsClassifier(n_neighbors=8)
    model = KNeighborsClassifier(n_neighbors=8, metric=lambda x, y: get_lorentzian_distance(x, y))
    model.fit(X_train, y_train)
    return model

# Generate the last signal using numpy
def generate_last_signal(data, model):
    X = data[-1:, 6:10]  # RSI, WT, CCI, ADX for the last row
    prediction = model.predict(X)[0]
    
    volatility_filter, regime_filter = data[-1, 4], data[-1, 5]
    last_signal = 1 if volatility_filter and regime_filter and prediction == 1 else -1 if volatility_filter and regime_filter else 0
    return last_signal

# Main function to run the entire process
def Signal(npArr):
    npArr = npArr[:,:4].astype(float)
    data = apply_filters(npArr)
    if not (data[-1][-1] and data[-1][-2]): return 0
    data = calculate_technical_indicators(data)
    
    X, y = prepare_ml_data(data)
    model = train_ml_model(X, y)
    
    last_signal = generate_last_signal(data, model)
    
    return last_signal

def Lz(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 200
    # if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 2:
        #     sma100 = SmaArr(npArr[:-1][:,3], 100)
        # ema200 = EmaArr(npArr[:-1][:,3][-201:], 200)
        lzSignal = Signal(npArr[:-1][-150:])
        trend = GetTrend(npArr[:-1][:,3][-200:])
        # ema = EmaArr(npArr[:-1][:,3][-16:], 15)
        vwapPeriod = 50
        npArrC = npArr[:-1]
        npArrC = npArrC[npArrC[:, 4] != 0]
        vwap = Vwap(npArrC[:,4][-vwapPeriod:],npArrC[:,1][-vwapPeriod:],npArrC[:,2][-vwapPeriod:])
        if (
            lzSignal > 0 and
            trend > 0 and
            npArr[-2][3] < vwap[-1] and
            npArr[-3][3] > npArr[-3][0]
        ):
            signal = 1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
        elif (
            lzSignal < 0 and
            trend < 0 and
            npArr[-2][3] > vwap[-1] and
            npArr[-3][3] < npArr[-3][0]
        ):
            signal = -1
            op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
            return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def HpLz(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 200
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    # if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 2:
        #     sma100 = SmaArr(npArr[:-1][:,3], 100)
        # ema200 = EmaArr(npArr[:-1][:,3][-201:], 200)
    lzSignal = Signal(npArr[:-1][-150:])
    trend = GetTrend(npArr[:-1][:,3][-200:])
    # ema = EmaArr(npArr[:-1][:,3][-16:], 15)
    vwapPeriod = 50
    npArrC = npArr[:-1]
    npArrC = npArrC[npArrC[:, 4] != 0]
    vwap = Vwap(npArrC[:,4][-vwapPeriod:],npArrC[:,1][-vwapPeriod:],npArrC[:,2][-vwapPeriod:])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 1
    if (
        lzSignal > 0 and
        trend > 0 and
        npArr[-2][3] < vwap[-1] and
        npArr[-3][3] > npArr[-3][0]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        lzSignal < 0 and
        trend < 0 and
        npArr[-2][3] > vwap[-1] and
        npArr[-3][3] < npArr[-3][0]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0
