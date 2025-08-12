import numpy as np

# Function to calculate rolling mean
def rolling_mean(arr, period):
    return np.convolve(arr, np.ones(period)/period, mode='valid')

# Function to calculate rolling std deviation
def rolling_std(arr, period):
    return np.array([np.std(arr[i:i+period]) for i in range(len(arr)-period+1)])

def squeeze(npArr):
    open_prices = npArr[:, 0]
    high_prices = npArr[:, 1]
    low_prices = npArr[:, 2]
    close_prices = npArr[:, 3]

    # Parameters
    period = 24

    # Calculate 20-period SMA
    sma_20 = rolling_mean(close_prices, period)

    # Calculate TR
    tr = np.abs(high_prices - low_prices)

    # Calculate ATR
    atr = rolling_mean(tr, period)

    # Calculate Keltner Channels
    lower_keltner = sma_20 - (atr * 1.5)
    upper_keltner = sma_20 + (atr * 1.5)

    # Calculate stddev for Bollinger Bands
    stddev = rolling_std(close_prices, period)
    lower_band = sma_20 - (2 * stddev)
    upper_band = sma_20 + (2 * stddev)

    # Check for squeeze condition
    squeeze_on = np.logical_and(lower_band > lower_keltner, upper_band < upper_keltner)

    # Check if there is a squeeze
    squeeze = 0
    if len(squeeze_on) > 1 and squeeze_on[-1] and not squeeze_on[-2]:
        squeeze = 1

    return squeeze