import numpy as np
from scipy.signal import argrelextrema

def find_extrema(closeArr, WINDOW=10):
    min_indices = argrelextrema(closeArr, np.less_equal, order=WINDOW)[0]
    max_indices = argrelextrema(closeArr, np.greater_equal, order=WINDOW)[0]
    
    min_values = np.zeros_like(closeArr)
    max_values = np.zeros_like(closeArr)
    
    min_values[min_indices] = closeArr[min_indices]
    max_values[max_indices] = closeArr[max_indices]
    
    return min_values, max_values