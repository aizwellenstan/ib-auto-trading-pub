import numpy as np

def MfiArr(npArr, period=14):
    """
    Calculate the Money Flow Index (MFI).
    
    Parameters:
    npArr (np.ndarray): A 2D array with columns [Open, High, Low, Close, Volume].
    period (int): The number of periods to use in the calculation (default is 14).
    
    Returns:
    np.ndarray: The Money Flow Index for each period.
    """
    # Extract columns
    high = npArr[:, 1]
    low = npArr[:, 2]
    close = npArr[:, 3]
    volume = npArr[:, 4]
    
    # Calculate Typical Price (TP)
    tp = (high + low + close) / 3
    
    # Calculate Money Flow (MF)
    mf = tp * volume
    
    # Initialize PMF and NMF arrays
    pmf = np.zeros_like(mf)
    nmf = np.zeros_like(mf)
    
    # Determine Positive and Negative Money Flows
    for i in range(1, len(tp)):
        if tp[i] > tp[i - 1]:
            pmf[i] = mf[i]
        elif tp[i] < tp[i - 1]:
            nmf[i] = mf[i]
    
    # Calculate MFR (Money Flow Ratio)
    mfr = np.convolve(pmf, np.ones(period), mode='valid') / np.convolve(nmf, np.ones(period), mode='valid')
    
    # Calculate MFI
    mfi = 100 - (100 / (1 + mfr))
    
    # Fill the start of the result with NaNs to align with the original data length
    mfi = np.concatenate([np.full(period - 1, np.nan), mfi])
    
    return mfi