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
def find_order_blocks(data, atr=None, cmean_range=None, atr_threshold=1.5, cmean_threshold=1.5):
    bull_ob_levels = []
    bear_ob_levels = []
    
    if atr is None and cmean_range is not None:
        ob_threshold = cmean_range * cmean_threshold
    elif atr is not None:
        ob_threshold = atr[-1] * atr_threshold
    else:
        raise ValueError("Either ATR or Cumulative Mean Range must be provided")

    for i in range(1, data.shape[0]):
        if (data[i, 1] - data[i, 2]) < ob_threshold:
            if data[i, 3] > data[i, 0]:
                bull_ob_levels.append({
                    'Index': i,
                    'Top': data[i, 1],
                    'Bottom': data[i, 2]
                })
            else:
                bear_ob_levels.append({
                    'Index': i,
                    'Top': data[i, 1],
                    'Bottom': data[i, 2]
                })
    
    return bull_ob_levels, bear_ob_levels

# Function to plot Order Blocks
def plot_order_blocks(data, bull_ob_levels, bear_ob_levels, bull_ob_color='blue', bear_ob_color='red'):
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.plot(data[:, 0], data[:, 3], label='Close Price', color='black')
    
    # Plot bullish order blocks
    for ob in bull_ob_levels:
        rect = patches.FancyBboxPatch(
            (ob['Index'], ob['Bottom']),
            1, ob['Top'] - ob['Bottom'],
            boxstyle="round,pad=0.1", edgecolor=bull_ob_color, facecolor=bull_ob_color, alpha=0.5
        )
        ax.add_patch(rect)
    
    # Plot bearish order blocks
    for ob in bear_ob_levels:
        rect = patches.FancyBboxPatch(
            (ob['Index'], ob['Top']),
            1, ob['Bottom'] - ob['Top'],
            boxstyle="round,pad=0.1", edgecolor=bear_ob_color, facecolor=bear_ob_color, alpha=0.5
        )
        ax.add_patch(rect)
    
    ax.set_xlabel('Index')
    ax.set_ylabel('Price')
    ax.legend()
    plt.show()

# Example data (numpy array)
# Format: [Open, High, Low, Close]
data = np.array([
    [100, 105, 95, 102],
    [102, 108, 100, 106],
    [106, 110, 104, 108],
    # Add more rows as needed
])

# Calculate indicators
atr = calculate_atr(data, period=14)
cmean_range = calculate_cmean_range(data)

# Find and plot order blocks
bull_ob_levels, bear_ob_levels = find_order_blocks(data, atr=atr)
plot_order_blocks(data, bull_ob_levels, bear_ob_levels, bull_ob_color='blue', bear_ob_color='red')
