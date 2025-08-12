import numpy as np


def GetBahaiReversal(npArr, p=18, pp=8):
    sig_array = np.zeros(len(npArr))  # Initialize signature array with zeros
    h = npArr[:, 1]
    l = npArr[:, 2]
    for i in range(p+pp+1, len(npArr)):
        last_p_highs = h[i-p:i+1]
        last_pp_highs = h[i-p-pp:i+1-pp]
        last_p_lows = l[i-p:i+1]
        last_pp_lows = l[i-p-pp:i+1-pp]
        
        if np.all(last_p_highs > last_pp_highs):
            sig_array[i] = -1  # Highs are higher
        elif np.all(last_p_lows < last_pp_lows):
            sig_array[i] = 1  # Lows are lower
    return sig_array