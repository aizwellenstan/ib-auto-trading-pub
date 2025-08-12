import numpy as np
import matplotlib.pyplot as plt
import scipy 

def hawkes_process(data: np.ndarray, kappa: float) -> np.ndarray:
    assert(kappa > 0.0)
    alpha = np.exp(-kappa)
    arr = np.copy(data)
    output = np.full(len(data), np.nan)
    
    for i in range(1, len(data)):
        if np.isnan(output[i - 1]):
            output[i] = arr[i]
        else:
            output[i] = output[i - 1] * alpha + arr[i]
    
    return output * kappa

def rolling_quantile(arr: np.ndarray, window: int, q: float) -> np.ndarray:
    """Calculate rolling quantile for a 1D numpy array."""
    result = np.full_like(arr, np.nan)
    for i in range(window - 1, len(arr)):
        
        result[i] = np.quantile(arr[i - window + 1:i + 1], q)
    return result

def vol_signal(close: np.ndarray, vol_hawkes: np.ndarray, lookback: int) -> np.ndarray:
    signal = np.zeros(len(close))
    q05 = rolling_quantile(vol_hawkes, lookback, 0.05)
    q95 = rolling_quantile(vol_hawkes, lookback, 0.95)
    
    last_below = -1
    curr_sig = 0

    for i in range(len(signal)):
        if vol_hawkes[i] < q05[i]:
            last_below = i
            curr_sig = 0

        if (i > 0 and vol_hawkes[i] > q95[i] and vol_hawkes[i - 1] <= q95[i - 1] and last_below > 0):
            change = close[i] - close[last_below]
            curr_sig = 1 if change > 0.0 else -1
        
        signal[i] = curr_sig

    return signal

def calculate_atr(data, period=14):
    high_low = data[:, 1] - data[:, 2]  # High - Low
    high_prev_close = np.abs(data[:, 1] - np.roll(data[:, 3], 1))  # High - Previous Close
    low_prev_close = np.abs(data[:, 2] - np.roll(data[:, 3], 1))  # Low - Previous Close

    tr = np.maximum(high_low, np.maximum(high_prev_close, low_prev_close))
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')
    return atr

def GetVolatilityHawkesSignal(npArr: np.ndarray, norm_lookback=336) -> np.ndarray:
    npArr = npArr[:,:4]
    # Extract relevant columns
    open_, high, low, close = npArr.T

    # Calculate ATR
    atr = calculate_atr(npArr, norm_lookback)
    atrLen = len(atr)
    high = high[-atrLen:]
    low = low[-atrLen:]
    # Normalize volume
    norm_range = (high - low) / atr
    vHawk = hawkes_process(norm_range, 0.1)
    close = close[-len(vHawk):]
    
    sig = vol_signal(close, vHawk, 168)
    return sig
