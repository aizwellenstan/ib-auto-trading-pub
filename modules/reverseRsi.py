import numpy as np

rsi_length = 25
rsi_level = 50.0

def GetReverseRsi(close):
    delta = np.diff(close)
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    avg_gain = np.convolve(gain, np.ones(rsi_length)/rsi_length, mode='full')[:-rsi_length+1]
    avg_loss = np.convolve(loss, np.ones(rsi_length)/rsi_length, mode='full')[:-rsi_length+1]
    # Avoid division by zero
    avg_loss[avg_loss == 0] = np.nan
    rs = np.divide(avg_gain, avg_loss, out=np.zeros_like(avg_gain), where=avg_loss != 0)
    rsi = 100 - (100 / (1 + rs))

    # Calculate Reverse RSI
    ema_length = (2 * rsi_length) - 1
    up = np.maximum(np.append([0], np.diff(close)), 0)
    dn = np.maximum(np.append([0], -np.diff(close)), 0)
    up_ema = np.convolve(up, np.ones(ema_length)/ema_length, mode='valid')
    dn_ema = np.convolve(dn, np.ones(ema_length)/ema_length, mode='valid')
    x = (rsi_length - 1) * (dn_ema * rsi_level / (100 - rsi_level) - up_ema)
    rev_rsi = np.empty_like(close)
    rev_rsi[:ema_length-1] = np.nan  # Pad with NaNs
    rev_rsi[ema_length-1:] = close[ema_length-1:] + np.where(x >= 0, x, x * ((100 - rsi_level) / rsi_level))

    return rev_rsi