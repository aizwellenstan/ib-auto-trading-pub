import numpy as np

# Define a function for linear decay weighted sum
def ts_decay_linear(values, decay_rate):
    weights = np.arange(len(values), 0, -1) * decay_rate
    weighted_sum = np.convolve(values, weights, mode='valid') / np.sum(weights)
    return np.pad(weighted_sum, (len(values) - len(weighted_sum), 0), mode='constant', constant_values=np.nan)

def Alpha3(npArr):
    close_prices = npArr[:, 3]  # Assuming 'close' is the 4th column
    rel_days_since_max = np.zeros_like(close_prices)
    for i in range(29, len(close_prices)):
        rel_days_since_max[i] = np.argmax(close_prices[i-29:i+1])

    # Calculate 'decline_pct'
    volume = npArr[:, 4]  # Assuming 'volume' is the 5th column
    decline_pct = (volume * close_prices - close_prices) / close_prices

    # Calculate 'a'
    rel_days_max_values = rel_days_since_max
    decay_weights = np.minimum(ts_decay_linear(rel_days_max_values, 1), 0.15)
    a = decline_pct / decay_weights

    # Backfill missing values in 'a' up to 64 periods
    a = np.nan_to_num(a, nan=np.nanmedian(a))
    a_filled = np.zeros_like(a)
    for i in range(len(a)):
        if np.isnan(a[i]):
            a_filled[i] = a_filled[i - 1] if i > 0 else 0
        else:
            a_filled[i] = a[i]

    # Winsorize 'a' to remove outliers beyond 4 standard deviations
    a_winsorized = np.clip(a_filled, np.percentile(a_filled, 0.1), np.percentile(a_filled, 99.9))

    return a_winsorized