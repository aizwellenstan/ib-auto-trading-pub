import numpy as np

def WilliamsR(high, low, close, lookback=8):
    """
    Calculate Williams %R indicator.
    
    :param high: numpy array of high prices
    :param low: numpy array of low prices
    :param close: numpy array of close prices
    :param lookback: Lookback period for the Williams %R calculation
    :return: numpy array of Williams %R values
    """
    highest_high = np.zeros_like(close)
    lowest_low = np.zeros_like(close)
    williams_r = np.zeros_like(close)
    
    for i in range(lookback - 1, len(close)):
        highest_high[i] = np.max(high[i - lookback + 1:i + 1])
        lowest_low[i] = np.min(low[i - lookback + 1:i + 1])
        williams_r[i] = -100 * ((highest_high[i] - close[i]) / (highest_high[i] - lowest_low[i]))

    return williams_r