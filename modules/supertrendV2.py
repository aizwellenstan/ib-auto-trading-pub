import numpy as np

def atr(high, low, close, period):
    # Calculate True Range (TR)
    tr = np.maximum(high - low, np.maximum(np.abs(high - np.roll(close, 1)), np.abs(low - np.roll(close, 1))))
    tr[0] = np.nan  # First value has no previous close, set to NaN

    # Calculate ATR
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')
    atr = np.concatenate([np.full(period-1, np.nan), atr])
    return atr

def supertrend(npArr, period=10, atr_multiplier=3):
    npArr = npArr[:,:4]
    # Extract columns
    Open, High, Low, Close = npArr.T

    # Calculate HL2
    hl2 = (High + Low) / 2

    # Calculate ATR
    atr_values = atr(High, Low, Close, period)

    # Initialize arrays for supertrend calculations
    upperband = np.full_like(Close, np.nan)
    lowerband = np.full_like(Close, np.nan)
    in_uptrend = np.full_like(Close, False)

    for i in range(period-1, len(Close)):
        upperband[i] = hl2[i] + (atr_multiplier * atr_values[i])
        lowerband[i] = hl2[i] - (atr_multiplier * atr_values[i])

    for i in range(period, len(Close)):
        if Close[i] > upperband[i-1]:
            in_uptrend[i] = True
        elif Close[i] < lowerband[i-1]:
            in_uptrend[i] = False
        else:
            in_uptrend[i] = in_uptrend[i-1]

            if in_uptrend[i] and lowerband[i] < lowerband[i-1]:
                lowerband[i] = lowerband[i-1]

            if not in_uptrend[i] and upperband[i] > upperband[i-1]:
                upperband[i] = upperband[i-1]

    last_index = len(Close) - 1

    if in_uptrend[last_index]:
        return 1
    elif not in_uptrend[last_index]:
        return -1
    else:
        return 0