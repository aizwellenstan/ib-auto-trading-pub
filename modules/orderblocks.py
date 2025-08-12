import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Function to calculate Average True Range (ATR)
def calculate_atr(data, period=14):
    high_low = data[:, 1] - data[:, 2]  # High - Low
    high_prev_close = np.abs(data[:, 1] - np.roll(data[:, 3], 1))  # High - Previous Close
    low_prev_close = np.abs(data[:, 2] - np.roll(data[:, 3], 1))  # Low - Previous Close

    tr = np.maximum(high_low, np.maximum(high_prev_close, low_prev_close))
    atr = np.convolve(tr, np.ones(period)/period, mode='valid')
    return atr

# Function to calculate Cumulative Mean Range
def calculate_cmean_range(data):
    mean_range = np.mean(data[:, 1] - data[:, 2])
    return np.full(data.shape[0], mean_range)

# Function to find Order Blocks
def find_order_blocks(data, atr=None, atr_threshold=1.5, cmean_threshold=1.5):
    bull_ob_levels = []
    bear_ob_levels = []

    # Determine the threshold based on the provided indicators
    if atr is not None and len(atr) > 0:
        ob_threshold = atr[-1] * atr_threshold
    else:
        raise ValueError("Either ATR or Cumulative Mean Range must be provided and calculated")

    for i in range(1, data.shape[0]):
        if (data[i, 1] - data[i, 2]) < ob_threshold:
            if data[i, 3] > data[i, 0]:  # Bullish Order Block
                bull_ob_levels.append(
                    [i, data[i, 1], data[i, 2]]
                )
            else:  # Bearish Order Block
                bear_ob_levels.append(
                    [i, data[i, 1], data[i, 2]]
                )
    
    return bull_ob_levels, bear_ob_levels


def GetOrderBlocks(data):
    # Calculate indicators
    atr = calculate_atr(data, period=14) if data.shape[0] >= 14 else None

    # Find and plot order blocks
    bull_ob_levels, bear_ob_levels = find_order_blocks(data, atr=atr)
    return bull_ob_levels, bear_ob_levels
