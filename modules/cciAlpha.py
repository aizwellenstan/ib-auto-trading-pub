import numpy as np

def CciAlpha(npArr):
    tp = (npArr[:,1] + npArr[:,2] + npArr[:,3]) / 3
    n = 64
    sma = np.convolve(tp, np.ones(n,)/n, mode='valid')  # Simple Moving Average
    md = np.mean(np.abs(tp - sma[:, np.newaxis]), axis=1)  # Mean Deviation
    cci = (tp - sma) / (0.015 * md)

    mean = np.convolve(cci, np.ones(10,)/10, mode='valid')  # 10-period Mean
    std = np.std(cci, ddof=1)  # 10-period Standard Deviation
    
    conditions = np.abs((cci - mean[:, np.newaxis]) / std) > 1.2
    
    return conditions