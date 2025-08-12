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
    # elif tf in ['30 mins']: TP_VAL = 2
    # elif tf in ['10 mins']: TP_VAL = 5
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


import numpy as np
from scipy import linalg as la

def pca_linear_model(x: np.ndarray, y: np.ndarray, n_components: int, thresh: float = 0.01):
    # Center data at 0
    means = np.mean(x, axis=0)
    x -= means

    # Find covariance and compute eigen vectors
    cov = np.cov(x, rowvar=False)
    evals, evecs = la.eigh(cov)
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:, idx]
    evals = evals[idx]

    model_data = np.dot(x, evecs[:, :n_components])
    model_coefs = la.lstsq(model_data, y, rcond=None)[0]

    pred = np.dot(model_data, model_coefs)
    l_thresh = np.quantile(pred, 0.99)
    s_thresh = np.quantile(pred, 0.01)

    return model_coefs, evecs, means, l_thresh, s_thresh, pred

def pca_rsi_model(close: np.ndarray, rsi_lbs, train_size: int, step_size: int,
                  n_components: int = 2, lookahead: int = 6) -> np.ndarray:
    
    rsis = np.zeros((len(close), len(rsi_lbs)))

    # Compute RSI values
    for i, lb in enumerate(rsi_lbs):
        tmp = calculate_rsi(close, lb)
        if len(tmp) >= len(rsis):
            rsis[:, i] = tmp[-len(rsis):]

    tar = np.log(close[lookahead:]) - np.log(close[:-lookahead])
    signals = np.zeros(len(close))

    for i in range(train_size, len(close) - lookahead):
        if i % step_size == 0:
            train_data = rsis[i - train_size:i]
            y = tar[i - train_size:i]
            model_coefs, evecs, rsi_means, l_thresh, s_thresh, _ = pca_linear_model(train_data, y, n_components)

        curr_row = rsis[i] - rsi_means
        vec = np.dot(curr_row, evecs[:, :n_components])
        curr_pred = np.dot(vec, model_coefs)

        if curr_pred > l_thresh:
            signals[i] = 1
        elif curr_pred < s_thresh:
            signals[i] = -1

    return signals

def generate_signals(npArr: np.ndarray, rsi_lbs, train_size: int, step_size: int, 
                     n_components: int = 2, lookahead: int = 6) -> np.ndarray:
    return pca_rsi_model(npArr, rsi_lbs, train_size, step_size, n_components, lookahead)

def calculate_rsi(close_prices, period=14):
    """Calculate the Relative Strength Index (RSI) for given closing prices."""
    deltas = np.diff(close_prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[-period:]) if len(gains) >= period else np.mean(gains)
    avg_loss = np.mean(losses[-period:]) if len(losses) >= period else np.mean(losses)

    if avg_loss == 0:
        return 100  # Avoid division by zero; RSI is 100 if no losses

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def backtest_rsi(close_prices, period=14):
    """Backtest the RSI strategy based on the given conditions."""
    rsi_values = []
    returns1 = []
    returns2 = []

    # Calculate RSI for each position in the close_prices
    for i in range(len(close_prices)):
        if i >= period - 1:
            rsi = calculate_rsi(close_prices[:i + 1], period)
            rsi_values.append(rsi)
        else:
            rsi_values.append(None)

    # Simulating trades based on the two conditions
    for i in range(1, len(close_prices)):
        current_rsi = rsi_values[i - 1]

        # Condition 1: RSI < 50, Buy; RSI > 50, Sell
        if current_rsi is not None and current_rsi < 50:
            buy_price = close_prices[i]
            for j in range(i + 1, len(close_prices)):
                if rsi_values[j] is not None and rsi_values[j] > 50:
                    returns1.append((close_prices[j] - buy_price) / buy_price)
                    break

        # Condition 2: RSI > 50, Buy; RSI < 50, Sell
        elif current_rsi is not None and current_rsi > 50:
            buy_price = close_prices[i]
            for j in range(i + 1, len(close_prices)):
                if rsi_values[j] is not None and rsi_values[j] < 50:
                    returns2.append((close_prices[j] - buy_price) / buy_price)
                    break

    returns1 = np.array(returns1)
    returns2 = np.array(returns2)

    # Evaluate conditions for return value
    return1 = 0
    if returns1.size > 0:
        return1 = returns1.mean()
    return2 = 0
    if returns2.size > 0:
        return2 = returns2.mean()
    if return1 > 0 and return1 > abs(return2) * 2:
        if rsi_values[-1] < 50: return 1
        elif rsi_values[-1] > 50: return -1
        else: return 0
    if return2 > 0 and return2 > abs(return1) * 2:
        if rsi_values[-1] > 50: return 1
        elif rsi_values[-1] < 50: return -1
        else: return 0
    else:
        return 0

def DynamicRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    signal = backtest_rsi(npArr[:-1][:,3][-14:], 7)
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.7
    if (
        signal > 0 and
        npArr[-2][1] > npArr[-3][1]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 2:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        signal < 0 and
        npArr[-2][2] < npArr[-3][2]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 2:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def PcaRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    rsi = calculate_rsi(npArr[:-1][:,3][-8:], 7)
    if len(rsi) < 1: return 0, npArr[-1][0], 0, 0
    signals = generate_signals(npArr[:-1][:,3], list(range(2, 25)), 24 * 365 * 2, 24 * 365)
    # sma = SmaArr(npArr[:-1][:,3], 50)
    if (
        signals[-1] > 0
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = 1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    elif (
        signals[-1] < 0
    ):
        # pe = permutation_entropy(npArr[:-1][-212:][:,3])
        # sma = SmaArr(pe, 40)
        # if pe[-1] < sma[-1]:
        signal = -1
        op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
        return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def Rsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    rsi = calculate_rsi(npArr[:-1][-7:][:,3], 7)
    if len(rsi) < 1: return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        rsi[-1] > 90
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 2:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        rsi[-1] < 10
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 2:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def ExtremeRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    rsiHigh = calculate_rsi(npArr[:-1][-8:][:,1], 4)
    rsiLow = calculate_rsi(npArr[:-1][-8:][:,2], 4)
    if len(rsiHigh) < 1: return 0, npArr[-1][0], 0, 0
    if len(rsiLow) < 1: return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        rsiLow[-1] > 60
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 2:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        rsiHigh[-1] < 40
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 2:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def hurstExponent(prices):
    Rn = np.cumsum(prices)
    S = np.std(prices)
    hursts = ((np.log(Rn/S)) / np.log(prices)) - 0.5
    return hursts[-1]

def HurstRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    rsiHigh = calculate_rsi(npArr[:-1][-8:][:,1], 3)
    rsiLow = calculate_rsi(npArr[:-1][-8:][:,2], 3)
    if len(rsiHigh) < 1: return 0, npArr[-1][0], 0, 0
    if len(rsiLow) < 1: return 0, npArr[-1][0], 0, 0
    period = 4
    hurstsHigh = hurstExponent(rsiHigh[-period:])
    hurstsLow = hurstExponent(rsiLow[-period:])
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    if (
        rsiLow[-1] > 60 and
        hurstsHigh < 0.5
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 2:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        rsiHigh[-1] < 40 and
        hurstsLow < 0.5
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 2:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def RsiMa(npArr, tf, tick_val=0.25):
    if len(npArr) < 192 or npArr[-2][5] < 1 or npArr[-3][5] < 1:
        return 0, npArr[-1][0], 0, 0
    # atrPeriod = 100
    # if tf in ['5 mins']: atrPeriod = 200
    # atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:,2][-atrPeriod:],npArr[:,3][-atrPeriod:])
    # if np.max(npArr[-3:][:,1]) - np.min(npArr[-3:][:,2]) > atr * 3:
    rsi = calculate_rsi(npArr[:-1][-40:][:,3], 7)
    if len(rsi) < 1: return 0, npArr[-1][0], 0, 0
    op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr, 30, tick_val)
    rr = 2.1
    sma = SmaArr(rsi, 20)
    if (
        rsi[-2] < sma[-2] and
        rsi[-1] > sma[-1]
    ):
        signal = 1
        tp = op + maxRangeLong
        sl = npArr[-2][2]
        if op - sl > tick_val * 2:
            slippage = tick_val * 2
            if (tp - op - slippage) / (op - sl + slippage) > rr:
                return signal, op, sl, tp
    elif (
        rsi[-2] > sma[-2] and
        rsi[-1] < sma[-1]
    ):
        signal = -1
        tp = op - maxRangeShort
        sl = npArr[-2][1]
        if sl - op > tick_val * 2:
            slippage = tick_val * 2
            if (op - tp - slippage) / (sl - op + slippage) > rr:
                return signal, op, sl, tp
    return 0, npArr[-1][0], 0, 0

def FadeRsi(npArr, tf, tick_val=0.25):
    if len(npArr) < 192:
        return 0, npArr[-1][0], 0, 0
    atrPeriod = 100
    if tf in ['5 mins']: atrPeriod = 200
    atr = ATR(npArr[:-1][:,1][-atrPeriod:],npArr[:-1][:,2][-atrPeriod:],npArr[:-1][:,3][-atrPeriod:])
    if np.max(npArr[:-1][-2:][:,1]) - np.min(npArr[:-1][-2:][:,2]) > atr * 3:
        rsi = calculate_rsi(npArr[:-1][:,3][-14:], 14)
        if len(rsi) < 1: return 0, npArr[-1][0], 0, 0
        # sma = SmaArr(npArr[:-1][:,3], 50)
        # ema = EmaArr(npArr[:-1][:,3][-9:], 7)
        op, maxRRLong, maxRangeLong, maxRRShort, maxRangeShort = GetSweep(npArr)
        rr = 2.5
        if (
            rsi[-1] < 30 and
            rsi[-1] > 20
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                tp = op + maxRangeLong
                sl = npArr[-2][2]
                if op - sl > tick_val:
                    slippage = tick_val * 2
                    if (tp - op - slippage) / (op - sl + slippage) > rr:
                        signal = 1
                        # op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                        
                        return signal, op, sl, tp
        elif (
            rsi[-1] > 70 and
            rsi[-1] < 80
        ):
            pe = permutation_entropy(npArr[:-1][-212:][:,3])
            sma = SmaArr(pe, 40)
            if pe[-1] < sma[-1]:
                tp = op - maxRangeShort
                sl = npArr[-2][1]
                if sl - op > tick_val:
                    slippage = tick_val * 2
                    if (op - tp - slippage) / (sl - op + slippage) > rr:
                        signal = -1
                        # op, sl, tp = GetOPSLTP(npArr, signal, tf, tick_val)
                       
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